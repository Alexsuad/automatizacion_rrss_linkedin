from __future__ import annotations

import os
from typing import Optional

from linkedin_content_system.ai.mock_adapter import MockModelAdapter
from linkedin_content_system.ai.ports import ModelAdapter


def _extraer_linea(prompt: str, prefijo: str) -> str:
    for linea in prompt.splitlines():
        if linea.startswith(prefijo):
            return linea.split(":", 1)[1].strip()
    return ""


def _construir_borrador_util(prompt: str) -> str:
    texto_base = _extraer_linea(prompt, "Texto base original:")
    idea_central = _extraer_linea(prompt, "Idea central:")
    intencion = _extraer_linea(prompt, "Resumen de intencion:")
    audiencia = _extraer_linea(prompt, "Audiencia objetivo:")
    objetivo = _extraer_linea(prompt, "Objetivo del post:")
    cta = _extraer_linea(prompt, "CTA deseado:") or "Que opinas?"

    hook = idea_central or texto_base or "Hay una idea simple que conviene aterrizar"
    cuerpo = texto_base or idea_central or "El flujo textual debe dar una base util y revisable."
    cierre = cta if cta.endswith("?") else f"{cta}?"

    lineas = [
        f"Hay una idea concreta que vale la pena priorizar: {hook}.",
        f"Cuando se aterriza bien, el flujo gana foco y utilidad: {cuerpo}.",
    ]

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
    - ``controlado``: adaptador local útil por defecto.
    - ``mock``: adaptador determinista de pruebas.
    """

    modo_resuelto = (modo or os.getenv("LINKEDIN_CONTENT_AI_ADAPTER", "controlado")).strip().lower()
    if modo_resuelto == "mock":
        return MockModelAdapter()
    return ControlledModelAdapter()
