import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.evidencia_contexto_usado import EvidenciaContextoUsado


def test_contrato_evidencia_contexto_usado_valido():
    # S1: Contrato acepta evidencia válida
    ev = EvidenciaContextoUsado(
        id_evidencia="ev_12345",
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        nombre_operacion="Validar Contexto",
        resultado_operacion="PASS",
        datos_reales_permitidos=False,
        fuentes_autorizadas=["doc1.txt"],
        artefactos_generados=["art1.json"],
        advertencias=["advertencia 1"],
        bloqueos=[],
        limites_de_inferencia=["límite 1"]
    )
    assert ev.id_evidencia == "ev_12345"
    assert ev.contexto_id == "ctx_123"
    assert ev.cliente_id == "cliente_a"
    assert ev.superficie == "linkedin_personal"
    assert ev.campaña == "Q3_Launch"
    assert ev.nombre_operacion == "Validar Contexto"
    assert ev.resultado_operacion == "PASS"
    assert ev.datos_reales_permitidos is False
    assert ev.fuentes_autorizadas == ["doc1.txt"]
    assert ev.artefactos_generados == ["art1.json"]
    assert ev.advertencias == ["advertencia 1"]
    assert ev.bloqueos == []
    assert ev.limites_de_inferencia == ["límite 1"]


def test_contrato_rechaza_id_evidencia_vacio():
    # S2: Contrato rechaza id_evidencia vacío
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_contexto_id_vacio():
    # S3: Contrato rechaza contexto_id vacío
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_cliente_id_vacio():
    # S4: Contrato rechaza cliente_id vacío
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_superficie_invalida():
    # S5: Contrato rechaza superficie inválida
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_grupo",  # type: ignore
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_campaña_vacia_si_se_proporciona():
    # S6: Contrato rechaza campaña vacía si se proporciona
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            campaña="",
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_nombre_operacion_vacio():
    # S7: Contrato rechaza nombre_operacion vacío
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="",
            resultado_operacion="PASS",
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_resultado_operacion_invalido():
    # S8: Contrato rechaza resultado_operacion inválido
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="OK",  # type: ignore
            datos_reales_permitidos=False
        )


def test_contrato_rechaza_strings_vacios_en_listas():
    # S9: Contrato rechaza strings vacíos en listas
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="PASS",
            datos_reales_permitidos=False,
            fuentes_autorizadas=[""]
        )


def test_contrato_rechaza_bloqueado_sin_bloqueos():
    # S10: Contrato rechaza BLOQUEADO sin bloqueos
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="BLOQUEADO",
            datos_reales_permitidos=False,
            bloqueos=[]
        )


def test_contrato_rechaza_fail_sin_bloqueos_ni_advertencias():
    # S11: Contrato rechaza FAIL sin bloqueos ni advertencias
    with pytest.raises(ValidationError):
        EvidenciaContextoUsado(
            id_evidencia="ev_123",
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            nombre_operacion="Validar Contexto",
            resultado_operacion="FAIL",
            datos_reales_permitidos=False,
            bloqueos=[],
            advertencias=[]
        )
    # Acepta FAIL si tiene al menos un bloqueo
    ev1 = EvidenciaContextoUsado(
        id_evidencia="ev_123",
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        nombre_operacion="Validar Contexto",
        resultado_operacion="FAIL",
        datos_reales_permitidos=False,
        bloqueos=["bloqueo 1"],
        advertencias=[]
    )
    assert ev1.resultado_operacion == "FAIL"

    # Acepta FAIL si tiene al menos una advertencia
    ev2 = EvidenciaContextoUsado(
        id_evidencia="ev_123",
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        nombre_operacion="Validar Contexto",
        resultado_operacion="FAIL",
        datos_reales_permitidos=False,
        bloqueos=[],
        advertencias=["advertencia 1"]
    )
    assert ev2.resultado_operacion == "FAIL"
