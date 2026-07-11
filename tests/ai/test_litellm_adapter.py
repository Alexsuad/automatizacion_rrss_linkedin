from types import SimpleNamespace

import pytest

import linkedin_content_system.ai.litellm_adapter as litellm_adapter_module
from linkedin_content_system.ai import (
    LiteLLMAdapterError,
    LiteLLMConfigurationError,
    LiteLLMModelAdapter,
    LiteLLMProviderError,
    LiteLLMResponseError,
)


class _FakeLiteLLM:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def completion(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


def test_litellm_adapter_envia_max_tokens_por_defecto(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")
    resultado = adapter.generar_texto("Prompt base", system_instruction="Tono claro")

    assert resultado == "Borrador real util"
    assert fake_litellm.calls[0]["model"] == "openai/gpt-4o-mini"
    assert fake_litellm.calls[0]["max_tokens"] == 280
    assert fake_litellm.calls[0]["timeout"] == 30.0


def test_litellm_adapter_envia_max_tokens_personalizado(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = LiteLLMModelAdapter(
        modelo="gpt-4o-mini",
        proveedor="openai",
        timeout_seconds=12.5,
        max_tokens=123,
    )
    adapter.generar_texto("Prompt base", system_instruction="Tono claro")

    assert fake_litellm.calls == [
        {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Tono claro"},
                {"role": "user", "content": "Prompt base"},
            ],
            "timeout": 12.5,
            "temperature": 0.2,
            "max_tokens": 123,
        }
    ]


def test_litellm_adapter_usa_max_tokens_desde_entorno(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_MAX_TOKENS", "111")

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")
    adapter.generar_texto("Prompt base")

    assert fake_litellm.calls[0]["max_tokens"] == 111


def test_litellm_adapter_usa_api_base_desde_entorno(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    monkeypatch.setenv("OLLAMA_API_BASE", "http://windows-host.local:11434")

    adapter = LiteLLMModelAdapter(modelo="ollama_chat/llama3.2:latest", proveedor="ollama")
    adapter.generar_texto("Prompt base")

    assert fake_litellm.calls[0]["api_base"] == "http://windows-host.local:11434"
    assert fake_litellm.calls[0]["model"] == "ollama_chat/llama3.2:latest"


def test_litellm_adapter_usa_override_general_desde_entorno(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_API_BASE", "http://api-base-general.local:11434")
    monkeypatch.setenv("OLLAMA_API_BASE", "http://ollama-local.example:11434")

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")
    adapter.generar_texto("Prompt base")

    assert fake_litellm.calls[0]["api_base"] == "http://api-base-general.local:11434"


def test_litellm_adapter_da_prioridad_al_api_base_explicito_sobre_entorno(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_API_BASE", "http://api-base-general.local:11434")
    monkeypatch.setenv("OLLAMA_API_BASE", "http://ollama-local.example:11434")

    adapter = LiteLLMModelAdapter(
        modelo="ollama_chat/llama3.2:latest",
        proveedor="ollama",
        api_base="http://api-base-explicito.local:11434",
    )
    adapter.generar_texto("Prompt base")

    assert fake_litellm.calls[0]["api_base"] == "http://api-base-explicito.local:11434"


@pytest.mark.parametrize(
    ("proveedor", "modelo"),
    [
        ("deepseek", "deepseek-chat"),
        ("openrouter", "openrouter/deepseek/deepseek-v3"),
        ("openai", "gpt-4o-mini"),
    ],
)
def test_litellm_adapter_ignora_ollama_api_base_para_otros_proveedores(
    proveedor,
    modelo,
    monkeypatch,
):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador real util"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    monkeypatch.setenv("OLLAMA_API_BASE", "http://windows-host.local:11434")

    adapter = LiteLLMModelAdapter(modelo=modelo, proveedor=proveedor)
    adapter.generar_texto("Prompt base")

    assert "api_base" not in fake_litellm.calls[0]
    assert fake_litellm.calls[0]["model"] == litellm_adapter_module._resolver_modelo(modelo, proveedor)


def test_litellm_adapter_resuelve_modelo_prefijado():
    assert litellm_adapter_module._resolver_modelo("openai/gpt-4o-mini", "openai") == "openai/gpt-4o-mini"


def test_litellm_adapter_acepta_respuesta_objeto(monkeypatch):
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Borrador tipo objeto"))]
    )
    fake_litellm = _FakeLiteLLM(fake_response)
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    assert adapter.generar_texto("Prompt base") == "Borrador tipo objeto"


def test_litellm_adapter_acepta_respuesta_diccionario(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "Borrador tipo dict"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)

    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    assert adapter.generar_texto("Prompt base") == "Borrador tipo dict"


@pytest.mark.parametrize(
    ("kwargs", "regex"),
    [
        ({"modelo": "", "proveedor": "openai"}, "Falta configurar el modelo real"),
        ({"modelo": "gpt-4o-mini", "proveedor": "openai", "timeout_seconds": 0}, "timeout"),
        ({"modelo": "gpt-4o-mini", "proveedor": "openai", "max_tokens": 0}, "max_tokens"),
        ({"modelo": "gpt-4o-mini", "proveedor": "openai", "max_tokens": -5}, "max_tokens"),
    ],
)
def test_litellm_adapter_rechaza_configuracion_invalida(kwargs, regex):
    with pytest.raises(LiteLLMConfigurationError, match=regex):
        LiteLLMModelAdapter(**kwargs)


def test_litellm_adapter_rechaza_prompt_vacio(monkeypatch):
    fake_litellm = _FakeLiteLLM({"choices": [{"message": {"content": "No debe usarse"}}]})
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMConfigurationError, match="prompt no puede estar vac"):
        adapter.generar_texto("   ")

    assert fake_litellm.calls == []


def test_litellm_adapter_rechaza_max_tokens_invalido_desde_entorno(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_MAX_TOKENS", "ciento")

    with pytest.raises(LiteLLMConfigurationError, match="max_tokens"):
        LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")


@pytest.mark.parametrize("api_base", ["ftp://localhost:11434", "localhost:11434", "://malformed"])
def test_litellm_adapter_rechaza_api_base_invalido(api_base):
    with pytest.raises(LiteLLMConfigurationError, match="api_base"):
        LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai", api_base=api_base)


@pytest.mark.parametrize(
    ("env_var", "modelo", "proveedor"),
    [
        ("OLLAMA_API_BASE", "ollama_chat/llama3.2:latest", "ollama"),
        ("LINKEDIN_CONTENT_AI_API_BASE", "gpt-4o-mini", "deepseek"),
        ("LINKEDIN_CONTENT_AI_API_BASE", "gpt-4o-mini", "openrouter"),
    ],
)
def test_litellm_adapter_rechaza_api_base_invalido_desde_entorno(env_var, modelo, proveedor, monkeypatch):
    monkeypatch.setenv(env_var, "localhost:11434")

    with pytest.raises(LiteLLMConfigurationError, match="api_base"):
        LiteLLMModelAdapter(modelo=modelo, proveedor=proveedor)


def test_litellm_adapter_rechaza_litellm_ausente(monkeypatch):
    monkeypatch.setattr(litellm_adapter_module, "litellm", None)
    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMConfigurationError, match="dependencia litellm no est"):
        adapter.generar_texto("Prompt base")


def test_litellm_adapter_traduce_error_de_autenticacion(monkeypatch):
    fake_litellm = _FakeLiteLLM(error=RuntimeError("authentication failed for token SENSITIVE_VALUE"))
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMConfigurationError, match="credencial o configuraci"):
        adapter.generar_texto("Prompt base", system_instruction="SYS")


def test_litellm_adapter_traduce_error_externo_sin_exponer_secretos(monkeypatch):
    fake_litellm = _FakeLiteLLM(error=RuntimeError("rate limit on SECRET_TOKEN"))
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMProviderError) as excinfo:
        adapter.generar_texto("Prompt con SUPER_SECRETO", system_instruction="SYS_INTERNA")

    mensaje = str(excinfo.value)
    assert "SECRET_TOKEN" not in mensaje
    assert "SUPER_SECRETO" not in mensaje
    assert "SYS_INTERNA" not in mensaje


@pytest.mark.parametrize(
    "respuesta",
    [
        {},
        {"choices": []},
        {"choices": [{"message": {"content": ""}}]},
        SimpleNamespace(choices=[]),
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=""))]),
    ],
)
def test_litellm_adapter_rechaza_respuesta_vacia(respuesta, monkeypatch):
    fake_litellm = _FakeLiteLLM(respuesta)
    monkeypatch.setattr(litellm_adapter_module, "litellm", fake_litellm)
    adapter = LiteLLMModelAdapter(modelo="gpt-4o-mini", proveedor="openai")

    with pytest.raises(LiteLLMResponseError, match="contenido utilizable|respuesta"):
        adapter.generar_texto("Prompt base")


def test_litellm_adapter_base_error_sigue_siendo_runtime_error():
    assert issubclass(LiteLLMAdapterError, RuntimeError)
