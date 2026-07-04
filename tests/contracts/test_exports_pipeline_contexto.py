def test_export_publico_resultado_pipeline_contexto_offline_disponible():
    from linkedin_content_system.contracts import ResultadoPipelineContextoOffline

    assert ResultadoPipelineContextoOffline is not None

def test_exports_publicos_previos_de_contexto_y_evidencia_siguen_disponibles():
    from linkedin_content_system.contracts import ContextoTrabajo
    from linkedin_content_system.contracts import EvidenciaContextoUsado
    from linkedin_content_system.contracts import ResultadoCompatibilidadContexto
    from linkedin_content_system.contracts import ResultadoCambioContexto

    assert ContextoTrabajo is not None
    assert EvidenciaContextoUsado is not None
    assert ResultadoCompatibilidadContexto is not None
    assert ResultadoCambioContexto is not None
