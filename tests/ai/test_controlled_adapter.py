from linkedin_content_system.ai import ControlledModelAdapter, MockModelAdapter, construir_model_adapter


def _prompt_ejemplo():
    return "\n".join(
        [
            "Texto base original: Aprendi que un flujo simple mejora la utilidad del sistema.",
            "Idea central: Empezar simple mejora la utilidad del sistema",
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
    assert "Empezar simple mejora la utilidad del sistema" in res1
    assert "Que opinas?" in res1


def test_construir_model_adapter_por_defecto_es_controlado():
    adapter = construir_model_adapter()

    assert isinstance(adapter, ControlledModelAdapter)


def test_construir_model_adapter_puede_volver_a_mock(monkeypatch):
    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "mock")

    adapter = construir_model_adapter()

    assert isinstance(adapter, MockModelAdapter)
