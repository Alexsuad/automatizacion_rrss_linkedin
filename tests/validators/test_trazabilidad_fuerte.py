import pytest

from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IdeaCentral,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    PostCandidato,
    TipoEntrada,
)
from linkedin_content_system.contracts.trazabilidad import (
    EstadoTrazabilidad,
    TipoHallazgoTrazabilidad,
)
from linkedin_content_system.validators.trazabilidad import (
    resolver_estado_trazabilidad,
    validar_trazabilidad_fuerte,
)


@pytest.fixture
def entrada_trazable():
    return EntradaContenido(
        id_entrada="trz_001",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Contamos una mejora del 15% con datos internos ya explicados.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="profesionales",
            idea_central="Mejora del 15% con datos internos ya explicados.",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_trazable"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"contexto_permitido": ["datos internos ya explicados"]},
    )


def test_validar_trazabilidad_fuerte_pass_completamente_soportado(entrada_trazable):
    idea = IdeaCentral(
        idea_central="Mejora del 15% con datos internos ya explicados.",
        resumen_operativo="Resumen alineado con la entrada.",
        puntos_de_soporte=["Contamos una mejora del 15% con datos internos ya explicados."],
        limites_de_inferencia=["No inventar cifras nuevas."],
    )
    post = PostCandidato(texto="Contamos una mejora del 15% con datos internos ya explicados.")

    diagnostico = validar_trazabilidad_fuerte(entrada_trazable, idea, post)

    assert diagnostico.estado == EstadoTrazabilidad.PASS
    assert diagnostico.hallazgos == []


def test_validar_trazabilidad_fuerte_warn_por_inferencia_debil(entrada_trazable):
    idea = IdeaCentral(
        idea_central="Mejora útil para equipos pequeños.",
        resumen_operativo="Resumen con una hipótesis prudente.",
        puntos_de_soporte=["Mejora útil para equipos pequeños."],
        limites_de_inferencia=["No elevar hipótesis a hechos."],
    )
    post = PostCandidato(texto="Quizá sea una mejora útil para equipos pequeños.")

    diagnostico = validar_trazabilidad_fuerte(entrada_trazable, idea, post)

    assert diagnostico.estado == EstadoTrazabilidad.WARN
    assert len(diagnostico.hallazgos) == 1
    assert diagnostico.hallazgos[0].tipo == TipoHallazgoTrazabilidad.INFERENCIA_DEBIL
    assert diagnostico.hallazgos[0].bloqueante is False


@pytest.mark.parametrize(
    "texto_post, tipo_hallazgo",
    [
        ("Aumentamos 42% en un mes.", TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA),
        ("Somos líderes certificados del sector.", TipoHallazgoTrazabilidad.AUTORIDAD_FINGIDA),
        ("Me pasó con un cliente real.", TipoHallazgoTrazabilidad.ANECDOTA_INVENTADA),
        ("Garantiza resultados sin riesgo.", TipoHallazgoTrazabilidad.PROMESA_EXCESIVA),
        ("Los estudios demuestran que el mercado confirma todo.", TipoHallazgoTrazabilidad.CLAIM_SIN_FUENTE),
    ],
)
def test_validar_trazabilidad_fuerte_fail_por_patron_sensible(
    entrada_trazable,
    texto_post,
    tipo_hallazgo,
):
    idea = IdeaCentral(
        idea_central="Idea base sin la afirmación sensible.",
        resumen_operativo="Resumen base sin la afirmación sensible.",
        puntos_de_soporte=["Idea base sin la afirmación sensible."],
        limites_de_inferencia=["No inventar soporte."],
    )
    post = PostCandidato(texto=texto_post)

    diagnostico = validar_trazabilidad_fuerte(entrada_trazable, idea, post)

    assert diagnostico.estado == EstadoTrazabilidad.FAIL
    assert any(h.tipo == tipo_hallazgo for h in diagnostico.hallazgos)


def test_validar_trazabilidad_fuerte_fail_por_contradiccion_con_contexto(entrada_trazable):
    idea = IdeaCentral(
        idea_central="Mejora del 15% con datos internos ya explicados.",
        resumen_operativo="Resumen alineado con la entrada.",
        puntos_de_soporte=["Contamos una mejora del 15% con datos internos ya explicados."],
        limites_de_inferencia=["No inventar cifras nuevas."],
    )
    post = PostCandidato(texto="Contamos una mejora del 15% con datos internos ya explicados.")

    diagnostico = validar_trazabilidad_fuerte(
        entrada_trazable,
        idea,
        post,
        contexto_permitido=["sin cifras", "sin anécdotas"],
    )

    assert diagnostico.estado == EstadoTrazabilidad.FAIL
    assert any(h.tipo == TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO for h in diagnostico.hallazgos)


def test_resolver_estado_trazabilidad_prioriza_fail_sobre_warn():
    from linkedin_content_system.contracts.trazabilidad import HallazgoTrazabilidad

    hallazgos = [
        HallazgoTrazabilidad(
            tipo=TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
            fragmento_post="Quizá",
            descripcion="Inferencia débil",
            bloqueante=False,
        ),
        HallazgoTrazabilidad(
            tipo=TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA,
            fragmento_post="42%",
            descripcion="Cifra no soportada",
            bloqueante=True,
        ),
    ]

    assert resolver_estado_trazabilidad(hallazgos) == EstadoTrazabilidad.FAIL


def test_resolver_estado_trazabilidad_sin_hallazgos_es_pass():
    assert resolver_estado_trazabilidad([]) == EstadoTrazabilidad.PASS
