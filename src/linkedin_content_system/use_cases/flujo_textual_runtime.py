from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from linkedin_content_system.contracts import EntradaContenido


@dataclass(frozen=True)
class PerfilNarrativoRuntime:
    id_perfil: str
    tono_base: str
    tono_prohibido: str
    palabras_clave: tuple[str, ...] = ()
    frases_prohibidas: tuple[str, ...] = ()
    cta_preferidos: tuple[str, ...] = ()
    nivel_tecnico: str = "moderado"
    nivel_opinion_personal: str = "prudente"
    temas_permitidos: tuple[str, ...] = ()
    temas_prohibidos: tuple[str, ...] = ()
    experiencias_autorizadas: tuple[str, ...] = ()
    afirmaciones_sostenibles: tuple[str, ...] = ()
    ejemplos_si_suena: tuple[str, ...] = ()
    ejemplos_no_suena: tuple[str, ...] = ()
    estado_completitud: str = "fallback"


@dataclass(frozen=True)
class SolicitudGeneracionTextual:
    canal_destino: str
    prompt: str
    system_instruction: str


class NarrativeProfileResolver(Protocol):
    def resolve(self, id_perfil: str) -> PerfilNarrativoRuntime:
        """Resuelve el perfil narrativo runtime a partir de un id externo al core."""


class TextChannelStrategy(Protocol):
    canal_destino: str

    def supports(self, entrada: EntradaContenido) -> bool:
        """Indica si la estrategia puede operar con la entrada actual."""

    def build_request(
        self,
        entrada: EntradaContenido,
        idea_central: str,
        resumen_intencion: str,
        perfil: PerfilNarrativoRuntime,
    ) -> SolicitudGeneracionTextual:
        """Construye la solicitud textual para el adapter."""


def _string_tuple(value) -> tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _build_fallback_profile(id_perfil: str) -> PerfilNarrativoRuntime:
    return PerfilNarrativoRuntime(
        id_perfil=id_perfil,
        tono_base=(
            "Profesional, claro y directo. Prioriza aprendizajes reales, límites explícitos "
            "y una voz humana sin hype."
        ),
        tono_prohibido="Promesas grandilocuentes, autoridad fingida y engagement artificial.",
        cta_preferidos=("pregunta final concreta",),
        estado_completitud="fallback",
    )


_PROFILE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validar_id_perfil(id_perfil: str) -> str:
    id_limpio = (id_perfil or "").strip()
    if not id_limpio:
        raise ValueError("id_perfil no puede estar vacío.")
    if not _PROFILE_ID_PATTERN.fullmatch(id_limpio):
        raise ValueError(
            "id_perfil inválido: solo admite letras, números, guion y guion bajo."
        )
    return id_limpio


class FilesystemNarrativeProfileResolver:
    """
    Resuelve perfiles narrativos desde JSON fuera del core.

    Si el perfil no existe en disco, devuelve una configuración fallback segura.
    """

    def __init__(self, profile_dir: str | Path | None = None):
        self.profile_dir = Path(profile_dir).expanduser() if profile_dir else None

    def resolve(self, id_perfil: str) -> PerfilNarrativoRuntime:
        id_resuelto = _validar_id_perfil(id_perfil)

        if self.profile_dir is None:
            return _build_fallback_profile(id_resuelto)

        base_dir = self.profile_dir.resolve()
        profile_path = (base_dir / f"{id_resuelto}.json").resolve()
        if profile_path.parent != base_dir:
            raise ValueError("id_perfil inválido: la ruta resuelta sale de profile_dir.")
        if not profile_path.exists():
            return _build_fallback_profile(id_resuelto)

        data = json.loads(profile_path.read_text(encoding="utf-8"))
        voz = data.get("voz_marca") or {}
        lenguaje = data.get("lenguaje") or {}
        cta = data.get("cta") or {}
        limites = data.get("limites") or {}
        ejemplos = data.get("ejemplos") or {}

        tono_base = ((voz.get("tono_base") or {}).get("descripcion") or "").strip()
        tono_prohibido = ((voz.get("tono_prohibido") or {}).get("descripcion") or "").strip()

        return PerfilNarrativoRuntime(
            id_perfil=str(data.get("id_perfil") or id_resuelto).strip(),
            tono_base=tono_base or _build_fallback_profile(id_resuelto).tono_base,
            tono_prohibido=tono_prohibido or _build_fallback_profile(id_resuelto).tono_prohibido,
            palabras_clave=_string_tuple((lenguaje.get("palabras_frecuentes") or []))
            + _string_tuple((lenguaje.get("expresiones_propias") or [])),
            frases_prohibidas=_string_tuple(lenguaje.get("frases_prohibidas")),
            cta_preferidos=_string_tuple(cta.get("cta_preferidos")),
            nivel_tecnico=str(data.get("nivel_tecnico") or "moderado").strip(),
            nivel_opinion_personal=str(data.get("nivel_opinion_personal") or "prudente").strip(),
            temas_permitidos=_string_tuple(data.get("temas_permitidos")),
            temas_prohibidos=_string_tuple(data.get("temas_prohibidos")),
            experiencias_autorizadas=_string_tuple(data.get("experiencias_autorizadas")),
            afirmaciones_sostenibles=_string_tuple(data.get("afirmaciones_sostenibles")),
            ejemplos_si_suena=_string_tuple(data.get("ejemplos_si_suena") or ejemplos.get("si_suena")),
            ejemplos_no_suena=_string_tuple(data.get("ejemplos_no_suena") or ejemplos.get("no_suena")),
            estado_completitud=str(data.get("estado_completitud") or limites.get("estado_completitud") or "parcial").strip(),
        )


class LinkedInTextChannelStrategy:
    canal_destino = "linkedin"

    def supports(self, entrada: EntradaContenido) -> bool:
        return self.canal_destino in entrada.canales_destino

    def build_request(
        self,
        entrada: EntradaContenido,
        idea_central: str,
        resumen_intencion: str,
        perfil: PerfilNarrativoRuntime,
    ) -> SolicitudGeneracionTextual:
        lineas_prompt = [
            f"Canal destino: {self.canal_destino}",
            f"Texto base original: {entrada.texto_base.strip()}",
            f"Idea central: {idea_central}",
            f"Resumen de intencion: {resumen_intencion}",
            f"Perfil narrativo resuelto: {perfil.id_perfil}",
        ]

        if entrada.intencion_editorial.idea_central:
            lineas_prompt.append(f"Idea explicita del usuario: {entrada.intencion_editorial.idea_central}")
        if entrada.intencion_editorial.audiencia_objetivo:
            lineas_prompt.append(f"Audiencia objetivo: {entrada.intencion_editorial.audiencia_objetivo}")
        if entrada.intencion_editorial.objetivo_del_post:
            lineas_prompt.append(f"Objetivo del post: {entrada.intencion_editorial.objetivo_del_post}")
        if entrada.intencion_editorial.cta_intencionado:
            lineas_prompt.append(f"CTA deseado: {entrada.intencion_editorial.cta_intencionado}")
        if perfil.palabras_clave:
            lineas_prompt.append(f"Palabras o expresiones propias: {', '.join(perfil.palabras_clave)}")
        metadata = entrada.metadatos_origen or {}
        for clave, etiqueta in (
            ("hechos_autorizados", "Hechos autorizados"),
            ("opiniones_explicitas", "Opiniones explícitas"),
            ("experiencias_autorizadas", "Experiencias autorizadas"),
            ("instrucciones_editoriales", "Instrucciones editoriales"),
            ("no_inferir", "No inferir"),
        ):
            valores = _string_tuple(metadata.get(clave))
            if valores:
                lineas_prompt.append(f"{etiqueta}: {', '.join(valores)}")
        if perfil.experiencias_autorizadas:
            lineas_prompt.append(
                f"Experiencias autorizadas por perfil: {', '.join(perfil.experiencias_autorizadas)}"
            )
        if perfil.afirmaciones_sostenibles:
            lineas_prompt.append(
                f"Afirmaciones sostenibles por perfil: {', '.join(perfil.afirmaciones_sostenibles)}"
            )

        lineas_prompt.append(
            "Escribe un borrador breve, claro y revisable para LinkedIn sin inventar experiencia ni claims."
        )
        lineas_prompt.extend(
            [
                "Mantén la salida entre 80 y 120 palabras, con un máximo de 3 párrafos cortos.",
                "Contrato de salida obligatorio: Devuelve exclusivamente el post candidato listo para revisión.",
                "No incluyas análisis, revisión inicial, notas editoriales, explicaciones, títulos de sección ni metatexto visible.",
                "No añadas preámbulos como 'Aquí tienes un borrador del post' ni frases equivalentes.",
                "No afirmes experiencias personales en primera persona salvo que estén explícitas en el texto base.",
                "Completa la última oración y termina el post con puntuación final.",
            ]
        )

        system_parts = [
            "Actúa como un asistente editorial prudente.",
            f"Tono base: {perfil.tono_base}",
            f"Tono prohibido: {perfil.tono_prohibido}",
        ]
        if perfil.frases_prohibidas:
            system_parts.append(
                f"Frases prohibidas: {', '.join(perfil.frases_prohibidas)}"
            )
        if perfil.cta_preferidos:
            system_parts.append(
                f"CTA preferidos: {', '.join(perfil.cta_preferidos)}"
            )
        if perfil.temas_prohibidos:
            system_parts.append(f"Temas prohibidos: {', '.join(perfil.temas_prohibidos)}")
        if perfil.ejemplos_si_suena:
            system_parts.append(f"Ejemplos que sí suenan: {' | '.join(perfil.ejemplos_si_suena)}")
        if perfil.ejemplos_no_suena:
            system_parts.append(f"Ejemplos que no suenan: {' | '.join(perfil.ejemplos_no_suena)}")
        system_parts.append(
            "Si faltan datos, mantén el texto prudente y no inventes autoridad, experiencia personal ni recuerdos."
        )

        return SolicitudGeneracionTextual(
            canal_destino=self.canal_destino,
            prompt="\n".join(lineas_prompt),
            system_instruction=" ".join(system_parts),
        )
