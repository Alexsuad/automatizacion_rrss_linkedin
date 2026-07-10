import os
import json
import pytest
import linkedin_content_system.publishers.localdraft as localdraft_module
from pydantic import ValidationError
from linkedin_content_system.contracts import (
    SalidaLocalDraft, PostCandidato, DiagnosticoEditorial, AprobacionHumana, EstadoAprobacion,
    EstadoRevision, NivelRiesgoGenerico, ModoPublicacion, AdaptadorActivo, EstadoSalidaLocal,
    BloqueoCritico, TipoBloqueoCritico
)
from linkedin_content_system.contracts.salida import TipoAprobacion
from linkedin_content_system.contracts.trazabilidad import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
    HallazgoTrazabilidad,
    TipoHallazgoTrazabilidad,
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )


@pytest.fixture
def diagnostico_trazabilidad_pass():
    return DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)


@pytest.fixture
def diagnostico_trazabilidad_warn():
    return DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.WARN,
        hallazgos=[
            HallazgoTrazabilidad(
                tipo=TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
                fragmento_post="Quizá",
                descripcion="Inferencia débil",
                bloqueante=False,
            )
        ],
        resumen="Solo hay una inferencia débil.",
    )


@pytest.fixture
def diagnostico_trazabilidad_fail():
    return DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.FAIL,
        hallazgos=[
            HallazgoTrazabilidad(
                tipo=TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA,
                fragmento_post="42%",
                descripcion="La cifra no está soportada.",
                bloqueante=True,
            )
        ],
        resumen="Se detectó una cifra no soportada.",
    )

def _trazabilidad_pass():
    return DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)

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

def test_localdraft_rechaza_sobrescritura_silenciosa(tmp_path, salida_valida):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))

    publisher.guardar(salida_valida, id_entrada="102_dup")
    post_original = (tmp_path / "localdraft_102_dup" / "post.md").read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="ya existe"):
        publisher.guardar(salida_valida, id_entrada="102_dup")

    assert (tmp_path / "localdraft_102_dup" / "post.md").read_text(encoding="utf-8") == post_original


def test_localdraft_marca_mock_como_no_publicable(tmp_path, diagnostico_pass, aprobacion_aprobada):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida_mock = SalidaLocalDraft(
        post=PostCandidato(
            texto=(
                "[BORRADOR SIMULADO DE POST]\n"
                "Contexto de sistema recibido: no\n"
                "Fragmento de origen: Automatizacion offline\n"
                "--- Contenido generado determinista para LinkedIn ---"
            )
        ),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    publisher.guardar(salida_mock, id_entrada="mock_001")

    salida_file = tmp_path / "localdraft_mock_001" / "salida_v1.json"
    with open(salida_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["estado_publicabilidad"] == "no_publicable"

def test_localdraft_clock_determinista(tmp_path, salida_valida):
    fake_time = "2026-07-04T12:00:00Z"
    publisher = LocalDraftPublisher(base_dir=str(tmp_path), clock=lambda: fake_time)
    manifest = publisher.guardar(salida_valida, id_entrada="103")
    
    assert manifest.timestamp == fake_time


def test_localdraft_limpia_directorio_temporal_si_falla_la_escritura(tmp_path, salida_valida, monkeypatch):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    original_dump = localdraft_module.json.dump
    llamadas = {"count": 0}

    def _failing_dump(data, handle, *args, **kwargs):
        llamadas["count"] += 1
        if llamadas["count"] == 2:
            raise OSError("fallo simulado de escritura")
        return original_dump(data, handle, *args, **kwargs)

    monkeypatch.setattr(localdraft_module.json, "dump", _failing_dump)

    with pytest.raises(OSError, match="fallo simulado"):
        publisher.guardar(salida_valida, id_entrada="atomic_fail")

    assert not (tmp_path / "localdraft_atomic_fail").exists()
    assert not [path for path in tmp_path.iterdir() if path.name.startswith(".localdraft_atomic_fail_")]

def test_localdraft_bloquea_si_aprobacion_pendiente(tmp_path, diagnostico_pass):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida_pendiente = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=_trazabilidad_pass(),
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
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
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="rutas locales"):
        publisher.guardar(salida_ruta, id_entrada="107")

def test_localdraft_bloquea_si_falta_diagnostico_trazabilidad(
    tmp_path,
    diagnostico_pass,
    aprobacion_aprobada,
):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Este es un post seguro y limpio de prueba."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=None,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    with pytest.raises(ValueError, match="diagnostico_trazabilidad"):
        publisher.guardar(salida, id_entrada="107_missing_trace")

def test_localdraft_persiste_diagnostico_trazabilidad_pass(
    tmp_path,
    diagnostico_pass,
    aprobacion_aprobada,
    diagnostico_trazabilidad_pass,
):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Este es un post seguro y limpio de prueba."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=diagnostico_trazabilidad_pass,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    manifest = publisher.guardar(salida, id_entrada="108")

    assert (tmp_path / "localdraft_108" / "salida_v1.json").exists()
    assert manifest.id_entrada == "108"


def test_localdraft_persiste_trazabilidad_warn_con_aprobacion_reforzada(
    tmp_path,
    diagnostico_trazabilidad_warn,
):
    diagnostico_warn = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.WARN,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.WARN,
    )
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños."),
        diagnostico_editorial=diagnostico_warn,
        diagnostico_trazabilidad=diagnostico_trazabilidad_warn,
        aprobacion_humana=AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex",
            fecha_aprobacion="2026-07-04T11:00:00Z",
            tipo_aprobacion=TipoAprobacion.REFORZADA,
            revision_reforzada_requerida=True,
            motivo_revision_reforzada="Se aceptó la inferencia débil.",
        ),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    manifest = publisher.guardar(salida, id_entrada="112")

    assert (tmp_path / "localdraft_112" / "manifest.json").exists()
    assert manifest.id_entrada == "112"


def test_localdraft_bloquea_si_trazabilidad_fail_y_no_persiste(
    tmp_path,
    diagnostico_pass,
    aprobacion_aprobada,
    diagnostico_trazabilidad_fail,
):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Aumentamos 42% en un mes."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=diagnostico_trazabilidad_fail,
        aprobacion_humana=aprobacion_aprobada,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    with pytest.raises(ValueError, match="trazabilidad"):
        publisher.guardar(salida, id_entrada="109")

    assert not (tmp_path / "localdraft_109").exists()


def test_localdraft_warn_trazabilidad_requiere_aprobacion_reforzada_y_persiste(
    tmp_path,
    diagnostico_pass,
    diagnostico_trazabilidad_warn,
):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))
    salida_simple = SalidaLocalDraft(
        post=PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=diagnostico_trazabilidad_warn,
        aprobacion_humana=AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex",
            fecha_aprobacion="2026-07-04T11:00:00Z",
        ),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    with pytest.raises(ValueError, match="trazabilidad"):
        publisher.guardar(salida_simple, id_entrada="110")

    salida_reforzada = SalidaLocalDraft(
        post=PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños."),
        diagnostico_editorial=diagnostico_pass,
        diagnostico_trazabilidad=diagnostico_trazabilidad_warn,
        aprobacion_humana=AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex",
            fecha_aprobacion="2026-07-04T11:00:00Z",
            tipo_aprobacion=TipoAprobacion.REFORZADA,
            revision_reforzada_requerida=True,
            motivo_revision_reforzada="Se aceptó la inferencia débil.",
        ),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
    )

    manifest = publisher.guardar(salida_reforzada, id_entrada="111")

    assert (tmp_path / "localdraft_111" / "manifest.json").exists()
    assert manifest.id_entrada == "111"

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
