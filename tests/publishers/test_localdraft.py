import os
import json
import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts import (
    SalidaLocalDraft, PostCandidato, DiagnosticoEditorial, AprobacionHumana, EstadoAprobacion,
    EstadoRevision, NivelRiesgoGenerico, ModoPublicacion, AdaptadorActivo, EstadoSalidaLocal,
    BloqueoCritico, TipoBloqueoCritico
)
from linkedin_content_system.publishers import LocalDraftPublisher

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
        estado_revision=EstadoRevision.PASS
    )

@pytest.fixture
def aprobacion_aprobada():
    return AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T11:00:00Z"
    )

@pytest.fixture
def salida_valida(diagnostico_pass, aprobacion_aprobada):
    return SalidaLocalDraft(
        post=PostCandidato(texto="Este es un post seguro y limpio de prueba."),
        diagnostico_editorial=diagnostico_pass,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )

def test_localdraft_crea_directorio_y_archivos(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    manifest = publisher.guardar(salida_valida, id_entrada="101")

    # Verificar creación de directorio
    dir_path = tmp_path / "localdraft_101"
    assert dir_path.exists()
    assert dir_path.is_dir()

    # Verificar archivos físicos
    post_file = dir_path / "post.md"
    diag_file = dir_path / "diagnostico.json"
    salida_file = dir_path / "salida_v1.json"
    manifest_file = dir_path / "manifest.json"

    assert post_file.exists()
    assert diag_file.exists()
    assert salida_file.exists()
    assert manifest_file.exists()

    # Verificar contenido de post.md
    with open(post_file, "r", encoding="utf-8") as f:
        assert f.read() == salida_valida.post.texto

    # Verificar manifest.json cargado desde disco
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["id_entrada"] == "101"
        assert data["id_evidencia"] == "ev_101"
        assert f"localdraft_101/salida_v1.json" in data["archivos_generados"]


def test_localdraft_coincidencia_manifest(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    manifest_obj = publisher.guardar(salida_valida, id_entrada="102")

    manifest_file = tmp_path / "localdraft_102" / "manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert manifest_obj.id_evidencia == data["id_evidencia"]
    assert manifest_obj.id_entrada == data["id_entrada"]
    assert manifest_obj.archivos_generados == data["archivos_generados"]
    assert manifest_obj.estado == data["estado"]
    assert manifest_obj.timestamp == data["timestamp"]

def test_localdraft_clock_determinista(tmp_path, salida_valida):
    fake_time = "2026-07-04T12:00:00Z"
    publisher = LocalDraftPublisher(base_dir=str(tmp_path), clock=lambda: fake_time)
    manifest = publisher.guardar(salida_valida, id_entrada="103")
    
    assert manifest.timestamp == fake_time

def test_localdraft_bloquea_si_aprobacion_pendiente(tmp_path, diagnostico_pass):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida_pendiente = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diagnostico_pass,
        aprobacion_humana=AprobacionHumana(estado=EstadoAprobacion.PENDIENTE),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    
    with pytest.raises(ValueError, match="Publicación denegada"):
        publisher.guardar(salida_pendiente, id_entrada="104")

    assert not (tmp_path / "localdraft_104").exists()

def test_localdraft_bloquea_si_requiere_revision_y_no_persiste(tmp_path, aprobacion_aprobada):
    diagnostico_warn = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.WARN,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.WARN
    )
    salida_warn_simple = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diagnostico_warn,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))

    with pytest.raises(ValueError, match="aprobación reforzada"):
        publisher.guardar(salida_warn_simple, id_entrada="104_warn")

    assert not (tmp_path / "localdraft_104_warn").exists()

def test_localdraft_bloquea_si_hay_bloqueos_criticos_y_no_persiste(tmp_path, aprobacion_aprobada):
    diagnostico_bloqueado = DiagnosticoEditorial(
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
            BloqueoCritico(tipo=TipoBloqueoCritico.PII, descripcion="Correo detectado")
        ]
    )
    salida_bloqueada = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diagnostico_bloqueado,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))

    with pytest.raises(ValueError, match="bloqueos críticos"):
        publisher.guardar(salida_bloqueada, id_entrada="104_blocks")

    assert not (tmp_path / "localdraft_104_blocks").exists()

def test_localdraft_bloquea_si_post_inseguro(tmp_path, diagnostico_pass, aprobacion_aprobada):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    
    # 1. PII
    salida_pii = SalidaLocalDraft(
        post=PostCandidato(texto="Mi correo es test@correo.com"),
        diagnostico_editorial=diagnostico_pass,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="correo electrónico"):
        publisher.guardar(salida_pii, id_entrada="105")

    # 2. Secreto
    salida_secreto = SalidaLocalDraft(
        post=PostCandidato(texto="Mi token sk-projabcdefghijklmnopqrstuvwx"),
        diagnostico_editorial=diagnostico_pass,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="secretos o credenciales"):
        publisher.guardar(salida_secreto, id_entrada="106")

    # 3. Ruta absoluta
    salida_ruta = SalidaLocalDraft(
        post=PostCandidato(texto="Ver archivo en file:///home/user/test"),
        diagnostico_editorial=diagnostico_pass,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="rutas locales"):
        publisher.guardar(salida_ruta, id_entrada="107")

def test_localdraft_bloquea_path_traversal(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    
    with pytest.raises(ValueError, match="contiene caracteres prohibidos"):
        publisher.guardar(salida_valida, id_entrada="101/../traversal")
        
    with pytest.raises(ValueError, match="contiene caracteres prohibidos"):
        publisher.guardar(salida_valida, id_entrada="..\\traversal")

    with pytest.raises(ValueError, match="contiene caracteres prohibidos"):
        publisher.guardar(salida_valida, id_entrada="C:traversal")

def test_localdraft_no_escribe_fuera_de_base_dir(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    with pytest.raises(ValueError):
        publisher.guardar(salida_valida, id_entrada="..")

def test_localdraft_bloquea_id_entrada_vacio(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    with pytest.raises(ValueError, match="no puede estar vacío"):
        publisher.guardar(salida_valida, id_entrada="")
    with pytest.raises(ValueError, match="no puede estar vacío"):
        publisher.guardar(salida_valida, id_entrada="   ")
