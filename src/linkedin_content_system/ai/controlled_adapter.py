from __future__ import annotations

import os
from typing import Optional

from linkedin_content_system.ai.mock_adapter import MockModelAdapter
from linkedin_content_system.ai.litellm_adapter import LiteLLMModelAdapter
from linkedin_content_system.ai.ports import ModelAdapter


def _extraer_linea(prompt: str, prefijo: str) -> str:
    for linea in prompt.splitlines():
        if linea.startswith(prefijo):
            return linea.split(":", 1)[1].strip()
    return ""


def _limpiar_fragmento(texto: str) -> str:
    return texto.strip().rstrip(" .!?¡¿")


def _construir_borrador_util(prompt: str) -> str:
    texto_base = _extraer_linea(prompt, "Texto base original:")
    idea_central = _extraer_linea(prompt, "Idea central:")
    idea_explicita = _extraer_linea(prompt, "Idea explicita del usuario:")
    intencion = _extraer_linea(prompt, "Resumen de intencion:")
    audiencia = _extraer_linea(prompt, "Audiencia objetivo:")
    objetivo = _extraer_linea(prompt, "Objetivo del post:")
    cta = _extraer_linea(prompt, "CTA deseado:") or "Que opinas?"

    idea_prioritaria = idea_explicita or idea_central or texto_base
    hook = _limpiar_fragmento(idea_prioritaria) or "Hay una idea simple que conviene aterrizar"
    cuerpo_origen = texto_base or idea_prioritaria
    cuerpo = _limpiar_fragmento(cuerpo_origen) or "El flujo textual debe dar una base util y revisable"
    cierre = cta if cta.endswith("?") else f"{cta}?"

    lineas = [
        f"Hay una idea concreta que vale la pena priorizar: {hook}.",
        f"Cuando se aterriza bien, el flujo gana foco y utilidad: {cuerpo}.",
    ]

    if idea_explicita:
        lineas.append(f"La idea explicita del usuario es {_limpiar_fragmento(idea_explicita)}.")
    if intencion:
        lineas.append(f"La intencion editorial resumida es {intencion.lower()}.")
    if audiencia:
        lineas.append(f"Esta pieza apunta a {audiencia}.")
    if objetivo:
        lineas.append(f"El objetivo del post es {objetivo}.")

    lineas.append(cierre)
    return "\n".join(lineas)


class ControlledModelAdapter(ModelAdapter):
    """
    Adaptador local controlado.

    Sigue siendo offline y sin credenciales, pero transforma el prompt en un
    borrador editorial más util que el mock plano.
    """

    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")

        return _construir_borrador_util(prompt.strip())


def construir_model_adapter(modo: Optional[str] = None) -> ModelAdapter:
    """
    Selecciona el adaptador textual sin tocar proveedores reales.

    Valores admitidos:
    - ``controlado`` o ``controlled``: adaptador local útil por defecto.
    - ``mock``: adaptador determinista de pruebas.
    - ``litellm``: adaptador real configurable detrás del seam.
    """

    modo_resuelto = (modo or os.getenv("LINKEDIN_CONTENT_AI_ADAPTER", "controlado")).strip().lower()
    if modo_resuelto in {"controlado", "controlled"}:
        return ControlledModelAdapter()
    if modo_resuelto == "mock":
        return MockModelAdapter()
    if modo_resuelto == "litellm":
        return LiteLLMModelAdapter()
    raise ValueError(
        "Modo de adaptador desconocido. Valores admitidos: controlado, controlled, mock, litellm."
    )
