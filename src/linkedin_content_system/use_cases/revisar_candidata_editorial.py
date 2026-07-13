from __future__ import annotations

from typing import Protocol

from linkedin_content_system.contracts import (
    BloqueoCritico,
    DiagnosticoEditorial,
    EstadoRevision,
    IdeaCentral,
    NivelRiesgoGenerico,
    TipoBloqueoCritico,
)
from linkedin_content_system.use_cases.diagnosticar_base_editorial import DiagnosticoBaseEditorial
from linkedin_content_system.use_cases.flujo_textual_runtime import PerfilNarrativoRuntime
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


class RevisorEditorial(Protocol):
    """Revisa una candidata sin aprobarla ni generar una salida final."""

    def revisar(
        self,
        idea_central: IdeaCentral,
        diagnostico_base: DiagnosticoBaseEditorial,
        perfil: PerfilNarrativoRuntime,
        texto_post: str,
    ) -> DiagnosticoEditorial: ...


class RevisorEditorialConservador:
    """Distingue gates demostrables de cualidades que requieren juicio humano."""

    def revisar(
        self,
        idea_central: IdeaCentral,
        diagnostico_base: DiagnosticoBaseEditorial,
        perfil: PerfilNarrativoRuntime,
        texto_post: str,
    ) -> DiagnosticoEditorial:
        bloqueos: list[BloqueoCritico] = []
        try:
            validar_texto_sin_pii_basica(texto_post)
            validar_texto_sin_secretos_basicos(texto_post)
            validar_sin_rutas_locales(texto_post)
        except ValueError as exc:
            bloqueos.append(BloqueoCritico(tipo=TipoBloqueoCritico.COMPLIANCE, descripcion=str(exc)))

        texto = " ".join(texto_post.lower().split())
        tokens_idea = [token for token in idea_central.idea_central.lower().split() if len(token) > 3]
        claridad = (
            EstadoRevision.PASS
            if texto and (not tokens_idea or any(token in texto for token in tokens_idea))
            else EstadoRevision.WARN
        )
        compliance = EstadoRevision.FAIL if bloqueos else EstadoRevision.PASS
        estado = EstadoRevision.FAIL if bloqueos else EstadoRevision.WARN
        recomendaciones = list(diagnostico_base.recomendaciones)
        recomendaciones.append(
            "La voz, naturalidad, hook, autenticidad y CTA requieren revisión humana; no se autoaprueba la pieza."
        )
        return DiagnosticoEditorial(
            claridad_idea=claridad,
            audiencia=EstadoRevision.WARN,
            hook=EstadoRevision.WARN if texto else EstadoRevision.FAIL,
            voz_cliente=EstadoRevision.WARN if perfil.id_perfil else EstadoRevision.FAIL,
            autenticidad=EstadoRevision.WARN if not bloqueos else EstadoRevision.FAIL,
            cta=EstadoRevision.WARN if texto else EstadoRevision.FAIL,
            compliance=compliance,
            riesgo_generico=NivelRiesgoGenerico.ALTO if bloqueos else NivelRiesgoGenerico.MEDIO,
            estado_revision=estado,
            motivo=(
                f"{diagnostico_base.resumen} Compliance y estructura se validan por separado. "
                "La evaluación editorial automática es conservadora y requiere revisión humana antes de la decisión humana."
            ),
            ajustes_recomendados=" | ".join(recomendaciones),
            bloqueos_criticos=bloqueos,
        )
