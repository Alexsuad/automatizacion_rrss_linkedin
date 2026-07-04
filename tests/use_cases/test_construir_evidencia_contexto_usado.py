import os
import pytest
from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.use_cases.construir_evidencia_contexto_usado import construir_evidencia_contexto_usado


def test_construir_evidencia_contexto_usado_valido():
    # S12: Caso de uso construye evidencia válida desde ContextoTrabajo.
    # S17: Copia datos del contexto.
    # S21: incluye límite de inferencia fijo.
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="Q3_Launch",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )

    ev = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="Validar",
        resultado_operacion="PASS",
        artefactos_generados=["art1.json"],
        advertencias=["adv 1"],
        bloqueos=[]
    )

    assert ev.contexto_id == "ctx_123"
    assert ev.cliente_id == "cliente_a"
    assert ev.superficie == "linkedin_personal"
    assert ev.campaña == "Q3_Launch"
    assert ev.fuentes_autorizadas == ["doc1.txt"]
    assert ev.datos_reales_permitidos is False
    assert ev.nombre_operacion == "Validar"
    assert ev.resultado_operacion == "PASS"
    assert ev.artefactos_generados == ["art1.json"]
    assert ev.advertencias == ["adv 1"]
    assert ev.bloqueos == []
    assert len(ev.limites_de_inferencia) >= 1
    assert any("no verifica por sí sola" in lim for lim in ev.limites_de_inferencia)


def test_construir_evidencia_rechaza_contexto_none():
    # S13: Rechaza contexto None con ValueError
    with pytest.raises(ValueError, match="El contexto no puede ser None"):
        construir_evidencia_contexto_usado(
            contexto=None,  # type: ignore
            nombre_operacion="Validar",
            resultado_operacion="PASS"
        )


def test_construir_evidencia_rechaza_nombre_operacion_vacio():
    # S14: Rechaza nombre_operacion vacío con ValueError
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    with pytest.raises(ValueError, match="El nombre de la operación no puede estar vacío"):
        construir_evidencia_contexto_usado(
            contexto=contexto,
            nombre_operacion="",
            resultado_operacion="PASS"
        )
    with pytest.raises(ValueError, match="El nombre de la operación no puede estar vacío"):
        construir_evidencia_contexto_usado(
            contexto=contexto,
            nombre_operacion="   ",
            resultado_operacion="PASS"
        )


def test_construir_evidencia_rechaza_resultado_operacion_invalido():
    # S15: Rechaza resultado_operacion inválido
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    with pytest.raises(ValueError, match="Resultado de operación inválido"):
        construir_evidencia_contexto_usado(
            contexto=contexto,
            nombre_operacion="Validar",
            resultado_operacion="INVALIDO"
        )


def test_construir_evidencia_listas_none_se_convierten_en_vacias():
    # S16: Listas None se convierten en listas vacías
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    ev = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="Validar",
        resultado_operacion="PASS",
        artefactos_generados=None,
        advertencias=None,
        bloqueos=None
    )
    assert ev.artefactos_generados == []
    assert ev.advertencias == []
    assert ev.bloqueos == []


def test_construir_evidencia_no_muta_contexto():
    # S18: No muta el ContextoTrabajo original
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    contexto_dict_antes = contexto.model_dump()

    _ = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="Validar",
        resultado_operacion="PASS"
    )

    assert contexto.model_dump() == contexto_dict_antes


def test_construir_evidencia_id_evidencia_es_determinista():
    # S19: id_evidencia es determinista
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    ev1 = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="Validar",
        resultado_operacion="PASS"
    )
    ev2 = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="Validar",
        resultado_operacion="PASS"
    )
    assert ev1.id_evidencia == ev2.id_evidencia


def test_construir_evidencia_entradas_distintas_producen_ids_distintos():
    # S20: entradas distintas producen id_evidencia distinto
    contexto1 = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    contexto2 = ContextoTrabajo(
        contexto_id="ctx_456",
        cliente_id="cliente_b",
        superficie="linkedin_personal",
        estado="activo"
    )

    ev1 = construir_evidencia_contexto_usado(
        contexto=contexto1,
        nombre_operacion="Validar",
        resultado_operacion="PASS"
    )
    ev2 = construir_evidencia_contexto_usado(
        contexto=contexto1,
        nombre_operacion="Publicar",
        resultado_operacion="PASS"
    )
    ev3 = construir_evidencia_contexto_usado(
        contexto=contexto2,
        nombre_operacion="Validar",
        resultado_operacion="PASS"
    )
    ev4 = construir_evidencia_contexto_usado(
        contexto=contexto1,
        nombre_operacion="Validar",
        resultado_operacion="WARN",
        advertencias=["advertencia"]
    )

    ids = {ev1.id_evidencia, ev2.id_evidencia, ev3.id_evidencia, ev4.id_evidencia}
    assert len(ids) == 4


def test_construir_evidencia_no_escribe_archivos(tmp_path):
    # S22: no escribe archivos en disco
    contexto = ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        estado="activo"
    )
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        ev = construir_evidencia_contexto_usado(
            contexto=contexto,
            nombre_operacion="Validar",
            resultado_operacion="PASS"
        )
        assert ev is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)
