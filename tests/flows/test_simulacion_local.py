import os
import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts import (
    EntradaContenido, IntencionEditorial, PerfilNarrativoReferencia, EstadoIntencionEditorial, TipoEntrada, EstadoPrivacidad,
    DiagnosticoEditorial, EstadoRevision, NivelRiesgoGenerico,
    PostCandidato, AprobacionHumana, EstadoAprobacion, SalidaLocalDraft, ManifestEvidencia
)
from linkedin_content_system.contracts.salida import EstadoPublicabilidad, TipoAprobacion
from linkedin_content_system.contracts.trazabilidad import EstadoTrazabilidad
from linkedin_content_system.flows import ensamblar_flujo_local_simulado

@pytest.fixture
def entrada_valida():
    return EntradaContenido(
        id_entrada="in_100",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Este es el texto base válido de prueba.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="profesionales",
            idea_central="Automatización segura"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_abc"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"fecha_objetivo_sugerida": "2026-07-10T10:00:00Z"}
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
        aprobado_por="Usuario Revisor",
        fecha_aprobacion="2026-07-04T10:00:00Z"
    )


@pytest.fixture
def aprobacion_reforzada():
    return AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Usuario Revisor",
        fecha_aprobacion="2026-07-04T10:00:00Z",
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        revision_reforzada_requerida=True,
        motivo_revision_reforzada="Se revisó la inferencia débil de forma explícita.",
    )

def test_flujo_simulado_exitoso(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Este es un post seguro e interesante para publicar en LinkedIn.")
    salida, manifest = ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)
    
    assert isinstance(salida, SalidaLocalDraft)
    assert isinstance(manifest, ManifestEvidencia)
    assert salida.post.texto == post.texto
    assert salida.estado_publicabilidad == EstadoPublicabilidad.PUBLICABLE
    assert salida.diagnostico_trazabilidad is not None
    assert salida.diagnostico_trazabilidad.estado == EstadoTrazabilidad.PASS
    assert manifest.id_entrada == entrada_valida.id_entrada
    assert "output/simulado/post.md" in manifest.archivos_generados

def test_flujo_bloquea_si_aprobacion_pendiente(entrada_valida, diagnostico_pass):
    post = PostCandidato(texto="Post limpio")
    aprob_pendiente = AprobacionHumana(estado=EstadoAprobacion.PENDIENTE)
    
    with pytest.raises(ValueError, match="Publicación denegada"):
        ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprob_pendiente)

def test_flujo_bloquea_si_post_contiene_email(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Contáctanos en contacto@dominio.com para saber más.")
    with pytest.raises(ValueError, match="correo electrónico"):
        ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)

def test_flujo_bloquea_si_post_contiene_secreto(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="No compartas la clave sk-projabcdefghijklmnopqrstuvwx en público.")
    with pytest.raises(ValueError, match="secretos o credenciales"):
        ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)

def test_flujo_bloquea_si_post_contiene_ruta_local(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Ver archivo en file:///home/nalex/secrets.txt")
    with pytest.raises(ValueError, match="rutas locales"):
        ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)


def test_flujo_bloquea_si_trazabilidad_fail_por_cifra_no_soportada(
    entrada_valida,
    diagnostico_pass,
    aprobacion_aprobada,
):
    post = PostCandidato(texto="Aumentamos 42% en un mes con un método propio.")

    with pytest.raises(ValueError, match="trazabilidad"):
        ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)


def test_flujo_permite_warn_con_aprobacion_reforzada(
    entrada_valida,
    diagnostico_pass,
    aprobacion_reforzada,
):
    post = PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños.")
    salida, _ = ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_reforzada)

    assert salida.diagnostico_trazabilidad is not None
    assert salida.diagnostico_trazabilidad.estado == EstadoTrazabilidad.WARN
    assert salida.estado_publicabilidad == EstadoPublicabilidad.PUBLICABLE

def test_flujo_permite_warn_editorial_y_trazabilidad_con_aprobacion_reforzada(
    entrada_valida,
    aprobacion_reforzada,
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
    post = PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños.")

    salida, _ = ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_warn, aprobacion_reforzada)

    assert salida.diagnostico_trazabilidad is not None
    assert salida.diagnostico_trazabilidad.estado == EstadoTrazabilidad.WARN
    assert salida.estado_publicabilidad == EstadoPublicabilidad.PUBLICABLE

def test_flujo_no_escribe_archivos_en_disco(entrada_valida, diagnostico_pass, aprobacion_aprobada):
    post = PostCandidato(texto="Post seguro para verificar que no se escribe en disco.")
    
    fictitious_path = "output/simulado/post.md"
    if os.path.exists(fictitious_path):
        os.remove(fictitious_path)
        
    salida, manifest = ensamblar_flujo_local_simulado(entrada_valida, post, diagnostico_pass, aprobacion_aprobada)
    
    assert not os.path.exists(fictitious_path)
    assert not os.path.exists("output/simulado/manifest.json")
