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

        lineas_prompt.append(
            "Escribe un borrador breve, claro y revisable para LinkedIn sin inventar experiencia ni claims."
        )
        lineas_prompt.extend(
            [
                "Contrato de salida obligatorio: Devuelve exclusivamente el post candidato listo para revisión.",
                "No incluyas análisis, revisión inicial, notas editoriales, explicaciones, títulos de sección ni metatexto.",
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
        system_parts.append("Si faltan datos, mantén el texto prudente y no inventes autoridad.")

        return SolicitudGeneracionTextual(
            canal_destino=self.canal_destino,
            prompt="\n".join(lineas_prompt),
            system_instruction=" ".join(system_parts),
        )
