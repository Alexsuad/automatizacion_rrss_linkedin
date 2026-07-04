from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.contracts.compatibilidad_contexto import ResultadoCompatibilidadContexto


def validar_compatibilidad_contexto(
    contexto: ContextoTrabajo,
    cliente_id_operacion: str,
    superficie_operacion: str,
    fuentes_usadas: list[str] | None = None,
    datos_reales_detectados: bool = False,
) -> ResultadoCompatibilidadContexto:
    """
    Valida de forma determinista si una operación declarada es compatible con el contexto de trabajo activo,
    previniendo contaminación entre clientes, superficies, fuentes y datos reales no autorizados.
    """
    if contexto is None:
        raise ValueError("El contexto no puede ser None.")

    if cliente_id_operacion is None or not cliente_id_operacion.strip():
        raise ValueError("cliente_id_operacion no puede estar vacío.")

    if superficie_operacion is None or not superficie_operacion.strip():
        raise ValueError("superficie_operacion no puede estar vacía.")

    fuentes = fuentes_usadas if fuentes_usadas is not None else []
    bloqueos = []

    # Validar cliente_id
    if cliente_id_operacion.strip() != contexto.cliente_id:
        bloqueos.append(
            f"cliente_id_operacion '{cliente_id_operacion.strip()}' no coincide con el cliente del contexto '{contexto.cliente_id}'."
        )

    # Validar superficie
    if superficie_operacion.strip() != contexto.superficie:
        bloqueos.append(
            f"superficie_operacion '{superficie_operacion.strip()}' no coincide con la superficie del contexto '{contexto.superficie}'."
        )

    # Validar datos reales permitidos
    if datos_reales_detectados and not contexto.datos_reales_permitidos:
        bloqueos.append(
            "Se detectaron datos reales pero el contexto actual no los permite."
        )

    # Validar fuentes autorizadas
    for fuente in fuentes:
        if fuente.strip() not in contexto.fuentes_autorizadas:
            bloqueos.append(
                f"La fuente '{fuente.strip()}' no está autorizada en el contexto activo."
            )

    if bloqueos:
        return ResultadoCompatibilidadContexto(
            compatible=False,
            estado="BLOQUEADO",
            motivo=f"Incompatibilidad detectada con el contexto activo: {len(bloqueos)} bloqueos.",
            bloqueos=bloqueos,
            advertencias=[],
            limites_de_inferencia=["Validación determinista local sin acceso a servicios externos."]
        )

    return ResultadoCompatibilidadContexto(
        compatible=True,
        estado="PASS",
        motivo="Compatibilidad de contexto validada correctamente.",
        bloqueos=[],
        advertencias=[],
        limites_de_inferencia=["Validación determinista local sin acceso a servicios externos."]
    )
