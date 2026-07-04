from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.contracts.resultado_pipeline_contexto_offline import ResultadoPipelineContextoOffline
from linkedin_content_system.use_cases.validar_compatibilidad_contexto import validar_compatibilidad_contexto
from linkedin_content_system.use_cases.extraer_idea_central import extraer_idea_central
from linkedin_content_system.use_cases.extraer_intencion_editorial import extraer_intencion_editorial
from linkedin_content_system.use_cases.diagnosticar_base_editorial import diagnosticar_base_editorial
from linkedin_content_system.use_cases.construir_evidencia_contexto_usado import construir_evidencia_contexto_usado


def ejecutar_pipeline_contexto_offline(
    contexto: ContextoTrabajo,
    texto_base: str,
    cliente_id_operacion: str,
    superficie_operacion: str,
    fuentes_usadas: list[str] | None = None,
    datos_reales_detectados: bool = False,
) -> ResultadoPipelineContextoOffline:
    """
    Ejecuta el pipeline offline con validación de contexto y evidencias en memoria.
    No escribe archivos, no usa red ni IA real.
    """
    if contexto is None:
        raise ValueError("El contexto no puede ser None.")
    if texto_base is None or not texto_base.strip():
        raise ValueError("El texto_base no puede estar vacío.")
    if cliente_id_operacion is None or not cliente_id_operacion.strip():
        raise ValueError("cliente_id_operacion no puede estar vacío.")
    if superficie_operacion is None or not superficie_operacion.strip():
        raise ValueError("superficie_operacion no puede estar vacía.")

    fuentes = fuentes_usadas if fuentes_usadas is not None else []
    limite_fijo = "Pipeline offline determinista: no verifica contenido externo ni ejecuta IA real."

    # 1. Validar compatibilidad de contexto
    res_compatibilidad = validar_compatibilidad_contexto(
        contexto=contexto,
        cliente_id_operacion=cliente_id_operacion,
        superficie_operacion=superficie_operacion,
        fuentes_usadas=fuentes,
        datos_reales_detectados=datos_reales_detectados
    )

    if res_compatibilidad.estado == "BLOQUEADO":
        # Construir evidencia de contexto con resultado BLOQUEADO
        evidencia = construir_evidencia_contexto_usado(
            contexto=contexto,
            nombre_operacion="ejecutar_pipeline_contexto_offline",
            resultado_operacion="BLOQUEADO",
            artefactos_generados=[],
            advertencias=res_compatibilidad.advertencias,
            bloqueos=res_compatibilidad.bloqueos
        )
        return ResultadoPipelineContextoOffline(
            estado="BLOQUEADO",
            contexto_id=contexto.contexto_id,
            idea_central=None,
            intencion_editorial=None,
            diagnostico_base=None,
            evidencia_contexto=evidencia,
            bloqueos=res_compatibilidad.bloqueos,
            advertencias=res_compatibilidad.advertencias,
            limites_de_inferencia=[limite_fijo]
        )

    # 2. Si es compatible, continuar con el pipeline
    idea = extraer_idea_central(texto_base)
    intencion = extraer_intencion_editorial(idea)
    diagnostico = diagnosticar_base_editorial(idea, intencion)

    # El estado final del pipeline copia el estado del diagnóstico
    estado_final = diagnostico.estado  # "PASS", "WARN" o "FAIL"

    # Construir evidencia de contexto usado con los resultados del diagnóstico
    evidencia = construir_evidencia_contexto_usado(
        contexto=contexto,
        nombre_operacion="ejecutar_pipeline_contexto_offline",
        resultado_operacion=estado_final,
        artefactos_generados=["IdeaCentral", "IntencionEditorialClasificada", "DiagnosticoBaseEditorial"],
        advertencias=diagnostico.hallazgos,
        bloqueos=diagnostico.bloqueos
    )

    return ResultadoPipelineContextoOffline(
        estado=estado_final,  # type: ignore
        contexto_id=contexto.contexto_id,
        idea_central=idea,
        intencion_editorial=intencion,
        diagnostico_base=diagnostico,
        evidencia_contexto=evidencia,
        bloqueos=diagnostico.bloqueos,
        advertencias=diagnostico.hallazgos,
        limites_de_inferencia=[limite_fijo]
    )
