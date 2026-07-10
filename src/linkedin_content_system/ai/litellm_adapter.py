from __future__ import annotations

import os
from typing import Any, Optional

try:
    import litellm
except ImportError:  # pragma: no cover - solo si falta la dependencia instalada
    litellm = None

from linkedin_content_system.ai.ports import ModelAdapter


class LiteLLMAdapterError(ValueError):
    """Error controlado del adaptador real de IA."""


def _resolver_modelo(modelo: str, proveedor: Optional[str]) -> str:
    if proveedor and "/" not in modelo:
        return f"{proveedor}/{modelo}"
    return modelo


def _extraer_texto_respuesta(respuesta: Any) -> str:
    if hasattr(respuesta, "choices") and respuesta.choices:
        primera = respuesta.choices[0]
        mensaje = getattr(primera, "message", None)
        if mensaje is not None:
            contenido = getattr(mensaje, "content", None)
            if contenido:
                return str(contenido)
        texto = getattr(primera, "text", None)
        if texto:
            return str(texto)

    if isinstance(respuesta, dict):
        choices = respuesta.get("choices") or []
        if choices:
            primera = choices[0]
            if isinstance(primera, dict):
                mensaje = primera.get("message") or {}
                contenido = mensaje.get("content")
                if contenido:
                    return str(contenido)
                texto = primera.get("text")
                if texto:
                    return str(texto)

    return ""


class LiteLLMModelAdapter(ModelAdapter):
    """
    Adaptador real configurable detrás de LiteLLM.

    El core no importa LiteLLM: solo este módulo conoce el proveedor.
    """

    def __init__(
        self,
        modelo: Optional[str] = None,
        proveedor: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.modelo = (modelo or os.getenv("LINKEDIN_CONTENT_AI_MODEL") or "").strip()
        self.proveedor = (proveedor or os.getenv("LINKEDIN_CONTENT_AI_PROVIDER") or "").strip() or None
        self.timeout_seconds = timeout_seconds

        if not self.modelo:
            raise LiteLLMAdapterError(
                "Falta configurar el modelo real para LINKEDIN_CONTENT_AI_ADAPTER=litellm."
            )
        if self.timeout_seconds <= 0:
            raise LiteLLMAdapterError("El timeout del adaptador real debe ser positivo.")

    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise LiteLLMAdapterError("El prompt no puede estar vacío.")
        if litellm is None:
            raise LiteLLMAdapterError("La dependencia litellm no está disponible en este entorno.")

        messages = []
        if system_instruction and system_instruction.strip():
            messages.append({"role": "system", "content": system_instruction.strip()})
        messages.append({"role": "user", "content": prompt.strip()})

        try:
            respuesta = litellm.completion(
                model=_resolver_modelo(self.modelo, self.proveedor),
                messages=messages,
                timeout=self.timeout_seconds,
                temperature=0.2,
            )
        except Exception as exc:  # pragma: no cover - la red/proveedor se stubbea en tests
            raise LiteLLMAdapterError(
                "No se pudo generar texto con el proveedor IA configurado."
            ) from exc

        contenido = _extraer_texto_respuesta(respuesta).strip()
        if not contenido:
            raise LiteLLMAdapterError("El proveedor IA no devolvió contenido utilizable.")
        return contenido
