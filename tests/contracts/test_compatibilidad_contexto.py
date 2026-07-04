import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.compatibilidad_contexto import ResultadoCompatibilidadContexto


def test_s1_contrato_acepta_resultado_compatible_valido():
    # S1 — Contrato acepta resultado compatible válido.
    resultado = ResultadoCompatibilidadContexto(
        compatible=True,
        estado="PASS",
        motivo="Todo coincide",
        bloqueos=[],
        advertencias=[],
        limites_de_inferencia=["Límite 1"]
    )
    assert resultado.compatible is True
    assert resultado.estado == "PASS"
    assert resultado.motivo == "Todo coincide"


def test_s2_contrato_rechaza_motivo_vacio():
    # S2 — Contrato rechaza motivo vacío.
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="PASS",
            motivo="",
            bloqueos=[],
            advertencias=[],
            limites_de_inferencia=[]
        )
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="PASS",
            motivo="   ",
            bloqueos=[],
            advertencias=[],
            limites_de_inferencia=[]
        )


def test_s3_contrato_rechaza_estado_invalido():
    # S3 — Contrato rechaza estado inválido.
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="INVALID_STATE",  # type: ignore
            motivo="Estado incorrecto",
            bloqueos=[],
            advertencias=[],
            limites_de_inferencia=[]
        )


def test_s4_contrato_rechaza_strings_vacios_en_listas():
    # S4 — Contrato rechaza strings vacíos en listas.
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="PASS",
            motivo="Ok",
            bloqueos=[""],
            advertencias=[],
            limites_de_inferencia=[]
        )
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="PASS",
            motivo="Ok",
            bloqueos=[],
            advertencias=["   "],
            limites_de_inferencia=[]
        )


def test_s5_contrato_rechaza_estado_bloqueado_con_compatible_true():
    # S5 — Contrato rechaza estado BLOQUEADO con compatible=True.
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=True,
            estado="BLOQUEADO",
            motivo="Bloqueado pero compatible True",
            bloqueos=["Error"],
            advertencias=[],
            limites_de_inferencia=[]
        )


def test_s6_contrato_rechaza_compatible_false_sin_bloqueos():
    # S6 — Contrato rechaza compatible=False sin bloqueos.
    with pytest.raises(ValidationError):
        ResultadoCompatibilidadContexto(
            compatible=False,
            estado="BLOQUEADO",
            motivo="Bloqueado pero sin lista de bloqueos",
            bloqueos=[],
            advertencias=[],
            limites_de_inferencia=[]
        )
