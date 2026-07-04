from linkedin_content_system.contracts.validacion_aprobacion_humana import (
    DecisionAprobacionHumana,
    ResultadoValidacionAprobacionHumana,
)


def validar_aprobacion_humana(
    aprobacion: DecisionAprobacionHumana,
    requiere_aprobacion_reforzada: bool,
) -> ResultadoValidacionAprobacionHumana:
    """
    Valida de forma determinista si el contenido puede avanzar en el flujo de publicación
    según la decisión de aprobación humana y las reglas de negocio establecidas.
    """
    if aprobacion is None:
        raise ValueError("aprobacion no puede ser None")

    estado = aprobacion.estado

    if estado == "pendiente":
        return ResultadoValidacionAprobacionHumana(
            puede_avanzar=False,
            requiere_revision_adicional=True,
            estado_publicabilidad="no_publicable",
            motivo="El contenido está pendiente de revisión."
        )

    elif estado == "rechazado":
        motivo_rechazo = aprobacion.motivo or "El contenido ha sido rechazado."
        return ResultadoValidacionAprobacionHumana(
            puede_avanzar=False,
            requiere_revision_adicional=False,
            estado_publicabilidad="no_publicable",
            motivo=motivo_rechazo
        )

    elif estado == "aprobado_simple":
        if requiere_aprobacion_reforzada:
            return ResultadoValidacionAprobacionHumana(
                puede_avanzar=False,
                requiere_revision_adicional=True,
                estado_publicabilidad="no_publicable",
                motivo="Se requiere aprobación reforzada, pero solo se tiene aprobación simple."
            )
        else:
            return ResultadoValidacionAprobacionHumana(
                puede_avanzar=True,
                requiere_revision_adicional=False,
                estado_publicabilidad="publicable_con_aprobacion_simple",
                motivo="Aprobado de forma simple."
            )

    elif estado == "aprobado_reforzado":
        if aprobacion.confirmacion_explicita:
            return ResultadoValidacionAprobacionHumana(
                puede_avanzar=True,
                requiere_revision_adicional=False,
                estado_publicabilidad="publicable_con_aprobacion_reforzada",
                motivo="Aprobado de forma reforzada con confirmación explícita."
            )
        else:
            return ResultadoValidacionAprobacionHumana(
                puede_avanzar=False,
                requiere_revision_adicional=True,
                estado_publicabilidad="no_publicable",
                motivo="Aprobación reforzada requiere confirmación explícita."
            )

    else:
        raise ValueError(f"Estado de aprobación no soportado: {estado}")

