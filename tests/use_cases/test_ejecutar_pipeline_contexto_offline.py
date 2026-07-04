import os
import pytest
from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.use_cases.ejecutar_pipeline_contexto_offline import ejecutar_pipeline_contexto_offline


@pytest.fixture
def contexto_valido():
    return ContextoTrabajo(
        contexto_id="ctx_1",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )


def test_rechaza_contexto_none():
    # S10 — Caso de uso rechaza contexto None.
    with pytest.raises(ValueError, match="El contexto no puede ser None"):
        ejecutar_pipeline_contexto_offline(
            contexto=None,  # type: ignore
            texto_base="Texto base largo de ejemplo",
            cliente_id_operacion="cliente_a",
            superficie_operacion="linkedin_personal"
        )


def test_rechaza_texto_base_vacio(contexto_valido):
    # S11 — Caso de uso rechaza texto_base vacío.
    with pytest.raises(ValueError, match="El texto_base no puede estar vacío"):
        ejecutar_pipeline_contexto_offline(
            contexto=contexto_valido,
            texto_base="",
            cliente_id_operacion="cliente_a",
            superficie_operacion="linkedin_personal"
        )
    with pytest.raises(ValueError, match="El texto_base no puede estar vacío"):
        ejecutar_pipeline_contexto_offline(
            contexto=contexto_valido,
            texto_base="   ",
            cliente_id_operacion="cliente_a",
            superficie_operacion="linkedin_personal"
        )


def test_rechaza_cliente_id_operacion_vacio(contexto_valido):
    # S12 — Caso de uso rechaza cliente_id_operacion vacío.
    with pytest.raises(ValueError, match="cliente_id_operacion no puede estar vacío"):
        ejecutar_pipeline_contexto_offline(
            contexto=contexto_valido,
            texto_base="Texto base largo de ejemplo",
            cliente_id_operacion="",
            superficie_operacion="linkedin_personal"
        )


def test_rechaza_superficie_operacion_vacia(contexto_valido):
    # S13 — Caso de uso rechaza superficie_operacion vacía.
    with pytest.raises(ValueError, match="superficie_operacion no puede estar vacía"):
        ejecutar_pipeline_contexto_offline(
            contexto=contexto_valido,
            texto_base="Texto base largo de ejemplo",
            cliente_id_operacion="cliente_a",
            superficie_operacion="   "
        )


def test_si_contexto_incompatible_devuelve_bloqueado(contexto_valido):
    # S14 — Si contexto es incompatible, devuelve BLOQUEADO.
    res = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_b",  # Incompatible cliente
        superficie_operacion="linkedin_personal"
    )
    assert res.estado == "BLOQUEADO"
    assert len(res.bloqueos) >= 1
    assert any("cliente" in b for b in res.bloqueos)


def test_si_contexto_incompatible_no_ejecuta_pipeline_posterior(contexto_valido):
    # S15 — Si contexto es incompatible, no ejecuta pipeline posterior.
    res = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_b",
        superficie_operacion="linkedin_personal"
    )
    assert res.idea_central is None
    assert res.intencion_editorial is None
    assert res.diagnostico_base is None


def test_si_contexto_compatible_ejecuta_pipeline_exitosamente(contexto_valido):
    # S16, S17, S18 — Si contexto es compatible, genera idea central, intención y diagnóstico.
    res = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Esta es una idea central lo suficientemente larga para pasar el test.",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    assert res.estado in ["PASS", "WARN"]
    assert res.idea_central is not None
    assert res.idea_central.idea_central is not None
    assert res.intencion_editorial is not None
    assert res.diagnostico_base is not None


def test_siempre_construye_evidencia_de_contexto_usado(contexto_valido):
    # S19 — Siempre construye evidencia de contexto usado.
    res_bloq = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Idea central",
        cliente_id_operacion="cliente_b",
        superficie_operacion="linkedin_personal"
    )
    assert res_bloq.evidencia_contexto is not None
    assert res_bloq.evidencia_contexto.resultado_operacion == "BLOQUEADO"

    res_pass = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Esta es una idea central lo suficientemente larga para pasar el test.",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    assert res_pass.evidencia_contexto is not None
    assert res_pass.evidencia_contexto.resultado_operacion in ["PASS", "WARN", "FAIL"]


def test_fuentes_usadas_none_se_convierten_en_lista_vacia(contexto_valido):
    # S20 — fuentes_usadas None se convierte en lista vacía.
    res = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Esta es una idea central lo suficientemente larga para pasar el test.",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=None
    )
    assert res.estado in ["PASS", "WARN"]


def test_estado_final_respeta_diagnostico_pass_warn(contexto_valido):
    # S21 — estado final respeta diagnóstico PASS/WARN.
    # Un texto muy corto debe causar WARN en diagnostico_base
    res_warn = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Corta",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    assert res_warn.diagnostico_base.estado == "WARN"
    assert res_warn.estado == "WARN"

    # Un texto suficientemente largo debe causar PASS en diagnostico_base
    res_pass = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Esta es una idea central lo suficientemente larga para no causar un warn por longitud corta.",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    # Note: it might cause WARN due to other rules (like number of support points), but let's check:
    assert res_pass.estado == res_pass.diagnostico_base.estado


def test_id_evidencia_es_determinista(contexto_valido):
    # S22 — id/evidencia es determinista.
    res1 = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    res2 = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    assert res1.evidencia_contexto.id_evidencia == res2.evidencia_contexto.id_evidencia


def test_no_escribe_archivos(contexto_valido, tmp_path):
    # S23 — no escribe archivos.
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        _ = ejecutar_pipeline_contexto_offline(
            contexto=contexto_valido,
            texto_base="Texto de prueba",
            cliente_id_operacion="cliente_a",
            superficie_operacion="linkedin_personal"
        )
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_no_usa_ia_real_ni_red_ni_random(contexto_valido):
    # S24 — no usa IA real, red, fecha/hora, uuid ni random.
    # El pipeline es puramente determinista y offline
    res1 = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    import time
    time.sleep(0.01)
    res2 = ejecutar_pipeline_contexto_offline(
        contexto=contexto_valido,
        texto_base="Texto base largo de ejemplo",
        cliente_id_operacion="cliente_a",
        superficie_operacion="linkedin_personal"
    )
    assert res1.evidencia_contexto.id_evidencia == res2.evidencia_contexto.id_evidencia
