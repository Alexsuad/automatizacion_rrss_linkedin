import json
import socket

import pytest

from linkedin_content_system.contracts import (
    AprobacionHumana,
    BloqueoCritico,
    DiagnosticoEditorial,
    EstadoAprobacion,
    EstadoEvidencia,
    EstadoPublicabilidad,
    EstadoRevision,
    EstadoSalidaLocal,
    NivelRiesgoGenerico,
    PostCandidato,
    SalidaLocalDraft,
    TipoBloqueoCritico,
    ModoPublicacion,
    AdaptadorActivo,
)
from linkedin_content_system.contracts.trazabilidad import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
    HallazgoTrazabilidad,
    TipoHallazgoTrazabilidad,
)
from linkedin_content_system.publishers import ExternalDryRunPublisher, PublicationPublisherPort


@pytest.fixture
def diagnostico_pass():
    return DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )


@pytest.fixture
def aprobacion_aprobada():
    return AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-08T11:00:00Z",
    )


@pytest.fixture
def salida_valida(diagnostico_pass, aprobacion_aprobada):
    return SalidaLocalDraft(
        post=PostCandidato(texto="Contenido listo para preparacion externa en dry_run."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        estado_publicabilidad=EstadoPublicabilidad.PUBLICABLE,
    )


def _trazabilidad_pass():
    return DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)


def test_external_dryrunpublisher_cumple_puerto_publicacion(tmp_path):
    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    assert isinstance(publisher, PublicationPublisherPort)
    assert hasattr(publisher, "guardar")


def test_external_dryrun_crea_evidencia_local(tmp_path, salida_valida):
    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path), clock=lambda: "2026-07-08T12:00:00Z")

    manifest = publisher.guardar(salida_valida, id_entrada="201")

    target_dir = tmp_path / "external_dryrun_201"
    payload_file = target_dir / "publicacion_simulada.json"
    manifest_file = target_dir / "manifest.json"

    assert target_dir.exists()
    assert payload_file.exists()
    assert manifest_file.exists()
    assert manifest.id_entrada == "201"
    assert manifest.id_evidencia == "ev_external_201"
    assert manifest.timestamp == "2026-07-08T12:00:00Z"

    with open(payload_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["modo"] == "dry_run"
    assert data["proveedor"] == "simulated_external"
    assert data["canal_destino"] == "linkedin"
    assert data["no_publicado_realmente"] is True
    assert data["id_externo_simulado"] == "dryrun-201"
    assert data["estado_publicabilidad_origen"] == "publicable"
    assert data["salida_origen"]["estado"] == "borrador_local"


def test_external_dryrun_rechaza_sobrescritura_silenciosa(tmp_path, salida_valida):
    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    publisher.guardar(salida_valida, id_entrada="202")

    with pytest.raises(ValueError, match="ya existe"):
        publisher.guardar(salida_valida, id_entrada="202")


def test_external_dryrun_rechaza_id_vacio_y_traversal(tmp_path, salida_valida):
    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    with pytest.raises(ValueError, match="no puede estar vacío"):
        publisher.guardar(salida_valida, id_entrada="")

    with pytest.raises(ValueError, match="contiene caracteres prohibidos"):
        publisher.guardar(salida_valida, id_entrada="../traversal")


def test_external_dryrun_no_usa_red(tmp_path, salida_valida, monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("No se debe usar red en dry-run")

    monkeypatch.setattr(socket, "create_connection", _fail)

    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))
    manifest = publisher.guardar(salida_valida, id_entrada="203")

    assert manifest.id_entrada == "203"


def test_external_dryrun_reutiliza_validaciones_de_seguridad(tmp_path, aprobacion_aprobada):
    diagnostico = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    trazabilidad = DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)
    salida_insegura = SalidaLocalDraft(
        post=PostCandidato(texto="Mi correo es test@correo.com"),
        diagnostico_editorial=diagnostico,
        diagnostico_trazabilidad=trazabilidad,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        estado_publicabilidad=EstadoPublicabilidad.PUBLICABLE,
    )

    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    with pytest.raises(ValueError, match="correo electrónico"):
        publisher.guardar(salida_insegura, id_entrada="204")


def test_external_dryrun_bloquea_bloqueos_criticos(tmp_path, aprobacion_aprobada):
    diagnostico = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.FAIL,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.FAIL,
        bloqueos_criticos=[
            BloqueoCritico(tipo=TipoBloqueoCritico.PII, descripcion="Correo detectado"),
        ],
    )
    trazabilidad = DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)
    salida_bloqueada = SalidaLocalDraft(
        post=PostCandidato(texto="Contenido limpio"),
        diagnostico_editorial=diagnostico,
        diagnostico_trazabilidad=trazabilidad,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        estado_publicabilidad=EstadoPublicabilidad.PUBLICABLE,
    )

    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    with pytest.raises(ValueError, match="bloqueos críticos"):
        publisher.guardar(salida_bloqueada, id_entrada="205")
