import pytest
from unittest.mock import patch
from linkedin_content_system.contracts.validacion_aprobacion_humana import DecisionAprobacionHumana
from linkedin_content_system.use_cases.validar_aprobacion_humana import validar_aprobacion_humana


def test_s5_estado_pendiente_no_avanza():
    # S5 — Estado pendiente no avanza.
    aprobacion = DecisionAprobacionHumana(estado="pendiente")
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
    assert resultado.puede_avanzar is False
    assert resultado.requiere_revision_adicional is True
    assert resultado.estado_publicabilidad == "no_publicable"
    assert "pendiente" in resultado.motivo


def test_s6_estado_rechazado_no_avanza():
    # S6 — Estado rechazado no avanza.
    aprobacion = DecisionAprobacionHumana(estado="rechazado", motivo="No cumple lineamientos")
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
    assert resultado.puede_avanzar is False
    assert resultado.requiere_revision_adicional is False
    assert resultado.estado_publicabilidad == "no_publicable"
    assert resultado.motivo == "No cumple lineamientos"


def test_s7_aprobado_simple_avanza_si_no_requiere_reforzada():
    # S7 — Aprobado simple avanza si no requiere reforzada.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_simple")
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
    assert resultado.puede_avanzar is True
    assert resultado.requiere_revision_adicional is False
    assert resultado.estado_publicabilidad == "publicable_con_aprobacion_simple"
    assert "simple" in resultado.motivo


def test_s8_aprobado_simple_no_avanza_si_requiere_reforzada():
    # S8 — Aprobado simple no avanza si requiere reforzada.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_simple")
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=True)
    assert resultado.puede_avanzar is False
    assert resultado.requiere_revision_adicional is True
    assert resultado.estado_publicabilidad == "no_publicable"
    assert "reforzada" in resultado.motivo


def test_s9_aprobado_reforzado_avanza_con_confirmacion_explicita():
    # S9 — Aprobado reforzado avanza con confirmación explícita.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_reforzado", confirmacion_explicita=True)
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
    assert resultado.puede_avanzar is True
    assert resultado.requiere_revision_adicional is False
    assert resultado.estado_publicabilidad == "publicable_con_aprobacion_reforzada"
    assert "reforzada" in resultado.motivo


def test_s10_aprobado_reforzado_no_avanza_sin_confirmacion_explicita():
    # S10 — Aprobado reforzado no avanza sin confirmación explícita.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_reforzado", confirmacion_explicita=False)
    resultado = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
    assert resultado.puede_avanzar is False
    assert resultado.requiere_revision_adicional is True
    assert resultado.estado_publicabilidad == "no_publicable"
    assert "confirmación" in resultado.motivo


def test_s11_rechaza_aprobacion_none():
    # S11 — Rechaza aprobacion None.
    with pytest.raises(ValueError, match="aprobacion no puede ser None"):
        validar_aprobacion_humana(None, requiere_aprobacion_reforzada=False)


def test_s12_no_escribe_archivos():
    # S12 — No escribe archivos.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_simple")
    with patch("builtins.open") as mock_open:
        validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=False)
        mock_open.assert_not_called()


def test_s13_es_determinista():
    # S13 — Es determinista.
    aprobacion = DecisionAprobacionHumana(estado="aprobado_reforzado", confirmacion_explicita=True)
    
    res1 = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=True)
    res2 = validar_aprobacion_humana(aprobacion, requiere_aprobacion_reforzada=True)
    
    assert res1.puede_avanzar == res2.puede_avanzar
    assert res1.requiere_revision_adicional == res2.requiere_revision_adicional
    assert res1.estado_publicabilidad == res2.estado_publicabilidad
    assert res1.motivo == res2.motivo

