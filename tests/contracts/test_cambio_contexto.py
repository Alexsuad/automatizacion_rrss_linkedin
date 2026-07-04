import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.cambio_contexto import ResultadoCambioContexto


def test_contrato_acepta_resultado_valido():
    # S1 — Contrato acepta resultado válido.
    res = ResultadoCambioContexto(
        puede_cambiar=True,
        estado="PASS",
        motivo="Cambio justificado",
        requiere_limpieza_manual=False,
        advertencias=["advertencia 1"],
        bloqueos=[],
        limites_de_inferencia=["límite 1"]
    )
    assert res.puede_cambiar is True
    assert res.estado == "PASS"
    assert res.motivo == "Cambio justificado"
    assert res.requiere_limpieza_manual is False
    assert res.advertencias == ["advertencia 1"]
    assert res.bloqueos == []
    assert res.limites_de_inferencia == ["límite 1"]


def test_contrato_rechaza_motivo_vacio():
    # S2 — Contrato rechaza motivo vacío.
    with pytest.raises(ValidationError):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="PASS",
            motivo="",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=[],
            limites_de_inferencia=[]
        )
    with pytest.raises(ValidationError):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="PASS",
            motivo="   ",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=[],
            limites_de_inferencia=[]
        )


def test_contrato_rechaza_estado_invalido():
    # S3 — Contrato rechaza estado inválido.
    with pytest.raises(ValidationError):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="INVALIDO",  # type: ignore
            motivo="Cambio justificado",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=[],
            limites_de_inferencia=[]
        )


def test_contrato_rechaza_strings_vacios_en_listas():
    # S4 — Contrato rechaza strings vacíos en listas.
    with pytest.raises(ValidationError):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="PASS",
            motivo="Cambio",
            requiere_limpieza_manual=False,
            advertencias=[""],
            bloqueos=[],
            limites_de_inferencia=[]
        )
    with pytest.raises(ValidationError):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="PASS",
            motivo="Cambio",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=["   "],
            limites_de_inferencia=[]
        )


def test_contrato_rechaza_bloqueado_con_puede_cambiar_true():
    # S5 — Contrato rechaza estado BLOQUEADO con puede_cambiar=True.
    with pytest.raises(ValidationError, match="puede_cambiar debe ser False"):
        ResultadoCambioContexto(
            puede_cambiar=True,
            estado="BLOQUEADO",
            motivo="Cambio no confirmado",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=["Falta confirmación"],
            limites_de_inferencia=[]
        )


def test_contrato_rechaza_puede_cambiar_false_sin_bloqueos():
    # S6 — Contrato rechaza puede_cambiar=False sin bloqueos.
    with pytest.raises(ValidationError, match="debe existir al menos un bloqueo"):
        ResultadoCambioContexto(
            puede_cambiar=False,
            estado="PASS",
            motivo="Cambio",
            requiere_limpieza_manual=False,
            advertencias=[],
            bloqueos=[],
            limites_de_inferencia=[]
        )
