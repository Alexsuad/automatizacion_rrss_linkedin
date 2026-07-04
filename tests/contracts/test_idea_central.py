import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.idea_central import IdeaCentral


def test_contrato_idea_central_valido():
    idea = IdeaCentral(
        idea_central="IA offline local",
        resumen_operativo="Extractor determinista inicial",
        puntos_de_soporte=["Primer punto clave"],
        limites_de_inferencia=["Límite de inferencia 1"]
    )
    assert idea.idea_central == "IA offline local"
    assert idea.puntos_de_soporte == ["Primer punto clave"]


def test_contrato_rechaza_idea_central_vacia():
    # S7: El contrato rechaza idea_central vacía
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="",
            resumen_operativo="Resumen",
            puntos_de_soporte=["Soporte"]
        )
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="   ",
            resumen_operativo="Resumen",
            puntos_de_soporte=["Soporte"]
        )


def test_contrato_rechaza_resumen_operativo_vacio():
    # S8: El contrato rechaza resumen_operativo vacío
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="",
            puntos_de_soporte=["Soporte"]
        )
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="   ",
            puntos_de_soporte=["Soporte"]
        )


def test_contrato_rechaza_puntos_de_soporte_vacio():
    # S9: El contrato rechaza puntos_de_soporte vacío o con elementos vacíos
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="Resumen",
            puntos_de_soporte=[]
        )
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="Resumen",
            puntos_de_soporte=[""]
        )


def test_contrato_rechaza_limites_de_inferencia_con_elementos_vacios():
    # Si limites_de_inferencia trae elementos, ninguno puede estar vacío
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="Resumen",
            puntos_de_soporte=["Soporte"],
            limites_de_inferencia=[""]
        )
    with pytest.raises(ValidationError):
        IdeaCentral(
            idea_central="Idea",
            resumen_operativo="Resumen",
            puntos_de_soporte=["Soporte"],
            limites_de_inferencia=["   "]
        )
