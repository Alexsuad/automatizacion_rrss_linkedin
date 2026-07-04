from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.intencion_editorial_clasificada import IntencionEditorialClasificada
from linkedin_content_system.contracts.diagnostico_base_editorial import DiagnosticoBaseEditorial


def diagnosticar_base_editorial(
    idea: IdeaCentral,
    intencion: IntencionEditorialClasificada,
) -> DiagnosticoBaseEditorial:
    """
    Diagnostica si una IdeaCentral y una IntencionEditorialClasificada tienen
    una base editorial suficiente para avanzar a una fase posterior.
    Es un caso de uso determinista, sin uso de IA, sin red y sin efectos secundarios.
    """
    if idea is None:
        raise ValueError("La idea central no puede ser None.")
    if intencion is None:
        raise ValueError("La intención editorial no puede ser None.")

    hallazgos = []
    bloqueos = []
    recomendaciones = []
    limites_de_inferencia = [
        "Diagnóstico estático offline V0.",
        "No evalúa marketing avanzado ni voz de marca.",
        "No decide publicación final ni genera posts."
    ]

    es_warn = False
    es_fail = False

    # FAIL por falta de contenido crítico inesperado
    # (Si lograsen evadir Pydantic con cadenas vacías)
    if not idea.idea_central or not idea.idea_central.strip():
        es_fail = True
        bloqueos.append("Falta contenido crítico inesperado: idea_central vacía.")

    if not intencion.resumen_intencion or not intencion.resumen_intencion.strip():
        es_fail = True
        bloqueos.append("Falta contenido crítico inesperado: resumen_intencion vacío.")

    # WARN - idea corta (< 20 caracteres)
    if len(idea.idea_central) < 20:
        es_warn = True
        hallazgos.append("La idea central es corta (menos de 20 caracteres).")
        recomendaciones.append("Expandir la idea central con más contexto.")

    # WARN - pocos puntos de soporte (menos de 2)
    if len(idea.puntos_de_soporte) < 2:
        es_warn = True
        hallazgos.append("Pocos puntos de soporte (menos de 2).")
        recomendaciones.append("Añadir al menos 2 puntos de soporte para robustecer el contenido.")

    # WARN - intención principal indeterminada
    if intencion.intencion_principal == "indeterminada":
        es_warn = True
        hallazgos.append("Intención principal es indeterminada.")
        recomendaciones.append("Definir una intención principal más clara para el post.")

    # WARN - confianza de clasificación baja
    if intencion.confianza == "baja":
        es_warn = True
        hallazgos.append("La confianza de la clasificación de intención es baja.")
        recomendaciones.append("Revisar la justificación y coherencia de la intención editorial.")

    if es_fail:
        estado = "FAIL"
        resumen = "No se puede justificar el diagnóstico por falta de contenido crítico."
    elif es_warn:
        estado = "WARN"
        resumen = "Base editorial con advertencias. Requiere revisión o robustecimiento."
    else:
        estado = "PASS"
        resumen = "Base editorial suficiente para continuar el flujo."

    return DiagnosticoBaseEditorial(
        estado=estado,
        resumen=resumen,
        hallazgos=hallazgos,
        bloqueos=bloqueos,
        recomendaciones=recomendaciones,
        limites_de_inferencia=limites_de_inferencia
    )
