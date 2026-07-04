import os
import pytest
from linkedin_content_system.ai import MockModelAdapter
from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.use_cases import generar_post_mock


def test_generar_post_mock_es_determinista():
    # S1: Dado un texto base válido, genera el mismo resultado con el mismo adapter
    adapter = MockModelAdapter()
    texto = "Nota de voz sobre automatización offline"
    
    res1 = generar_post_mock(texto, adapter)
    res2 = generar_post_mock(texto, adapter)
    
    assert res1 == res2
    assert "[BORRADOR SIMULADO DE POST]" in res1


def test_generar_post_mock_usa_adapter_inyectado():
    # S2: Valida que delegue en la interfaz ModelAdapter inyectada
    class FakeAdapter(ModelAdapter):
        def __init__(self):
            self.llamado = False
            self.prompt_recibido = None
            
        def generar_texto(self, prompt: str, system_instruction: str = None) -> str:
            self.llamado = True
            self.prompt_recibido = prompt
            return "respuesta fake"
            
    spy = FakeAdapter()
    res = generar_post_mock("Prueba inyeccion", spy)
    
    assert spy.llamado is True
    assert spy.prompt_recibido == "Prueba inyeccion"
    assert res == "respuesta fake"


def test_generar_post_mock_rechaza_texto_vacio():
    # S3: Rechazo de entradas vacías
    adapter = MockModelAdapter()
    with pytest.raises(ValueError, match="El texto base no puede estar vacío."):
        generar_post_mock("", adapter)
    with pytest.raises(ValueError, match="El texto base no puede estar vacío."):
        generar_post_mock("   ", adapter)


def test_generar_post_mock_rechaza_adapter_none():
    with pytest.raises(ValueError, match="El adapter no puede ser None."):
        generar_post_mock("Texto válido", None)


def test_generar_post_mock_no_crea_archivos(tmp_path):
    # S4: Validar que no tenga efectos secundarios de persistencia en disco
    adapter = MockModelAdapter()
    cwd_inicial = os.getcwd()
    
    # Nos movemos a tmp_path para ver que no cree archivos allí
    os.chdir(tmp_path)
    try:
        res = generar_post_mock("Texto de prueba sin archivos", adapter)
        assert res is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos de forma inesperada: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_generar_post_mock_conserva_trazabilidad_minima():
    # S6: El resultado conserva una referencia al texto de origen
    adapter = MockModelAdapter()
    texto = "Automatización y soberanía en sistemas agénticos"
    
    res = generar_post_mock(texto, adapter)
    assert "Automatización y soberanía" in res

