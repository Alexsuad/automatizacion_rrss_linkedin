import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.intencion_editorial_clasificada import IntencionEditorialClasificada
from linkedin_content_system.contracts.diagnostico_base_editorial import DiagnosticoBaseEditorial
from linkedin_content_system.contracts.evidencia_contexto_usado import EvidenciaContextoUsado
from linkedin_content_system.contracts.resultado_pipeline_contexto_offline import ResultadoPipelineContextoOffline


@pytest.fixture
def idea_valida():
    return IdeaCentral(
        idea_central="Esta es una idea central lo suficientemente larga para ser válida.",
        resumen_operativo="Resumen operativo",
        puntos_de_soporte=["Punto 1"],
        limites_de_inferencia=[]
    )


@pytest.fixture
def intencion_valida():
    return IntencionEditorialClasificada(
        intencion_principal="explicar_idea",
        resumen_intencion="Resumen de intención",
        justificacion="Justificación",
        confianza="alta",
        limites_de_inferencia=[]
    )


@pytest.fixture
def diagnostico_valido():
    return DiagnosticoBaseEditorial(
        estado="PASS",
        resumen="Todo correcto",
        hallazgos=[],
        bloqueos=[],
        recomendaciones=[],
        limites_de_inferencia=[]
    )


@pytest.fixture
def evidencia_valida():
    return EvidenciaContextoUsado(
        id_evidencia="1234567890ab",
        contexto_id="ctx_1",
        cliente_id="cliente_a",
        superficie="linkedin_personal",
        campaña=None,
        nombre_operacion="test",
        resultado_operacion="PASS",
        datos_reales_permitidos=False,
        fuentes_autorizadas=[],
        artefactos_generados=[],
        advertencias=[],
        bloqueos=[],
        limites_de_inferencia=[]
    )


def test_contrato_acepta_resultado_pass_valido(idea_valida, intencion_valida, diagnostico_valido, evidencia_valida):
    # S1 — Contrato acepta resultado PASS válido.
    res = ResultadoPipelineContextoOffline(
        estado="PASS",
        contexto_id="ctx_1",
        idea_central=idea_valida,
        intencion_editorial=intencion_valida,
        diagnostico_base=diagnostico_valido,
        evidencia_contexto=evidencia_valida,
        bloqueos=[],
        advertencias=[],
        limites_de_inferencia=["Límite"]
    )
    assert res.estado == "PASS"
    assert res.contexto_id == "ctx_1"
    assert res.idea_central == idea_valida
    assert res.intencion_editorial == intencion_valida
    assert res.diagnostico_base == diagnostico_valido
    assert res.evidencia_contexto == evidencia_valida


def test_contrato_rechaza_estado_inválido(idea_valida, intencion_valida, diagnostico_valido, evidencia_valida):
    # S2 — Contrato rechaza estado inválido.
    with pytest.raises(ValidationError):
        ResultadoPipelineContextoOffline(
            estado="OTRO",  # type: ignore
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida
        )


def test_contrato_rechaza_contexto_id_vacio(idea_valida, intencion_valida, diagnostico_valido, evidencia_valida):
    # S3 — Contrato rechaza contexto_id vacío.
    with pytest.raises(ValidationError):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida
        )
    with pytest.raises(ValidationError):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="   ",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida
        )


def test_contrato_rechaza_strings_vacios_en_listas(idea_valida, intencion_valida, diagnostico_valido, evidencia_valida):
    # S4 — Contrato rechaza strings vacíos en listas.
    with pytest.raises(ValidationError):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida,
            advertencias=[""]
        )
    with pytest.raises(ValidationError):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida,
            bloqueos=["   "]
        )


def test_contrato_rechaza_bloqueado_sin_bloqueos(evidencia_valida):
    # S5 — Contrato rechaza BLOQUEADO sin bloqueos.
    # We must patch or supply a valid EvidenciaContextoUsado with BLOQUEADO
    evidencia_bloq = evidencia_valida.model_copy(update={
        "resultado_operacion": "BLOQUEADO",
        "bloqueos": ["Falta compatibilidad"]
    })
    with pytest.raises(ValidationError, match="Si el estado es BLOQUEADO, debe existir al menos un bloqueo"):
        ResultadoPipelineContextoOffline(
            estado="BLOQUEADO",
            contexto_id="ctx_1",
            idea_central=None,
            intencion_editorial=None,
            diagnostico_base=None,
            evidencia_contexto=evidencia_bloq,
            bloqueos=[],
            advertencias=[]
        )


def test_contrato_rechaza_pass_sin_idea_central(intencion_valida, diagnostico_valido, evidencia_valida):
    # S6 — Contrato rechaza PASS sin idea_central.
    with pytest.raises(ValidationError, match="idea_central, intencion_editorial y diagnostico_base deben existir"):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="ctx_1",
            idea_central=None,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida
        )


def test_contrato_rechaza_pass_sin_intencion_editorial(idea_valida, diagnostico_valido, evidencia_valida):
    # S7 — Contrato rechaza PASS sin intencion_editorial.
    with pytest.raises(ValidationError, match="idea_central, intencion_editorial y diagnostico_base deben existir"):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=None,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_valida
        )


def test_contrato_rechaza_pass_sin_diagnostico_base(idea_valida, intencion_valida, evidencia_valida):
    # S8 — Contrato rechaza PASS sin diagnostico_base.
    with pytest.raises(ValidationError, match="idea_central, intencion_editorial y diagnostico_base deben existir"):
        ResultadoPipelineContextoOffline(
            estado="PASS",
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=None,
            evidencia_contexto=evidencia_valida
        )


def test_contrato_rechaza_bloqueado_con_idea_intencion_diagnostico(evidencia_valida, idea_valida, intencion_valida, diagnostico_valido):
    # S9 — Contrato rechaza BLOQUEADO con idea/intención/diagnóstico presentes.
    evidencia_bloq = evidencia_valida.model_copy(update={
        "resultado_operacion": "BLOQUEADO",
        "bloqueos": ["Falta compatibilidad"]
    })
    with pytest.raises(ValidationError, match="idea_central, intencion_editorial y diagnostico_base deben ser None"):
        ResultadoPipelineContextoOffline(
            estado="BLOQUEADO",
            contexto_id="ctx_1",
            idea_central=idea_valida,
            intencion_editorial=intencion_valida,
            diagnostico_base=diagnostico_valido,
            evidencia_contexto=evidencia_bloq,
            bloqueos=["Compatibilidad fallida"]
        )
