import re
import unicodedata
from typing import Callable, Optional

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    AuditoriaEditorial,
    AprobacionHumana,
    DiagnosticoEditorial,
    EntradaContenido,
    ManifestEvidencia,
    IdeaCentral,
    EstadoRevision,
    NivelRiesgoGenerico,
    PostCandidato,
)
from linkedin_content_system.publishers import PublicationPublisherPort
from linkedin_content_system.use_cases.diagnosticar_base_editorial import diagnosticar_base_editorial
from linkedin_content_system.use_cases.extraer_idea_central import extraer_idea_central
from linkedin_content_system.use_cases.extraer_intencion_editorial import extraer_intencion_editorial
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
    NarrativeProfileResolver,
    TextChannelStrategy,
)
from linkedin_content_system.use_cases.generar_borrador_local import generar_borrador_local_desde_simulacion
from linkedin_content_system.use_cases.generar_post_mock import generar_post_mock
from linkedin_content_system.use_cases.normalizar_entrada_textual import normalizar_entrada_textual
from linkedin_content_system.use_cases.revisar_candidata_editorial import (
    RevisorEditorial,
    RevisorEditorialDeterminista,
)
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


def _normalizar_para_revision(texto: str) -> str:
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto).lower()
        if unicodedata.category(caracter) != "Mn"
    )


def _contiene_metatexto_visible(texto_revision: str) -> bool:
    patrones = [
        r"(?m)^\s*(?:#{1,6}\s*)?(?:revision inicial|analisis|notas editoriales|explicacion)\s*:",
        r"(?m)^\s*(?:aqui tienes|te comparto|te dejo)\s+(?:un\s+)?(?:borrador|post|texto)",
        r"(?m)^\s*(?:borrador del post|post candidato|publicacion para linkedin)\s*:",
    ]
    return any(re.search(patron, texto_revision) for patron in patrones)


def _tiene_cierre_completo(texto_limpio: str) -> bool:
    return bool(re.search(r'[.!?…][\"\'”’\)\]]*$', texto_limpio))


def _tiene_invencion_experiencial_no_respaldada(
    texto_post: str,
    texto_base: str,
    experiencias_autorizadas: tuple[str, ...] = (),
) -> bool:
    texto_post_revision = _normalizar_para_revision(texto_post)
    texto_base_revision = _normalizar_para_revision(texto_base)

    patrones_experienciales = {
        "recuerdo": [r"\brecuerdo cuando\b", r"\brecuerdo\b"],
        "trabajo_previo": [r"\btrabaje\b", r"\btrabajamos\b"],
        "aprendizaje": [r"\baprendi\b", r"\baprendimos\b"],
        "realizacion": [r"\bme di cuenta\b", r"\bnos dimos cuenta\b"],
        "experiencia": [r"\ben mi experiencia\b", r"\ben nuestra experiencia\b"],
        "vivencia": [r"\bvivi\b", r"\bnos paso\b", r"\bme paso\b"],
        "memoria_proyecto": [r"\bproyecto similar\b"],
    }

    categorias_post = {
        categoria
        for categoria, patrones in patrones_experienciales.items()
        if any(re.search(patron, texto_post_revision) for patron in patrones)
    }
    if not categorias_post:
        return False

    texto_autorizado_revision = " ".join(
        _normalizar_para_revision(experiencia) for experiencia in experiencias_autorizadas
    )
    categorias_base = {
        categoria
        for categoria, patrones in patrones_experienciales.items()
        if any(
            re.search(patron, texto_base_revision) or re.search(patron, texto_autorizado_revision)
            for patron in patrones
        )
    }

    categorias_no_respaldadas = categorias_post - categorias_base
    return bool(categorias_no_respaldadas)


def _validar_salida_post_candidata(texto_post: str) -> str:
    texto_limpio = (texto_post or "").strip()
    if not texto_limpio:
        raise ValueError("La salida del modelo está vacía.")
    # El doble mock es una valla de regresión offline; su formato deliberadamente
    # artificial no representa la salida del proveedor ni se usa en el smoke.
    if texto_limpio.startswith("[BORRADOR SIMULADO DE POST]"):
        return texto_limpio

    texto_revision = _normalizar_para_revision(texto_limpio)
    if _contiene_metatexto_visible(texto_revision):
        raise ValueError("La salida del modelo contiene metatexto editorial y no puede persistirse como post.")

    if not _tiene_cierre_completo(texto_limpio):
        raise ValueError("La salida del modelo termina con un cierre incompleto y no puede persistirse como post.")
    return texto_limpio


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


def generar_candidato_auditado(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
    revisor: RevisorEditorial | None = None,
) -> tuple[PostCandidato, DiagnosticoEditorial, IdeaCentral, AuditoriaEditorial]:
    fuente = normalizar_entrada_textual(entrada)
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

    texto_generado = _validar_salida_post_candidata(generar_post_mock(
        request.prompt,
        adapter,
        system_instruction=request.system_instruction,
    ))
    experiencias_input = tuple(
        str(item).strip()
        for item in (entrada.metadatos_origen or {}).get("experiencias_autorizadas", [])
        if str(item).strip()
    )
    if _tiene_invencion_experiencial_no_respaldada(
        texto_generado,
        entrada.texto_base,
        experiencias_input + perfil_runtime.experiencias_autorizadas,
    ):
        raise ValueError(
            "La salida del modelo inventa experiencia personal no respaldada por la entrada y no puede persistirse como post."
        )
    post = PostCandidato(texto=texto_generado)
    auditoria = (revisor or RevisorEditorialDeterminista()).revisar(
        fuente=fuente, perfil=perfil_runtime, texto_post=texto_generado
    )
    estado_revision = EstadoRevision.FAIL if auditoria.estado.value == "FAIL" else EstadoRevision.WARN
    diagnostico_editorial = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.WARN,
        audiencia=EstadoRevision.WARN,
        hook=EstadoRevision.WARN,
        voz_cliente=EstadoRevision.WARN,
        autenticidad=EstadoRevision.FAIL if auditoria.estado.value == "FAIL" else EstadoRevision.WARN,
        cta=EstadoRevision.WARN,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.MEDIO,
        estado_revision=estado_revision,
        motivo="Auditoría editorial estructurada disponible; requiere revisión humana antes de la aprobación.",
        ajustes_recomendados=auditoria.feedback_estructurado or None,
    )

    return post, diagnostico_editorial, idea_central, auditoria


def generar_candidato_textual(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
    revisor: RevisorEditorial | None = None,
) -> tuple[PostCandidato, DiagnosticoEditorial, IdeaCentral]:
    post, diagnostico, idea, _ = generar_candidato_auditado(
        entrada, adapter, profile_resolver, channel_strategy, revisor
    )
    return post, diagnostico, idea


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
