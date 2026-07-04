import pytest
from linkedin_content_system.ai import MockModelAdapter


def test_mock_adapter_retorna_respuesta_determinista():
    adapter = MockModelAdapter()
    prompt = "Automatización en LinkedIn offline"

    res1 = adapter.generar_texto(prompt, system_instruction="Tono formal")
    res2 = adapter.generar_texto(prompt, system_instruction="Tono formal")

    assert res1 == res2
    assert "[BORRADOR SIMULADO DE POST]" in res1


def test_mock_adapter_incluye_parte_del_prompt():
    adapter = MockModelAdapter()
    prompt = "Contenido clave de prueba"

    resultado = adapter.generar_texto(prompt)
    assert "Contenido clave de prueba" in resultado


def test_mock_adapter_soporta_system_instruction_vacio_y_none():
    adapter = MockModelAdapter()
    prompt = "Contenido básico"

    res_none = adapter.generar_texto(prompt, system_instruction=None)
    res_empty = adapter.generar_texto(prompt, system_instruction="")
    res_spaces = adapter.generar_texto(prompt, system_instruction="   ")

    assert "Contexto de sistema recibido: no" in res_none
    assert "Contexto de sistema recibido: no" in res_empty
    assert "Contexto de sistema recibido: no" in res_spaces


def test_mock_adapter_rechaza_entrada_vacia():
    adapter = MockModelAdapter()
    with pytest.raises(ValueError, match="El prompt no puede estar vacío."):
        adapter.generar_texto("")
    with pytest.raises(ValueError, match="El prompt no puede estar vacío."):
        adapter.generar_texto("   ")


def test_mock_adapter_no_requiere_configuracion_externa():
    # El test valida que el adaptador mock no requiera llaves ni de inicialización de red
    adapter = MockModelAdapter()
    res = adapter.generar_texto("Prueba de red offline")
    assert res is not None


def test_mock_adapter_no_expone_system_instruction_completa():
    adapter = MockModelAdapter()

    resultado = adapter.generar_texto(
        "Prompt válido",
        system_instruction="INSTRUCCION_INTERNA_SECRETA_NO_DEBE_SALIR",
    )

    assert "Contexto de sistema recibido: sí" in resultado
    assert "INSTRUCCION_INTERNA_SECRETA_NO_DEBE_SALIR" not in resultado

