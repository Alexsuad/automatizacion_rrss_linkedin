import os
import pytest
from linkedin_content_system.use_cases.construir_evidencia_generacion import construir_evidencia_generacion


def test_caso_de_uso_construye_evidencia_valida():
    # S8 — Caso de uso construye evidencia válida.
    ev = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS",
        artefactos=["art.json"],
        advertencias=["adv"],
        bloqueos=["bloq"]
    )
    assert ev.id_evidencia is not None
    assert len(ev.id_evidencia) == 12
    assert ev.fase == "Fase H"
    assert ev.entrada_resumen == "Entrada resumen"
    assert ev.salida_resumen == "Salida resumen"
    assert ev.estado == "PASS"
    assert ev.artefactos == ["art.json"]
    assert ev.advertencias == ["adv"]
    assert ev.bloqueos == ["bloq"]


def test_id_evidencia_es_determinista():
    # S9 — id_evidencia es determinista.
    ev1 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS",
        artefactos=["art.json"],
        advertencias=["adv"]
    )
    ev2 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS",
        artefactos=["art.json"],
        advertencias=["adv"]
    )
    assert ev1.id_evidencia == ev2.id_evidencia


def test_dos_entradas_distintas_producen_ids_distintos():
    # S10 — dos entradas distintas producen ids distintos.
    ev1 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen 1",
        salida_resumen="Salida resumen",
        estado="PASS"
    )
    ev2 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen 2",
        salida_resumen="Salida resumen",
        estado="PASS"
    )
    assert ev1.id_evidencia != ev2.id_evidencia


def test_listas_none_se_convierten_en_listas_vacias():
    # S11 — listas None se convierten en listas vacías.
    ev = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS",
        artefactos=None,
        advertencias=None,
        bloqueos=None
    )
    assert ev.artefactos == []
    assert ev.advertencias == []
    assert ev.bloqueos == []


def test_no_escribe_archivos(tmp_path):
    # S12 — No escribe archivos.
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        _ = construir_evidencia_generacion(
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS"
        )
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_no_usa_fecha_hora_ni_uuid_aleatorio():
    # S13 — No usa fecha/hora ni uuid aleatorio.
    # El id es generado puramente mediante hash sha256 y no cambia
    # con el tiempo o ejecuciones consecutivas.
    import time
    ev1 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS"
    )
    time.sleep(0.01)
    ev2 = construir_evidencia_generacion(
        fase="Fase H",
        entrada_resumen="Entrada resumen",
        salida_resumen="Salida resumen",
        estado="PASS"
    )
    assert ev1.id_evidencia == ev2.id_evidencia
