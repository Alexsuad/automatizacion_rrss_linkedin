import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts import IntencionEditorialClasificada


def test_contrato_intencion_editorial_clasificada_valido():
    # S1 — contrato acepta una intención válida.
    clasificacion = IntencionEditorialClasificada(
        intencion_principal="compartir_aprendizaje",
        resumen_intencion="Resumen de intención válido",
        justificacion="La justificación de la clasificación es requerida.",
        confianza="alta",
        limites_de_inferencia=["Límite de inferencia 1"]
    )
    assert clasificacion.intencion_principal == "compartir_aprendizaje"
    assert clasificacion.confianza == "alta"


def test_contrato_rechaza_resumen_intencion_vacio():
    # S2 — rechaza resumen_intencion vacío o compuesto solo por espacios.
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="explicar_idea",
            resumen_intencion="",
            justificacion="Justificación válida"
        )
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="explicar_idea",
            resumen_intencion="   ",
            justificacion="Justificación válida"
        )


def test_contrato_rechaza_justificacion_vacia():
    # S3 — rechaza justificacion vacía o compuesta solo por espacios.
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="posicionar_opinion",
            resumen_intencion="Resumen válido",
            justificacion=""
        )
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="posicionar_opinion",
            resumen_intencion="Resumen válido",
            justificacion="   "
        )


def test_contrato_rechaza_limites_vacios():
    # S4 — rechaza limites_de_inferencia con elementos vacíos.
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="contar_experiencia",
            resumen_intencion="Resumen",
            justificacion="Justificación",
            limites_de_inferencia=[""]
        )
    with pytest.raises(ValidationError):
        IntencionEditorialClasificada(
            intencion_principal="contar_experiencia",
            resumen_intencion="Resumen",
            justificacion="Justificación",
            limites_de_inferencia=["   "]
        )


def test_contrato_permite_limites_vacios_como_lista():
    # S5 — permite limites_de_inferencia vacío como lista.
    clasificacion = IntencionEditorialClasificada(
        intencion_principal="abrir_conversacion",
        resumen_intencion="Resumen",
        justificacion="Justificación",
        limites_de_inferencia=[]
    )
    assert len(clasificacion.limites_de_inferencia) == 0
