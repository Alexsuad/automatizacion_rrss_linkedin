import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.diagnostico_base_editorial import DiagnosticoBaseEditorial


def test_contrato_diagnostico_editorial_valido():
    # S1: Contrato acepta diagnóstico válido
    diag = DiagnosticoBaseEditorial(
        estado="PASS",
        resumen="Base editorial suficiente",
        hallazgos=["Idea bien explicada"],
        bloqueos=[],
        recomendaciones=["Ninguna"],
        limites_de_inferencia=["Límite local V0"]
    )
    assert diag.estado == "PASS"
    assert diag.resumen == "Base editorial suficiente"
    assert diag.hallazgos == ["Idea bien explicada"]
    assert diag.bloqueos == []
    assert diag.recomendaciones == ["Ninguna"]
    assert diag.limites_de_inferencia == ["Límite local V0"]


def test_contrato_rechaza_resumen_vacio():
    # S2: Contrato rechaza resumen vacío o con solo espacios
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="",
            hallazgos=[]
        )
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="   ",
            hallazgos=[]
        )


def test_contrato_rechaza_estado_invalido():
    # S3: Contrato rechaza estado inválido
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="OTRO_ESTADO",  # type: ignore
            resumen="Resumen válido",
            hallazgos=[]
        )


def test_contrato_rechaza_strings_vacios_dentro_de_listas():
    # S4: Contrato rechaza strings vacíos dentro de listas
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="Resumen válido",
            hallazgos=[""]
        )
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="Resumen válido",
            hallazgos=["   "]
        )
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="Resumen válido",
            bloqueos=[""]
        )
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="Resumen válido",
            recomendaciones=[""]
        )
    with pytest.raises(ValidationError):
        DiagnosticoBaseEditorial(
            estado="PASS",
            resumen="Resumen válido",
            limites_de_inferencia=[""]
        )
