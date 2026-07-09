from typing import Callable, Optional

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    BloqueoCritico,
    DiagnosticoEditorial,
    EntradaContenido,
    EstadoRevision,
    ManifestEvidencia,
    NivelRiesgoGenerico,
    PostCandidato,
    TipoBloqueoCritico,
    TipoEntrada,
)
from linkedin_content_system.use_cases.diagnosticar_base_editorial import diagnosticar_base_editorial
from linkedin_content_system.use_cases.extraer_idea_central import extraer_idea_central
from linkedin_content_system.use_cases.extraer_intencion_editorial import extraer_intencion_editorial
from linkedin_content_system.use_cases.generar_borrador_local import generar_borrador_local_desde_simulacion
from linkedin_content_system.use_cases.generar_post_mock import generar_post_mock
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


def _normalizar_texto(texto: str) -> str:
    return " ".join((texto or "").lower().split())


def _construir_prompt_textual(entrada: EntradaContenido, idea_central, intencion_clasificada) -> str:
    lineas = [
        f"Texto base original: {entrada.texto_base.strip()}",
        f"Idea central: {idea_central.idea_central}",
        f"Resumen de intencion: {intencion_clasificada.resumen_intencion}",
        f"Perfil narrativo de referencia: {entrada.perfil_narrativo.id_perfil}",
    ]

    if entrada.intencion_editorial.idea_central:
        lineas.append(f"Idea explicita del usuario: {entrada.intencion_editorial.idea_central}")
    if entrada.intencion_editorial.audiencia_objetivo:
        lineas.append(f"Audiencia objetivo: {entrada.intencion_editorial.audiencia_objetivo}")
    if entrada.intencion_editorial.objetivo_del_post:
        lineas.append(f"Objetivo del post: {entrada.intencion_editorial.objetivo_del_post}")
    if entrada.intencion_editorial.cta_intencionado:
        lineas.append(f"CTA deseado: {entrada.intencion_editorial.cta_intencionado}")

    lineas.append("Escribe un borrador breve, claro y publicable en LinkedIn.")
    return "\n".join(lineas)


def _construir_diagnostico_editorial_minimo(
    entrada: EntradaContenido,
    idea_central,
    diagnostico_base,
    prompt: str,
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
    primer_bloque = texto_post.strip().splitlines()[0] if texto_post.strip() else ""
    hook = EstadoRevision.PASS if primer_bloque.strip() else EstadoRevision.WARN
    voz_cliente = (
        EstadoRevision.PASS
        if entrada.perfil_narrativo.id_perfil and entrada.perfil_narrativo.id_perfil in prompt
        else EstadoRevision.WARN
    )
    autenticidad = EstadoRevision.PASS if cumplimiento_ok else EstadoRevision.FAIL
    cta = (
        EstadoRevision.PASS
        if (
            "?" in texto_post
            or "que opinas" in texto_post_normalizado
            or "te leo" in texto_post_normalizado
            or len(texto_post.split()) >= 8
        )
        else EstadoRevision.WARN
    )
    compliance = EstadoRevision.PASS if cumplimiento_ok else EstadoRevision.FAIL
    riesgo_generico = NivelRiesgoGenerico.BAJO if cumplimiento_ok else NivelRiesgoGenerico.ALTO

    revisiones = [claridad_idea, audiencia, hook, voz_cliente, autenticidad, cta, compliance]
    if not cumplimiento_ok:
        estado_revision = EstadoRevision.FAIL
    elif any(revision == EstadoRevision.WARN for revision in revisiones):
        estado_revision = EstadoRevision.WARN
    else:
        estado_revision = EstadoRevision.PASS

    motivo = diagnostico_base.resumen
    if diagnostico_base.estado == "WARN":
        motivo = f"{diagnostico_base.resumen} Base editorial derivada con advertencias controladas."

    ajustes_recomendados = (
        " | ".join(diagnostico_base.recomendaciones) if diagnostico_base.recomendaciones else None
    )

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


def ejecutar_flujo_textual(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    aprobacion: AprobacionHumana,
    base_dir: str,
    clock: Optional[Callable[[], str]] = None,
) -> ManifestEvidencia:
    if entrada.tipo_entrada != TipoEntrada.TEXTO_MANUAL:
        raise ValueError("Este flujo solo admite entradas de texto manual.")

    if "linkedin" not in entrada.canales_destino:
        raise ValueError("Este flujo textual inicial requiere que 'linkedin' esté presente en canales_destino.")

    idea_central = extraer_idea_central(entrada.texto_base)
    intencion_clasificada = extraer_intencion_editorial(idea_central)
    diagnostico_base = diagnosticar_base_editorial(idea_central, intencion_clasificada)

    if diagnostico_base.estado == "FAIL":
        raise ValueError("La base editorial es insuficiente para continuar el flujo textual.")

    prompt = _construir_prompt_textual(entrada, idea_central, intencion_clasificada)
    texto_generado = generar_post_mock(prompt, adapter)
    post = PostCandidato(texto=texto_generado)
    diagnostico_editorial = _construir_diagnostico_editorial_minimo(
        entrada=entrada,
        idea_central=idea_central,
        diagnostico_base=diagnostico_base,
        prompt=prompt,
        texto_post=texto_generado,
    )

    return generar_borrador_local_desde_simulacion(
        entrada=entrada,
        post=post,
        diagnostico=diagnostico_editorial,
        aprobacion=aprobacion,
        base_dir=base_dir,
        clock=clock,
    )
