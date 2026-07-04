import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.evidencia_generacion import EvidenciaGeneracion


def test_contrato_acepta_evidencia_valida():
    # S1 — Contrato acepta evidencia válida.
    evidencia = EvidenciaGeneracion(
        id_evidencia="1234567890ab",
        fase="Fase H",
        entrada_resumen="Entrada resumen válida",
        salida_resumen="Salida resumen válida",
        estado="PASS",
        artefactos=["art1.json", "art2.md"],
        advertencias=["advertencia 1"],
        bloqueos=[]
    )
    assert evidencia.id_evidencia == "1234567890ab"
    assert evidencia.fase == "Fase H"
    assert evidencia.entrada_resumen == "Entrada resumen válida"
    assert evidencia.salida_resumen == "Salida resumen válida"
    assert evidencia.estado == "PASS"
    assert evidencia.artefactos == ["art1.json", "art2.md"]
    assert evidencia.advertencias == ["advertencia 1"]
    assert evidencia.bloqueos == []


def test_contrato_rechaza_id_evidencia_vacio():
    # S2 — Contrato rechaza id_evidencia vacío.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="   ",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )


def test_contrato_rechaza_fase_vacia():
    # S3 — Contrato rechaza fase vacía.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="   ",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )


def test_contrato_rechaza_entrada_resumen_vacio():
    # S4 — Contrato rechaza entrada_resumen vacío.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="   ",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )


def test_contrato_rechaza_salida_resumen_vacio():
    # S5 — Contrato rechaza salida_resumen vacío.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="   ",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )


def test_contrato_rechaza_estado_invalido():
    # S6 — Contrato rechaza estado inválido.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="INVALIDO",  # type: ignore
            artefactos=[],
            advertencias=[],
            bloqueos=[]
        )


def test_contrato_rechaza_strings_vacios_en_listas():
    # S7 — Contrato rechaza strings vacíos dentro de listas.
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[""],
            advertencias=[],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=["   "],
            bloqueos=[]
        )
    with pytest.raises(ValidationError):
        EvidenciaGeneracion(
            id_evidencia="1234567890ab",
            fase="Fase H",
            entrada_resumen="Entrada resumen",
            salida_resumen="Salida resumen",
            estado="PASS",
            artefactos=[],
            advertencias=[],
            bloqueos=[""]
        )
