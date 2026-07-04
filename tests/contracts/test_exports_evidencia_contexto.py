def test_export_publico_evidencia_contexto_usado_disponible():
    from linkedin_content_system.contracts import EvidenciaContextoUsado

    assert EvidenciaContextoUsado is not None


def test_exports_publicos_previos_de_contexto_siguen_disponibles():
    from linkedin_content_system.contracts import ContextoTrabajo
    from linkedin_content_system.contracts import ResultadoCompatibilidadContexto
    from linkedin_content_system.contracts import ResultadoCambioContexto
    from linkedin_content_system.contracts import EvidenciaGeneracion

    assert ContextoTrabajo is not None
    assert ResultadoCompatibilidadContexto is not None
    assert ResultadoCambioContexto is not None
    assert EvidenciaGeneracion is not None
