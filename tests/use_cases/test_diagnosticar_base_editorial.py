import os
import pytest
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.intencion_editorial_clasificada import IntencionEditorialClasificada
from linkedin_content_system.use_cases.diagnosticar_base_editorial import diagnosticar_base_editorial


def test_diagnosticar_base_editorial_pass_coherente():
    # S5: Caso de uso con idea + intención claras devuelve PASS
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Primer punto de soporte para que sea coherente", "Segundo punto de soporte"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de la intención editorial clasificada",
        justificacion="Justificación clara de por qué se elige",
        confianza="alta"
    )
    
    diag = diagnosticar_base_editorial(idea, intencion)
    assert diag.estado == "PASS"
    assert "suficiente" in diag.resumen
    assert len(diag.hallazgos) == 0
    assert len(diag.bloqueos) == 0


def test_diagnosticar_base_editorial_warn_por_idea_corta():
    # S5: Caso de uso con idea corta devuelve WARN
    idea = IdeaCentral(
        idea_central="Idea corta",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="media"
    )

    diag = diagnosticar_base_editorial(idea, intencion)
    assert diag.estado == "WARN"
    assert any("corta" in h for h in diag.hallazgos)


def test_diagnosticar_base_editorial_intencion_indeterminada():
    # S6: Intención indeterminada devuelve WARN
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="indeterminada",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="alta"
    )

    diag = diagnosticar_base_editorial(idea, intencion)
    assert diag.estado == "WARN"
    assert any("indeterminada" in h for h in diag.hallazgos)


def test_diagnosticar_base_editorial_confianza_baja():
    # S7: Confianza baja devuelve WARN
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="baja"
    )

    diag = diagnosticar_base_editorial(idea, intencion)
    assert diag.estado == "WARN"
    assert any("confianza" in h for h in diag.hallazgos)


def test_diagnosticar_base_editorial_rechaza_idea_none():
    # S8: Rechaza idea None con ValueError
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="alta"
    )
    with pytest.raises(ValueError, match="La idea central no puede ser None"):
        diagnosticar_base_editorial(None, intencion)  # type: ignore


def test_diagnosticar_base_editorial_rechaza_intencion_none():
    # S9: Rechaza intención None con ValueError
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1"]
    )
    with pytest.raises(ValueError, match="La intención editorial no puede ser None"):
        diagnosticar_base_editorial(idea, None)  # type: ignore


def test_diagnosticar_base_editorial_no_escribe_archivos(tmp_path):
    # S10: El caso de uso no escribe archivos en disco
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="alta"
    )

    cwd_inicial = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = diagnosticar_base_editorial(idea, intencion)
        assert res is not None
        archivos = os.listdir(tmp_path)
        assert len(archivos) == 0, f"Se crearon archivos inesperados: {archivos}"
    finally:
        os.chdir(cwd_inicial)


def test_diagnosticar_base_editorial_es_determinista():
    # S11: Es determinista. Dos ejecuciones idénticas producen la misma salida.
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="alta"
    )

    res1 = diagnosticar_base_editorial(idea, intencion)
    res2 = diagnosticar_base_editorial(idea, intencion)
    assert res1 == res2


def test_diagnosticar_base_editorial_no_modifica_las_entradas():
    # S12: No modifica las entradas recibidas.
    idea = IdeaCentral(
        idea_central="Esta es una idea central suficientemente larga y clara.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1", "Punto 2"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="alta"
    )

    # Captura de estado inicial
    idea_dict_antes = idea.model_dump()
    intencion_dict_antes = intencion.model_dump()

    _ = diagnosticar_base_editorial(idea, intencion)

    # Verificación de que siguen idénticos
    assert idea.model_dump() == idea_dict_antes
    assert intencion.model_dump() == intencion_dict_antes


def test_diagnosticar_base_editorial_incluye_limites_de_inferencia():
    # S13: El diagnóstico incluye límites de inferencia.
    idea = IdeaCentral(
        idea_central="Esta es una idea central corta",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1"]
    )
    intencion = IntencionEditorialClasificada(
        intencion_principal="indeterminada",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación clara",
        confianza="baja"
    )

    res = diagnosticar_base_editorial(idea, intencion)
    assert isinstance(res.limites_de_inferencia, list)
    assert len(res.limites_de_inferencia) >= 1
    assert any("offline V0" in limit for limit in res.limites_de_inferencia)
