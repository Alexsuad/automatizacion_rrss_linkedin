def test_exports_publicos_contexto_disponibles():
    from linkedin_content_system.contracts import ContextoTrabajo
    from linkedin_content_system.contracts import ResultadoCompatibilidadContexto
    from linkedin_content_system.contracts import ResultadoCambioContexto

    assert ContextoTrabajo is not None
    assert ResultadoCompatibilidadContexto is not None
    assert ResultadoCambioContexto is not None

def test_exports_publicos_previos_siguen_disponibles():
    from linkedin_content_system.contracts import IdeaCentral
    from linkedin_content_system.contracts import IntencionEditorialClasificada
    from linkedin_content_system.contracts import DiagnosticoBaseEditorial

    assert IdeaCentral is not None
    assert IntencionEditorialClasificada is not None
    assert DiagnosticoBaseEditorial is not None
