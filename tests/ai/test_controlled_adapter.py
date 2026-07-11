import pytest

from linkedin_content_system.ai import (
    ControlledModelAdapter,
    LiteLLMConfigurationError,
    LiteLLMModelAdapter,
    MockModelAdapter,
    construir_model_adapter,
)


def _prompt_ejemplo():
    return "\n".join(
        [
            "Texto base original: Aprendi que un flujo simple mejora la utilidad del sistema.",
            "Idea central: Empezar simple mejora la utilidad del sistema",
            "Idea explicita del usuario: La utilidad real empieza con un flujo simple y seguro",
            "Resumen de intencion: compartir_aprendizaje",
            "Perfil narrativo de referencia: perfil_fundador",
            "Audiencia objetivo: equipos pequenos B2B",
            "Objetivo del post: explicar una idea operativa",
            "CTA deseado: Que opinas",
        ]
    )


def test_controlled_adapter_genera_texto_util_y_determinista():
    adapter = ControlledModelAdapter()
    prompt = _prompt_ejemplo()

    res1 = adapter.generar_texto(prompt)
    res2 = adapter.generar_texto(prompt)

    assert res1 == res2
    assert "[BORRADOR SIMULADO DE POST]" not in res1
    assert "La utilidad real empieza con un flujo simple y seguro" in res1
    assert "La intencion editorial resumida es compartir_aprendizaje" in res1
    assert "Que opinas?" in res1


def test_construir_model_adapter_por_defecto_es_controlado():
    adapter = construir_model_adapter()

    assert isinstance(adapter, ControlledModelAdapter)


def test_construir_model_adapter_puede_volver_a_mock(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "mock")

    adapter = construir_model_adapter()

    assert isinstance(adapter, MockModelAdapter)


def test_construir_model_adapter_puede_ir_a_litellm(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "litellm")
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_PROVIDER", "openai")

    from linkedin_content_system.ai import litellm_adapter as litellm_adapter_module

    class _FakeLiteLLM:
        def completion(self, **kwargs):
            return {"choices": [{"message": {"content": "respuesta real simulada"}}]}

    monkeypatch.setattr(litellm_adapter_module, "litellm", _FakeLiteLLM())

    adapter = construir_model_adapter()

    assert isinstance(adapter, LiteLLMModelAdapter)
    assert adapter.generar_texto("Prompt base") == "respuesta real simulada"


def test_construir_model_adapter_puede_leer_api_base_para_ollama(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "litellm")
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_MODEL", "ollama_chat/llama3.2:latest")
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_API_BASE", "http://windows-host.local:11434")

    from linkedin_content_system.ai import litellm_adapter as litellm_adapter_module

    class _FakeLiteLLM:
        def __init__(self):
            self.calls = []

        def completion(self, **kwargs):
            self.calls.append(kwargs)
            return {"choices": [{"message": {"content": "respuesta local"}}]}

    fake_litellm = _FakeLiteLLM()
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = construir_model_adapter()

    assert isinstance(adapter, LiteLLMModelAdapter)
    assert adapter.generar_texto("Prompt base") == "respuesta local"
    assert fake_litellm.calls[0]["api_base"] == "http://windows-host.local:11434"


def test_construir_model_adapter_rechaza_modo_desconocido(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "desconocido")

    with pytest.raises(ValueError, match="Modo de adaptador desconocido"):
        construir_model_adapter()


def test_construir_model_adapter_litellm_falla_si_configuracion_incompleta(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "litellm")
    monkeypatch.delenv("LINKEDIN_CONTENT_AI_MODEL", raising=False)

    with pytest.raises(LiteLLMConfigurationError, match="Falta configurar el modelo real"):
        construir_model_adapter()
