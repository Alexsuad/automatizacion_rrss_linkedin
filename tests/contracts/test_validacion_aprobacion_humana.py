import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.validacion_aprobacion_humana import (
    DecisionAprobacionHumana,
    ResultadoValidacionAprobacionHumana,
)


def test_s1_contrato_aprobacion_humana_acepta_estado_valido():
    # S1 — Contrato DecisionAprobacionHumana acepta estado válido.
    for estado in ["pendiente", "aprobado_simple", "aprobado_reforzado", "rechazado"]:
        aprobacion = DecisionAprobacionHumana(
            estado=estado,
            revisor="Juan Pérez",
            motivo="Todo correcto",
            confirmacion_explicita=True
        )
        assert aprobacion.estado == estado
        assert aprobacion.revisor == "Juan Pérez"
        assert aprobacion.motivo == "Todo correcto"
        assert aprobacion.confirmacion_explicita is True


def test_s2_contrato_aprobacion_humana_rechaza_estado_invalido():
    # S2 — Contrato DecisionAprobacionHumana rechaza estado inválido.
    with pytest.raises(ValidationError):
        DecisionAprobacionHumana(estado="invalido")


def test_s3_contrato_resultado_aprobacion_humana_acepta_resultado_valido():
    # S3 — Contrato ResultadoValidacionAprobacionHumana acepta resultado válido.
    resultado = ResultadoValidacionAprobacionHumana(
        puede_avanzar=True,
        requiere_revision_adicional=False,
        estado_publicabilidad="publicable_con_aprobacion_simple",
        motivo="Aprobación simple exitosa"
    )
    assert resultado.puede_avanzar is True
    assert resultado.requiere_revision_adicional is False
    assert resultado.estado_publicabilidad == "publicable_con_aprobacion_simple"
    assert resultado.motivo == "Aprobación simple exitosa"


def test_s4_contrato_resultado_aprobacion_humana_rechaza_motivo_vacio():
    # S4 — Contrato ResultadoValidacionAprobacionHumana rechaza motivo vacío.
    with pytest.raises(ValidationError):
        ResultadoValidacionAprobacionHumana(
            puede_avanzar=True,
            requiere_revision_adicional=False,
            estado_publicabilidad="publicable_con_aprobacion_simple",
            motivo=""
        )
    with pytest.raises(ValidationError):
        ResultadoValidacionAprobacionHumana(
            puede_avanzar=True,
            requiere_revision_adicional=False,
            estado_publicabilidad="publicable_con_aprobacion_simple",
            motivo="   "
        )


def test_contrato_aprobacion_humana_rechaza_revisor_vacio():
    # Revisor no puede ser string vacío si se proporciona
    with pytest.raises(ValidationError):
        DecisionAprobacionHumana(estado="pendiente", revisor="")
    with pytest.raises(ValidationError):
        DecisionAprobacionHumana(estado="pendiente", revisor="   ")


def test_contrato_aprobacion_humana_rechaza_motivo_vacio():
    # Motivo no puede ser string vacío si se proporciona
    with pytest.raises(ValidationError):
        DecisionAprobacionHumana(estado="pendiente", motivo="")
    with pytest.raises(ValidationError):
        DecisionAprobacionHumana(estado="pendiente", motivo="   ")
