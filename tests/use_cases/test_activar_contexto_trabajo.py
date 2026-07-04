import os
import pytest
from linkedin_content_system.use_cases.activar_contexto_trabajo import activar_contexto_trabajo


def test_activar_contexto_trabajo_construye_valido():
    # S8: Caso de uso construye ContextoTrabajo válido
    # S12: datos_reales_permitidos es False por defecto
    # S13: incluye nota de seguridad de aislamiento
    ctx = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        fuentes_autorizadas=["doc1.txt"]
    )
    assert ctx.cliente_id == "cliente_a"
    assert ctx.superficie == "linkedin_personal"
    assert ctx.campaña == "Q3_Launch"
    assert ctx.fuentes_autorizadas == ["doc1.txt"]
    assert ctx.datos_reales_permitidos is False
    assert ctx.estado == "activo"
    assert len(ctx.contexto_id) == 12

    # Nota de seguridad de aislamiento
    assert any("Contexto aislado" in nota for nota in ctx.notas_seguridad)
    # Al ser datos_reales_permitidos False por defecto, también incluye la otra nota
    assert any("Datos reales no permitidos" in nota for nota in ctx.notas_seguridad)


def test_activar_contexto_trabajo_fuentes_none_se_convierte_en_vacia():
    # S9: fuentes_autorizadas None se convierte en lista vacía
    ctx = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        fuentes_autorizadas=None
    )
    assert ctx.fuentes_autorizadas == []


def test_activar_contexto_trabajo_contexto_id_es_determinista():
    # S10: contexto_id es determinista
    ctx1 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False
    )
    ctx2 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False
    )
    assert ctx1.contexto_id == ctx2.contexto_id


def test_activar_contexto_trabajo_entradas_distintas_producen_ids_distintos():
    # S11: entradas distintas producen contexto_id distinto
    ctx1 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch"
    )
    ctx2 = activar_contexto_trabajo(
        cliente_id="cliente_b",
        superficie="linkedin_personal",
        campaña="Q3_Launch"
    )
    ctx3 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_empresa",
        campaña="Q3_Launch"
    )
    ctx4 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q4_Launch"
    )
    ctx5 = activar_contexto_trabajo(
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        datos_reales_permitidos=True
    )

    ids = {ctx1.contexto_id, ctx2.contexto_id, ctx3.contexto_id, ctx4.contexto_id, ctx5.contexto_id}
    assert len(ids) == 5


def test_activar_contexto_trabajo_no_escribe_archivos(tmp_path):
    # S14: no escribe archivos en disco
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        ctx = activar_contexto_trabajo(
            cliente_id="cliente_a",
            superficie="general"
        )
        assert ctx is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_activar_contexto_trabajo_rechaza_cliente_id_vacio():
    with pytest.raises(ValueError, match="El cliente_id no puede estar vacío"):
        activar_contexto_trabajo(cliente_id="", superficie="general")
    with pytest.raises(ValueError, match="El cliente_id no puede estar vacío"):
        activar_contexto_trabajo(cliente_id="   ", superficie="general")


def test_activar_contexto_trabajo_rechaza_superficie_invalida():
    with pytest.raises(ValueError, match="Superficie inválida"):
        activar_contexto_trabajo(cliente_id="cliente_a", superficie="linkedin_grupo")
