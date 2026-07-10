from types import SimpleNamespace

import pytest

import linkedin_content_system.ai.litellm_adapter as litellm_adapter_module
from linkedin_content_system.ai import LiteLLMAdapterError, LiteLLMModelAdapter


class _FakeLiteLLM:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def completion(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_litellm_adapter_convierte_respuesta_y_configuracion(monkeypatch):
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Borrador real util"))]
    )
    fake_litellm = _FakeLiteLLM(fake_response)
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai", timeout_seconds=12.5)
    resultado = adapter.generar_texto("Prompt base", system_instruction="Tono claro")

    assert resultado == "Borrador real util"
    assert fake_litellm.calls == [
        {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Tono claro"},
                {"role": "user", "content": "Prompt base"},
            ],
            "timeout": 12.5,
            "temperature": 0.2,
        }
    ]


def test_litellm_adapter_rechaza_configuracion_incompleta():
    with pytest.raises(LiteLLMAdapterError, match="Falta configurar el modelo real"):
        LiteLLMModelAdapter(modelo="", proveedor="openai")


def test_litellm_adapter_traduce_error_sin_exponer_prompt(monkeypatch):
    class _BoomLiteLLM:
        def completion(self, **kwargs):
            raise RuntimeError("boom secreto")

    monkeypatch.setattr(litellm_adapter_module, "litellm", _BoomLiteLLM())

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMAdapterError, match="No se pudo generar texto"):
        adapter.generar_texto("Prompt con secreto SUPER_SECRETO", system_instruction="SYS")
