def test_exports_publicos_use_cases_contexto_disponibles():
    from linkedin_content_system.use_cases import activar_contexto_trabajo
    from linkedin_content_system.use_cases import validar_compatibilidad_contexto
    from linkedin_content_system.use_cases import validar_cambio_contexto

    assert activar_contexto_trabajo is not None
    assert validar_compatibilidad_contexto is not None
    assert validar_cambio_contexto is not None

def test_exports_publicos_use_cases_previos_siguen_disponibles():
    from linkedin_content_system.use_cases import extraer_idea_central
    from linkedin_content_system.use_cases import extraer_intencion_editorial
    from linkedin_content_system.use_cases import diagnosticar_base_editorial

    assert extraer_idea_central is not None
    assert extraer_intencion_editorial is not None
    assert diagnosticar_base_editorial is not None
