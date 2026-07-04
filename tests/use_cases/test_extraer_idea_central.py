import os
import pytest
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.use_cases import extraer_idea_central


def test_extraer_idea_central_texto_valido_produce_idea_central():
    # S1: Texto válido produce IdeaCentral válida
    res = extraer_idea_central("Mi nota de voz sobre automatización")
    assert isinstance(res, IdeaCentral)
    assert res.idea_central == "Mi nota de voz sobre automatización"


def test_extraer_idea_central_texto_vacio_lanza_error():
    # S2: Texto vacío o con espacios lanza ValueError
    with pytest.raises(ValueError, match="El texto base no puede estar vacío."):
        extraer_idea_central("")
    with pytest.raises(ValueError, match="El texto base no puede estar vacío."):
        extraer_idea_central("   ")


def test_extraer_idea_central_conserva_contenido_del_texto():
    # S3: La idea central conserva contenido derivado del texto base (acotado a 280)
    texto_largo = "A" * 500
    res = extraer_idea_central(texto_largo)
    assert len(res.idea_central) == 280
    assert res.idea_central == "A" * 280


def test_extraer_idea_central_incluye_punto_de_soporte():
    # S4: El resultado incluye al menos un punto de soporte
    res = extraer_idea_central("Concepto clave")
    assert len(res.puntos_de_soporte) >= 1
    assert res.puntos_de_soporte[0] == "Concepto clave"


def test_extraer_idea_central_incluye_limites_de_inferencia_como_lista():
    # S5: El resultado incluye limites_de_inferencia como lista
    res = extraer_idea_central("Texto básico")
    assert isinstance(res.limites_de_inferencia, list)
    assert len(res.limites_de_inferencia) >= 1


def test_extraer_idea_central_sin_efectos_secundarios_de_disco(tmp_path):
    # S6: El caso de uso no escribe archivos ni tiene efectos secundarios
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = extraer_idea_central("Texto limpio")
        assert res is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_extraer_idea_central_es_determinista():
    # S10: Dos ejecuciones idénticas producen la misma IdeaCentral
    texto = "Texto para evaluar determinismo"
    res1 = extraer_idea_central(texto)
    res2 = extraer_idea_central(texto)
    assert res1 == res2
