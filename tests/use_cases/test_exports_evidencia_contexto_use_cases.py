def test_export_publico_construir_evidencia_contexto_usado_disponible():
    from linkedin_content_system.use_cases import construir_evidencia_contexto_usado

    assert construir_evidencia_contexto_usado is not None


def test_exports_publicos_use_cases_previos_de_contexto_siguen_disponibles():
    from linkedin_content_system.use_cases import activar_contexto_trabajo
    from linkedin_content_system.use_cases import validar_compatibilidad_contexto
    from linkedin_content_system.use_cases import validar_cambio_contexto
    from linkedin_content_system.use_cases import construir_evidencia_generacion

    assert activar_contexto_trabajo is not None
    assert validar_compatibilidad_contexto is not None
    assert validar_cambio_contexto is not None
    assert construir_evidencia_generacion is not None
