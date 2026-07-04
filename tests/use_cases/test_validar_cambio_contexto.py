import os
import pytest
from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.use_cases.validar_cambio_contexto import validar_cambio_contexto


@pytest.fixture
def contexto_valido_1():
    return ContextoTrabajo(
        contexto_id="ctx_1",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )


@pytest.fixture
def contexto_valido_2():
    return ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )


def test_rechaza_contexto_actual_none(contexto_valido_1):
    # S7 — Rechaza contexto_actual None.
    with pytest.raises(ValueError, match="El contexto actual no puede ser None"):
        validar_cambio_contexto(None, contexto_valido_1, True, "Motivo")  # type: ignore


def test_rechaza_contexto_nuevo_none(contexto_valido_1):
    # S8 — Rechaza contexto_nuevo None.
    with pytest.raises(ValueError, match="El contexto nuevo no puede ser None"):
        validar_cambio_contexto(contexto_valido_1, None, True, "Motivo")  # type: ignore


def test_rechaza_motivo_vacio(contexto_valido_1, contexto_valido_2):
    # S9 — Rechaza motivo vacío.
    with pytest.raises(ValueError, match="El motivo no puede estar vacío"):
        validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "")
    with pytest.raises(ValueError, match="El motivo no puede estar vacío"):
        validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "   ")


def test_bloquea_si_confirmacion_reset_false(contexto_valido_1, contexto_valido_2):
    # S10 — Bloquea si confirmacion_reset=False.
    res = validar_cambio_contexto(contexto_valido_1, contexto_valido_2, False, "Cambio")
    assert res.puede_cambiar is False
    assert res.estado == "BLOQUEADO"
    assert len(res.bloqueos) >= 1
    assert any("confirmación" in b for b in res.bloqueos)


def test_permite_si_confirmacion_reset_true(contexto_valido_1, contexto_valido_2):
    # S11 — Permite si confirmacion_reset=True.
    res = validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "Cambio")
    assert res.puede_cambiar is True
    assert res.estado == "PASS"
    assert len(res.bloqueos) == 0


def test_cambio_de_cliente_requiere_limpieza_manual(contexto_valido_1):
    # S12 — Cambio de cliente requiere limpieza manual.
    ctx_nuevo = ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_diferente",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )
    res = validar_cambio_contexto(contexto_valido_1, ctx_nuevo, True, "Cambio")
    assert res.puede_cambiar is True
    assert res.requiere_limpieza_manual is True


def test_cambio_de_superficie_requiere_limpieza_manual(contexto_valido_1):
    # S13 — Cambio de superficie requiere limpieza manual.
    ctx_nuevo = ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_a",
        superficie="linkedin_empresa",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )
    res = validar_cambio_contexto(contexto_valido_1, ctx_nuevo, True, "Cambio")
    assert res.puede_cambiar is True
    assert res.requiere_limpieza_manual is True


def test_cambio_de_datos_reales_permitidos_requiere_limpieza_manual(contexto_valido_1):
    # S14 — Cambio de datos_reales_permitidos requiere limpieza manual.
    ctx_nuevo = ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=True,
        estado="activo"
    )
    res = validar_cambio_contexto(contexto_valido_1, ctx_nuevo, True, "Cambio")
    assert res.puede_cambiar is True
    assert res.requiere_limpieza_manual is True


def test_cambio_de_campana_genera_advertencia(contexto_valido_1):
    # S15 — Cambio de campaña genera advertencia.
    ctx_nuevo = ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_diferente",
        fuentes_autorizadas=["doc1.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )
    res = validar_cambio_contexto(contexto_valido_1, ctx_nuevo, True, "Cambio")
    assert res.puede_cambiar is True
    assert len(res.advertencias) >= 1
    assert any("campaña" in adv for adv in res.advertencias)


def test_cambio_de_fuentes_genera_advertencia(contexto_valido_1):
    # S16 — Cambio de fuentes genera advertencia.
    ctx_nuevo = ContextoTrabajo(
        contexto_id="ctx_2",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña="campana_1",
        fuentes_autorizadas=["doc1.txt", "doc2.txt"],
        datos_reales_permitidos=False,
        estado="activo"
    )
    res = validar_cambio_contexto(contexto_valido_1, ctx_nuevo, True, "Cambio")
    assert res.puede_cambiar is True
    assert len(res.advertencias) >= 1
    assert any("fuentes" in adv for adv in res.advertencias)


def test_no_escribe_ni_borra_archivos(contexto_valido_1, contexto_valido_2, tmp_path):
    # S17 — No escribe ni borra archivos.
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        _ = validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "Cambio")
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se alteraron archivos de forma inesperada: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_es_determinista(contexto_valido_1, contexto_valido_2):
    # S18 — Es determinista.
    res1 = validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "Cambio")
    res2 = validar_cambio_contexto(contexto_valido_1, contexto_valido_2, True, "Cambio")
    assert res1 == res2
