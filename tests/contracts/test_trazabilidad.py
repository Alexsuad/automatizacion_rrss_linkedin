import pytest
from pydantic import ValidationError

from linkedin_content_system.contracts import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
    HallazgoTrazabilidad,
    TipoHallazgoTrazabilidad,
)


def test_diagnostico_trazabilidad_pass_sin_hallazgos():
    diagnostico = DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)

    assert diagnostico.estado == EstadoTrazabilidad.PASS
    assert diagnostico.hallazgos == []
    assert diagnostico.resumen is None


def test_hallazgo_critico_se_representa_correctamente():
    hallazgo = HallazgoTrazabilidad(
        tipo=TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA,
        fragmento_post="Aumentamos 42%",
        descripcion="La cifra no aparece en la entrada original ni en la idea central.",
        soporte_encontrado=None,
        bloqueante=True,
    )
    diagnostico = DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.FAIL,
        hallazgos=[hallazgo],
        resumen="La trazabilidad detectó una cifra no soportada.",
    )

    assert diagnostico.estado == EstadoTrazabilidad.FAIL
    assert diagnostico.hallazgos[0].tipo == TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA
    assert diagnostico.hallazgos[0].bloqueante is True


@pytest.mark.parametrize(
    "valor",
    ["PASS", "WARN", "FAIL"],
)
def test_estado_trazabilidad_solo_acepta_valores_esperados(valor):
    assert EstadoTrazabilidad(valor).value == valor


def test_estado_trazabilidad_rechaza_valor_invalido():
    with pytest.raises(ValueError):
        EstadoTrazabilidad("OTRO")


@pytest.mark.parametrize(
    "valor",
    [
        "hecho_no_soportado",
        "autoridad_fingida",
        "anecdota_inventada",
        "cifra_no_soportada",
        "promesa_excesiva",
        "claim_sin_fuente",
        "inferencia_debil",
        "contradiccion_con_contexto",
    ],
)
def test_tipo_hallazgo_trazabilidad_solo_acepta_valores_esperados(valor):
    assert TipoHallazgoTrazabilidad(valor).value == valor


def test_tipo_hallazgo_trazabilidad_rechaza_valor_invalido():
    with pytest.raises(ValueError):
        TipoHallazgoTrazabilidad("inventado")


def test_export_publico_contracts_incluye_trazabilidad():
    from linkedin_content_system.contracts import (
        DiagnosticoTrazabilidad as DiagnosticoTrazabilidadExportado,
        EstadoTrazabilidad as EstadoTrazabilidadExportado,
        HallazgoTrazabilidad as HallazgoTrazabilidadExportado,
        TipoHallazgoTrazabilidad as TipoHallazgoTrazabilidadExportado,
    )

    assert DiagnosticoTrazabilidadExportado is DiagnosticoTrazabilidad
    assert EstadoTrazabilidadExportado is EstadoTrazabilidad
    assert HallazgoTrazabilidadExportado is HallazgoTrazabilidad
    assert TipoHallazgoTrazabilidadExportado is TipoHallazgoTrazabilidad
