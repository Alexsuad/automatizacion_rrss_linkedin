from typing import Callable, Optional

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    BloqueoCritico,
    DiagnosticoEditorial,
    EntradaContenido,
    EstadoRevision,
    ManifestEvidencia,
    IdeaCentral,
    NivelRiesgoGenerico,
    PostCandidato,
    TipoBloqueoCritico,
    TipoEntrada,
)
from linkedin_content_system.publishers import PublicationPublisherPort
from linkedin_content_system.use_cases.diagnosticar_base_editorial import diagnosticar_base_editorial
from linkedin_content_system.use_cases.extraer_idea_central import extraer_idea_central
from linkedin_content_system.use_cases.extraer_intencion_editorial import extraer_intencion_editorial
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
    NarrativeProfileResolver,
    PerfilNarrativoRuntime,
    TextChannelStrategy,
)
from linkedin_content_system.use_cases.generar_borrador_local import generar_borrador_local_desde_simulacion
from linkedin_content_system.use_cases.generar_post_mock import generar_post_mock
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


def _normalizar_texto(texto: str) -> str:
    return " ".join((texto or "").lower().split())


def validar_entrada_generable(entrada: EntradaContenido) -> None:
    textos_a_validar = [
        entrada.texto_base,
        entrada.intencion_editorial.audiencia_objetivo,
        entrada.intencion_editorial.objetivo_del_post,
        entrada.intencion_editorial.idea_central,
        entrada.intencion_editorial.cta_intencionado,
    ]
    for texto in textos_a_validar:
        if not texto:
            continue
        validar_texto_sin_pii_basica(texto)
        validar_texto_sin_secretos_basicos(texto)
        validar_sin_rutas_locales(texto)


def _construir_diagnostico_editorial_minimo(
    entrada: EntradaContenido,
    idea_central,
    diagnostico_base,
    prompt: str,
    perfil_runtime: PerfilNarrativoRuntime,
    texto_post: str,
) -> DiagnosticoEditorial:
    bloqueos_criticos = []
    cumplimiento_ok = True

    try:
        validar_texto_sin_pii_basica(texto_post)
        validar_texto_sin_secretos_basicos(texto_post)
        validar_sin_rutas_locales(texto_post)
    except ValueError as exc:
        cumplimiento_ok = False
        bloqueos_criticos.append(
            BloqueoCritico(
                tipo=TipoBloqueoCritico.COMPLIANCE,
                descripcion=str(exc),
            )
        )

    texto_post_normalizado = _normalizar_texto(texto_post)
    idea_normalizada = _normalizar_texto(idea_central.idea_central)
    tokens_idea = [token for token in idea_normalizada.split() if len(token) > 3]

    claridad_idea = (
        EstadoRevision.PASS
        if texto_post.strip() and (not tokens_idea or any(token in texto_post_normalizado for token in tokens_idea))
        else EstadoRevision.WARN
    )
    audiencia = (
        EstadoRevision.PASS if entrada.intencion_editorial.audiencia_objetivo else EstadoRevision.WARN
    )
    hook = EstadoRevision.WARN if texto_post.strip() else EstadoRevision.FAIL
    voz_cliente = EstadoRevision.WARN if perfil_runtime.id_perfil else EstadoRevision.FAIL
    autenticidad = EstadoRevision.WARN if cumplimiento_ok else EstadoRevision.FAIL
    cta = EstadoRevision.WARN if texto_post.strip() else EstadoRevision.FAIL
    compliance = EstadoRevision.PASS if cumplimiento_ok else EstadoRevision.FAIL
    riesgo_generico = NivelRiesgoGenerico.BAJO if cumplimiento_ok else NivelRiesgoGenerico.ALTO

    if not cumplimiento_ok:
        estado_revision = EstadoRevision.FAIL
    elif any(revision == EstadoRevision.WARN for revision in (claridad_idea, audiencia)):
        estado_revision = EstadoRevision.WARN
    else:
        estado_revision = EstadoRevision.PASS

    motivo = (
        f"{diagnostico_base.resumen} "
        "Hook, voz, autenticidad y CTA quedan marcados como revisión editorial pendiente, no como PASS automático."
    )
    if diagnostico_base.estado == "WARN":
        motivo = f"{diagnostico_base.resumen} Base editorial derivada con advertencias controladas."

    recomendaciones = list(diagnostico_base.recomendaciones)
    recomendaciones.append(
        "Revisar hook, voz cliente, autenticidad y CTA con criterio humano o evaluación editorial posterior."
    )
    ajustes_recomendados = " | ".join(recomendaciones)

    return DiagnosticoEditorial(
        claridad_idea=claridad_idea,
        audiencia=audiencia,
        hook=hook,
        voz_cliente=voz_cliente,
        autenticidad=autenticidad,
        cta=cta,
        compliance=compliance,
        riesgo_generico=riesgo_generico,
        estado_revision=estado_revision,
        motivo=motivo,
        ajustes_recomendados=ajustes_recomendados,
        bloqueos_criticos=bloqueos_criticos,
    )


def generar_candidato_textual(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
) -> tuple[PostCandidato, DiagnosticoEditorial, IdeaCentral]:
    if entrada.tipo_entrada != TipoEntrada.TEXTO_MANUAL:
        raise ValueError("Este flujo solo admite entradas de texto manual.")

    validar_entrada_generable(entrada)

    idea_central = extraer_idea_central(entrada.texto_base)
    intencion_clasificada = extraer_intencion_editorial(idea_central)
    diagnostico_base = diagnosticar_base_editorial(idea_central, intencion_clasificada)

    if diagnostico_base.estado == "FAIL":
        raise ValueError("La base editorial es insuficiente para continuar el flujo textual.")

    channel_strategy_resuelta = channel_strategy or LinkedInTextChannelStrategy()
    if not channel_strategy_resuelta.supports(entrada):
        raise ValueError(
            f"Este flujo textual requiere un strategy compatible con '{channel_strategy_resuelta.canal_destino}'."
        )

    profile_resolver_resuelto = profile_resolver or FilesystemNarrativeProfileResolver()
    perfil_runtime = profile_resolver_resuelto.resolve(entrada.perfil_narrativo.id_perfil)
    request = channel_strategy_resuelta.build_request(
        entrada=entrada,
        idea_central=idea_central.idea_central,
        resumen_intencion=intencion_clasificada.resumen_intencion,
        perfil=perfil_runtime,
    )

    texto_generado = generar_post_mock(
        request.prompt,
        adapter,
        system_instruction=request.system_instruction,
    )
    post = PostCandidato(texto=texto_generado)
    diagnostico_editorial = _construir_diagnostico_editorial_minimo(
        entrada=entrada,
        idea_central=idea_central,
        diagnostico_base=diagnostico_base,
        prompt=request.prompt,
        perfil_runtime=perfil_runtime,
        texto_post=texto_generado,
    )

    return post, diagnostico_editorial, idea_central


def ejecutar_flujo_textual(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    aprobacion: AprobacionHumana,
    base_dir: str | None = None,
    clock: Optional[Callable[[], str]] = None,
    publisher: PublicationPublisherPort | None = None,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
) -> ManifestEvidencia:
    post, diagnostico_editorial, _ = generar_candidato_textual(
        entrada=entrada,
        adapter=adapter,
        profile_resolver=profile_resolver,
        channel_strategy=channel_strategy,
    )
    return generar_borrador_local_desde_simulacion(
        entrada=entrada,
        post=post,
        diagnostico=diagnostico_editorial,
        aprobacion=aprobacion,
        base_dir=base_dir,
        clock=clock,
        publisher=publisher,
    )
