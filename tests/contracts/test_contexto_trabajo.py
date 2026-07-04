import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo


def test_contrato_contexto_trabajo_valido():
    # S1: Contrato acepta contexto válido
    ctx = ContextoTrabajo(
        contexto_id="ctx_12345",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo",
        notas_seguridad=["Nota 1"]
    )
    assert ctx.contexto_id == "ctx_12345"
    assert ctx.cliente_id == "cliente_a"
    assert ctx.superficie == "linkedin_personal"
    assert ctx.campaña == "Q3_Launch"
    assert ctx.fuentes_autorizadas == ["doc1.txt"]
    assert ctx.datos_reales_permitidos is False
    assert ctx.estado == "activo"
    assert ctx.notas_seguridad == ["Nota 1"]


def test_contrato_rechaza_contexto_id_vacio():
    # S2: Contrato rechaza contexto_id vacío
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            estado="activo"
        )
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="   ",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            estado="activo"
        )


def test_contrato_rechaza_cliente_id_vacio():
    # S3: Contrato rechaza cliente_id vacío
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="",
            superficie="linkedin_personal",
            estado="activo"
        )
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="   ",
            superficie="linkedin_personal",
            estado="activo"
        )


def test_contrato_rechaza_superficie_invalida():
    # S4: Contrato rechaza superficie inválida
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="invalida",  # type: ignore
            estado="activo"
        )


def test_contrato_rechaza_campaña_vacia_si_se_proporciona():
    # S5: Contrato rechaza campaña vacía si se proporciona
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            campaña="",
            estado="activo"
        )
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            campaña="   ",
            estado="activo"
        )


def test_contrato_rechaza_strings_vacios_en_fuentes_autorizadas():
    # S6: Contrato rechaza strings vacíos en fuentes_autorizadas
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            fuentes_autorizadas=["doc1.txt", ""],
            estado="activo"
        )
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            fuentes_autorizadas=["doc1.txt", "   "],
            estado="activo"
        )


def test_contrato_rechaza_strings_vacios_en_notas_seguridad():
    # S7: Contrato rechaza strings vacíos en notas_seguridad
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            notas_seguridad=["Nota 1", ""],
            estado="activo"
        )
    with pytest.raises(ValidationError):
        ContextoTrabajo(
            contexto_id="ctx_123",
            cliente_id="cliente_a",
            superficie="linkedin_personal",
            notas_seguridad=["Nota 1", "   "],
            estado="activo"
        )
