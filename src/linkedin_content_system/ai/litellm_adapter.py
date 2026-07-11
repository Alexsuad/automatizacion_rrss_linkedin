from __future__ import annotations

import importlib
import os
from urllib.parse import urlparse
from typing import Any, Optional

from linkedin_content_system.ai.ports import ModelAdapter

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_TOKENS = 280
_LITELLM_UNSET = object()
litellm: Any = _LITELLM_UNSET


class LiteLLMAdapterError(RuntimeError):
    """Error base del adaptador LiteLLM."""


class LiteLLMConfigurationError(LiteLLMAdapterError):
    """Configuracion o entrada invalida para usar el adaptador real."""


class LiteLLMProviderError(LiteLLMAdapterError):
    """Fallo externo del proveedor o de la red al generar texto."""


class LiteLLMResponseError(LiteLLMAdapterError):
    """La respuesta del proveedor no contiene texto utilizable."""


def _resolver_modelo(modelo: str, proveedor: Optional[str]) -> str:
    if proveedor and "/" not in modelo:
        return f"{proveedor}/{modelo}"
    return modelo


def _es_ollama(proveedor: Optional[str], modelo: Optional[str]) -> bool:
    proveedor_normalizado = (proveedor or "").strip().lower()
    modelo_normalizado = (modelo or "").strip().lower()
    return (
        proveedor_normalizado == "ollama"
        or modelo_normalizado.startswith("ollama_")
        or modelo_normalizado.startswith("ollama/")
    )


def _validar_api_base(raw_api_base: Optional[str]) -> Optional[str]:
    if raw_api_base is None:
        return None

    api_base_resuelta = str(raw_api_base).strip()
    if not api_base_resuelta:
        return None

    parsed = urlparse(api_base_resuelta)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LiteLLMConfigurationError(
            "El api_base del adaptador real debe ser una URL http o https valida."
        )

    return api_base_resuelta


def _resolver_api_base(
    api_base: Optional[str],
    proveedor: Optional[str],
    modelo: Optional[str],
) -> Optional[str]:
    if api_base is not None:
        return _validar_api_base(api_base)

    api_base_general = os.getenv("LINKEDIN_CONTENT_AI_API_BASE")
    if api_base_general:
        return _validar_api_base(api_base_general)

    if _es_ollama(proveedor, modelo):
        return _validar_api_base(os.getenv("OLLAMA_API_BASE"))

    return None


def _parsear_timeout(timeout_seconds: Optional[float]) -> float:
    raw_timeout = timeout_seconds
    if raw_timeout is None:
        raw_timeout = os.getenv("LINKEDIN_CONTENT_AI_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)

    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError) as exc:
        raise LiteLLMConfigurationError("El timeout del adaptador real debe ser numerico y positivo.") from exc

    if timeout <= 0:
        raise LiteLLMConfigurationError("El timeout del adaptador real debe ser numerico y positivo.")
    return timeout


def _parsear_max_tokens(max_tokens: Optional[int]) -> int:
    raw_max_tokens = max_tokens
    if raw_max_tokens is None:
        raw_max_tokens = os.getenv("LINKEDIN_CONTENT_AI_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))

    try:
        tokens = int(str(raw_max_tokens).strip())
    except (TypeError, ValueError) as exc:
        raise LiteLLMConfigurationError(
            "LINKEDIN_CONTENT_AI_MAX_TOKENS (max_tokens) debe ser un entero positivo."
        ) from exc

    if tokens <= 0:
        raise LiteLLMConfigurationError(
            "LINKEDIN_CONTENT_AI_MAX_TOKENS (max_tokens) debe ser un entero positivo."
        )
    return tokens


def _resolver_litellm() -> Any:
    global litellm

    if litellm is _LITELLM_UNSET:
        try:
            litellm = importlib.import_module("litellm")
        except ImportError:
            litellm = None
    return litellm


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


def _es_error_de_configuracion(exc: Exception, client: Any) -> bool:
    nombre = exc.__class__.__name__.lower()
    mensaje = str(exc).lower()

    clases_config = (
        "authenticationerror",
        "permissiondeniederror",
        "badrequesterror",
    )
    if nombre in clases_config:
        return True

    for attr in ("AuthenticationError", "PermissionDeniedError", "BadRequestError"):
        candidate = getattr(client, attr, None)
        if candidate is not None and isinstance(exc, candidate):
            return True

    return any(
        marca in mensaje
        for marca in (
            "authentication",
            "unauthorized",
            "invalid api key",
            "api key",
            "credential",
            "permission denied",
            "model not found",
            "invalid model",
            "configuration",
        )
    )


class LiteLLMModelAdapter(ModelAdapter):
    """
    Adaptador real configurable detrás de LiteLLM.

    El core no importa LiteLLM: solo este módulo conoce el proveedor.
    """

    def __init__(
        self,
        modelo: Optional[str] = None,
        proveedor: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.modelo = (modelo or os.getenv("LINKEDIN_CONTENT_AI_MODEL") or "").strip()
        self.proveedor = (proveedor or os.getenv("LINKEDIN_CONTENT_AI_PROVIDER") or "").strip() or None
        self.api_base = _resolver_api_base(api_base, self.proveedor, self.modelo)
        self.timeout_seconds = _parsear_timeout(timeout_seconds)
        self.max_tokens = _parsear_max_tokens(max_tokens)

        if not self.modelo:
            raise LiteLLMConfigurationError(
                "Falta configurar el modelo real para LINKEDIN_CONTENT_AI_ADAPTER=litellm."
            )

    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise LiteLLMConfigurationError("El prompt no puede estar vacío.")

        client = _resolver_litellm()
        if client is None or not callable(getattr(client, "completion", None)):
            raise LiteLLMConfigurationError(
                "La dependencia litellm no está disponible. Instala la dependencia para usar el modo real."
            )

        messages = []
        if system_instruction and system_instruction.strip():
            messages.append({"role": "system", "content": system_instruction.strip()})
        messages.append({"role": "user", "content": prompt.strip()})

        try:
            kwargs = {
                "model": _resolver_modelo(self.modelo, self.proveedor),
                "messages": messages,
                "timeout": self.timeout_seconds,
                "temperature": 0.2,
                "max_tokens": self.max_tokens,
            }
            if self.api_base is not None:
                kwargs["api_base"] = self.api_base

            respuesta = client.completion(**kwargs)
        except Exception as exc:  # pragma: no cover - tests stubbean el proveedor
            if _es_error_de_configuracion(exc, client):
                raise LiteLLMConfigurationError(
                    "No se pudo generar texto por una credencial o configuración inválida del proveedor IA."
                ) from exc
            raise LiteLLMProviderError(
                "No se pudo generar texto por un fallo externo del proveedor IA."
            ) from exc

        contenido = _extraer_texto_respuesta(respuesta).strip()
        if not contenido:
            raise LiteLLMResponseError("El proveedor IA devolvió una respuesta sin contenido utilizable.")
        return contenido
