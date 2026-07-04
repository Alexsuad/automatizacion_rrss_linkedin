from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.contracts.cambio_contexto import ResultadoCambioContexto


def validar_cambio_contexto(
    contexto_actual: ContextoTrabajo,
    contexto_nuevo: ContextoTrabajo,
    confirmacion_reset: bool,
    motivo: str,
) -> ResultadoCambioContexto:
    """
    Valida de manera determinista y offline el cambio controlado entre dos contextos de trabajo.
    No escribe ni borra archivos, no usa red ni IA.
    """
    if contexto_actual is None:
        raise ValueError("El contexto actual no puede ser None.")
    if contexto_nuevo is None:
        raise ValueError("El contexto nuevo no puede ser None.")
    if not motivo or not motivo.strip():
        raise ValueError("El motivo no puede estar vacío.")

    bloqueos = []
    advertencias = []
    requiere_limpieza_manual = False

    # Regla de confirmación explícita
    if not confirmacion_reset:
        bloqueos.append("Falta confirmación explícita para resetear el contexto de trabajo.")

    # Cambio de cliente_id requiere limpieza manual
    if contexto_actual.cliente_id != contexto_nuevo.cliente_id:
        requiere_limpieza_manual = True

    # Cambio de superficie requiere limpieza manual
    if contexto_actual.superficie != contexto_nuevo.superficie:
        requiere_limpieza_manual = True

    # Cambio de datos_reales_permitidos requiere limpieza manual
    if contexto_actual.datos_reales_permitidos != contexto_nuevo.datos_reales_permitidos:
        requiere_limpieza_manual = True

    # Cambio de campaña genera advertencia
    if contexto_actual.campaña != contexto_nuevo.campaña:
        advertencias.append("Cambio de campaña detectado. Validar relevancia de datos anteriores.")

    # Cambio de fuentes_autorizadas genera advertencia
    if contexto_actual.fuentes_autorizadas != contexto_nuevo.fuentes_autorizadas:
        advertencias.append("Cambio en las fuentes autorizadas detectado. Revisar orígenes de datos.")

    limites_de_inferencia = [
        "Evaluación estática offline V0.",
        "No limpia bases reales ni borra archivos automáticamente.",
        "Requiere confirmación explícita del operador."
    ]

    estado = "BLOQUEADO" if bloqueos else "PASS"
    puede_cambiar = not bool(bloqueos)

    return ResultadoCambioContexto(
        puede_cambiar=puede_cambiar,
        estado=estado,
        motivo=motivo.strip(),
        requiere_limpieza_manual=requiere_limpieza_manual,
        advertencias=advertencias,
        bloqueos=bloqueos,
        limites_de_inferencia=limites_de_inferencia
    )
