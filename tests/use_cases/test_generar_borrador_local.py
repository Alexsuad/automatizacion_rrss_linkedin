import os
import json
import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts import (
    EntradaContenido, IntencionEditorial, PerfilNarrativoReferencia, EstadoIntencionEditorial, TipoEntrada, EstadoPrivacidad,
    DiagnosticoEditorial, EstadoRevision, NivelRiesgoGenerico,
    PostCandidato, AprobacionHumana, EstadoAprobacion, SalidaLocalDraft
)
from linkedin_content_system.use_cases import generar_borrador_local_desde_simulacion
from linkedin_content_system.publishers import PublicationPublisherPort

@pytest.fixture
def entrada_valida():
    return EntradaContenido(
        id_entrada="in_200",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Texto base válido de prueba para caso de uso.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="profesionales",
            idea_central="Automatización segura"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_usecase"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"fecha_objetivo_sugerida": "2026-07-15T08:00:00Z"}
    )

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
        aprobado_por="Alex Revisor",
        fecha_aprobacion="2026-07-04T11:00:00Z"
    )

def test_caso_uso_exitoso(tmp_path, entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Este es un post seguro y limpio de prueba para el caso de uso.")
    fake_time = "2026-07-04T12:00:00Z"
    
    manifest = generar_borrador_local_desde_simulacion(
        entrada=entrada_valida,
        post=post,
        diagnostico=diagnostico_pass,
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
        clock=lambda: fake_time
    )

    dir_path = tmp_path / "localdraft_in_200"
    assert dir_path.exists()
    assert dir_path.is_dir()

    post_file = dir_path / "post.md"
    diag_file = dir_path / "diagnostico.json"
    manifest_file = dir_path / "manifest.json"

    assert post_file.exists()
    assert diag_file.exists()
    assert manifest_file.exists()

    with open(post_file, "r", encoding="utf-8") as f:
        assert f.read() == post.texto

    assert manifest.timestamp == fake_time
    assert manifest.id_entrada == "in_200"

def test_caso_uso_coincidencia_manifest(tmp_path, entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Post limpio")
    manifest_obj = generar_borrador_local_desde_simulacion(
        entrada=entrada_valida,
        post=post,
        diagnostico=diagnostico_pass,
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path)
    )

    manifest_file = tmp_path / "localdraft_in_200" / "manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert manifest_obj.id_evidencia == data["id_evidencia"]
    assert manifest_obj.timestamp == data["timestamp"]

def test_caso_uso_bloquea_si_aprobacion_pendiente(tmp_path, entrada_valida, diagnostico_pass):
    post = PostCandidato(texto="Post limpio")
    aprob_pendiente = AprobacionHumana(estado=EstadoAprobacion.PENDIENTE)
    
    with pytest.raises(ValueError, match="Publicación denegada"):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_valida,
            post=post,
            diagnostico=diagnostico_pass,
            aprobacion=aprob_pendiente,
            base_dir=str(tmp_path)
        )

def test_caso_uso_bloquea_si_post_inseguro(tmp_path, entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post_pii = PostCandidato(texto="Mi correo es test@correo.com")
    with pytest.raises(ValueError, match="correo electrónico"):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_valida,
            post=post_pii,
            diagnostico=diagnostico_pass,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path)
        )

    post_secreto = PostCandidato(texto="Mi token sk-projabcdefghijklmnopqrstuvwx")
    with pytest.raises(ValueError, match="secretos o credenciales"):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_valida,
            post=post_secreto,
            diagnostico=diagnostico_pass,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path)
        )

    post_ruta = PostCandidato(texto="Ver archivo en file:///home/user/test")
    with pytest.raises(ValueError, match="rutas locales"):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_valida,
            post=post_ruta,
            diagnostico=diagnostico_pass,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path)
        )

def test_caso_uso_bloquea_path_traversal(tmp_path, diagnostico_pass, aprobacion_aprobada):
    entrada_bad_id = EntradaContenido(
        id_entrada="in_200/../traversal",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Texto base",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            idea_central="Idea"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_usecase"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={}
    )
    post = PostCandidato(texto="Post limpio")
    with pytest.raises(ValueError, match="contiene caracteres prohibidos"):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_bad_id,
            post=post,
            diagnostico=diagnostico_pass,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path)
        )

def test_caso_uso_no_escribe_fuera_de_base_dir(tmp_path, diagnostico_pass, aprobacion_aprobada):
    entrada_bad_id = EntradaContenido(
        id_entrada="..",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Texto base",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            idea_central="Idea"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_usecase"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={}
    )
    post = PostCandidato(texto="Post limpio")
    with pytest.raises(ValueError):
        generar_borrador_local_desde_simulacion(
            entrada=entrada_bad_id,
            post=post,
            diagnostico=diagnostico_pass,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path)
        )


def test_caso_uso_admite_publisher_inyectado(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    class PublisherSpy(PublicationPublisherPort):
        def __init__(self):
            self.salida = None
            self.id_entrada = None

        def guardar(self, salida, id_entrada):
            self.salida = salida
            self.id_entrada = id_entrada
            return {"id_entrada": id_entrada}

    publisher = PublisherSpy()
    post = PostCandidato(texto="Post limpio")

    manifest = generar_borrador_local_desde_simulacion(
        entrada=entrada_valida,
        post=post,
        diagnostico=diagnostico_pass,
        aprobacion=aprobacion_aprobada,
        publisher=publisher,
    )

    assert manifest == {"id_entrada": "in_200"}
    assert publisher.id_entrada == "in_200"
    assert publisher.salida.post.texto == "Post limpio"
