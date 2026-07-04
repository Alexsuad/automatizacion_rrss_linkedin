import os
import pytest
from linkedin_content_system.contracts import IdeaCentral, IntencionEditorialClasificada
from linkedin_content_system.use_cases import extraer_intencion_editorial


def test_extraer_intencion_editorial_valida():
    # S6 — IdeaCentral válida produce IntencionEditorialClasificada válida.
    idea = IdeaCentral(
        idea_central="Aprendí a usar git hoy.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert isinstance(res, IntencionEditorialClasificada)
    assert res.intencion_principal == "compartir_aprendizaje"


def test_extraer_intencion_editorial_rechaza_none():
    # S7 — rechaza idea None.
    with pytest.raises(ValueError, match="La idea central no puede ser None."):
        extraer_intencion_editorial(None)


def test_extraer_intencion_editorial_clasifica_aprendizaje():
    # S8 — clasifica aprendizaje de forma determinista.
    idea = IdeaCentral(
        idea_central="Hoy me di cuenta de que las lecciones son importantes.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert res.intencion_principal == "compartir_aprendizaje"


def test_extraer_intencion_editorial_clasifica_explicacion():
    # S9 — clasifica explicación de forma determinista.
    idea = IdeaCentral(
        idea_central="Esta es una guía de cómo implementar Clean Architecture.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert res.intencion_principal == "explicar_idea"


def test_extraer_intencion_editorial_clasifica_indeterminada():
    # S10 — si no hay señales claras devuelve indeterminada.
    idea = IdeaCentral(
        idea_central="Frase sin palabras clave obvias.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert res.intencion_principal == "indeterminada"
    assert res.confianza == "baja"


def test_extraer_intencion_editorial_incluye_justificacion():
    # S11 — incluye justificación no vacía.
    idea = IdeaCentral(
        idea_central="Creo que esto es lo mejor.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert res.intencion_principal == "posicionar_opinion"
    assert len(res.justificacion) > 0


def test_extraer_intencion_editorial_incluye_limite_de_inferencia():
    # S12 — incluye límite de inferencia.
    idea = IdeaCentral(
        idea_central="Qué opinas de esto?",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res = extraer_intencion_editorial(idea)
    assert res.intencion_principal == "abrir_conversacion"
    assert len(res.limites_de_inferencia) >= 1


def test_extraer_intencion_editorial_no_escribe_archivos(tmp_path):
    # S13 — no escribe archivos.
    idea = IdeaCentral(
        idea_central="Cuando era joven, programaba en Basic.",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = extraer_intencion_editorial(idea)
        assert res is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_extraer_intencion_editorial_es_idempotente():
    # S14 — dos ejecuciones idénticas producen el mismo resultado.
    idea = IdeaCentral(
        idea_central="Lección de hoy",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    res1 = extraer_intencion_editorial(idea)
    res2 = extraer_intencion_editorial(idea)
    assert res1 == res2


def test_extraer_intencion_editorial_no_modifica_idea():
    # S15 — no modifica la IdeaCentral de entrada.
    idea = IdeaCentral(
        idea_central="Lección de hoy",
        resumen_operativo="Resumen",
        puntos_de_soporte=["Soporte"]
    )
    extraer_intencion_editorial(idea)
    assert idea.idea_central == "Lección de hoy"
    assert idea.resumen_operativo == "Resumen"
