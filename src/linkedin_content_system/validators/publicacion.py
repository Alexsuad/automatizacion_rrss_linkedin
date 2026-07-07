from linkedin_content_system.contracts import (
    AprobacionHumana, EstadoAprobacion, SalidaLocalDraft,
    DiagnosticoEditorial, EstadoRevision, NivelRiesgoGenerico, TipoAprobacion,
)
from linkedin_content_system.contracts.salida import EstadoPublicabilidad
from linkedin_content_system.contracts.trazabilidad import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
)
from .privacidad import validar_texto_sin_pii_basica, validar_texto_sin_secretos_basicos
from .estructural import validar_sin_rutas_locales

def validar_aprobacion_para_publicacion(aprobacion: AprobacionHumana) -> None:
    if aprobacion.estado != EstadoAprobacion.APROBADO:
        raise ValueError(
            f"Publicación denegada: el estado de aprobación humana es '{aprobacion.estado}', se requiere 'aprobado'."
        )

def validar_modo_dry_run_local(salida: SalidaLocalDraft) -> None:
    if salida.modo_publicacion != "dry_run":
        raise ValueError(
            f"Fase V1 Restricción: modo_publicacion debe ser 'dry_run', se recibió '{salida.modo_publicacion}'."
        )
    if salida.adaptador_activo != "localdraft":
        raise ValueError(
            f"Fase V1 Restricción: adaptador_activo debe ser 'localdraft', se recibió '{salida.adaptador_activo}'."
        )
    if salida.estado != "borrador_local":
        raise ValueError(
            f"Fase V1 Restricción: estado de salida debe ser 'borrador_local', se recibió '{salida.estado}'."
        )

def resolver_estado_publicabilidad(
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    diagnostico_trazabilidad: DiagnosticoTrazabilidad | None = None,
) -> EstadoPublicabilidad:
    if diagnostico.bloqueos_criticos:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico.estado_revision == EstadoRevision.FAIL:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico.riesgo_generico == NivelRiesgoGenerico.ALTO:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico.compliance == EstadoRevision.FAIL:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico.autenticidad == EstadoRevision.FAIL:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico_trazabilidad is not None and diagnostico_trazabilidad.estado == EstadoTrazabilidad.FAIL:
        return EstadoPublicabilidad.RECHAZADO_EDITORIAL

    if diagnostico_trazabilidad is None:
        return EstadoPublicabilidad.NO_PUBLICABLE

    if aprobacion.estado != EstadoAprobacion.APROBADO:
        return EstadoPublicabilidad.NO_PUBLICABLE

    if diagnostico_trazabilidad is not None and diagnostico_trazabilidad.estado == EstadoTrazabilidad.WARN:
        if aprobacion.tipo_aprobacion != TipoAprobacion.REFORZADA:
            return EstadoPublicabilidad.REQUIERE_REVISION

    if diagnostico.estado_revision == EstadoRevision.WARN:
        if aprobacion.tipo_aprobacion != TipoAprobacion.REFORZADA:
            return EstadoPublicabilidad.REQUIERE_REVISION
        return EstadoPublicabilidad.PUBLICABLE

    if diagnostico_trazabilidad.estado == EstadoTrazabilidad.WARN:
        if aprobacion.tipo_aprobacion != TipoAprobacion.REFORZADA:
            return EstadoPublicabilidad.REQUIERE_REVISION
        return EstadoPublicabilidad.PUBLICABLE

    return EstadoPublicabilidad.PUBLICABLE


def validar_diagnostico_editorial_publicable(
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    diagnostico_trazabilidad: DiagnosticoTrazabilidad | None = None,
) -> None:
    if diagnostico.riesgo_generico == NivelRiesgoGenerico.ALTO:
        raise ValueError("Publicación denegada: nivel de riesgo genérico es alto.")
    if diagnostico.compliance == EstadoRevision.FAIL:
        raise ValueError("Publicación denegada: compliance es FAIL.")
    if diagnostico.autenticidad == EstadoRevision.FAIL:
        raise ValueError("Publicación denegada: autenticidad es FAIL.")

    if diagnostico_trazabilidad is not None and diagnostico_trazabilidad.estado == EstadoTrazabilidad.FAIL:
        raise ValueError("Publicación denegada: la trazabilidad es FAIL.")

    if diagnostico_trazabilidad is None:
        raise ValueError("Publicación denegada: falta diagnostico_trazabilidad.")

    estado_publicabilidad = resolver_estado_publicabilidad(
        diagnostico,
        aprobacion,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
    )
    if estado_publicabilidad == EstadoPublicabilidad.PUBLICABLE:
        return
    if estado_publicabilidad == EstadoPublicabilidad.REQUIERE_REVISION:
        if diagnostico_trazabilidad is not None and diagnostico_trazabilidad.estado == EstadoTrazabilidad.WARN:
            raise ValueError("Publicación denegada: la trazabilidad requiere aprobación reforzada.")
        raise ValueError(
            "Publicación denegada: el estado_revision es WARN pero no se cuenta con una aprobación reforzada."
        )
    if estado_publicabilidad == EstadoPublicabilidad.RECHAZADO_EDITORIAL:
        if diagnostico.bloqueos_criticos:
            raise ValueError("Publicación denegada: se detectaron bloqueos críticos en el diagnóstico editorial.")
        raise ValueError("Publicación denegada: estado_revision es FAIL.")
    raise ValueError("Publicación denegada: la aprobación humana no está aprobada o falta trazabilidad.")

def _validar_campo_persistible(campo) -> None:
    if campo is None:
        return
    if isinstance(campo, str):
        validar_texto_sin_pii_basica(campo)
        validar_texto_sin_secretos_basicos(campo)
        validar_sin_rutas_locales(campo)
    elif isinstance(campo, list):
        for item in campo:
            _validar_campo_persistible(item)

def validar_textos_persistibles_sin_pii_ni_secretos(salida: SalidaLocalDraft) -> None:
    _validar_campo_persistible(salida.post.texto)
    _validar_campo_persistible(salida.diagnostico_editorial.motivo)
    _validar_campo_persistible(salida.diagnostico_editorial.ajustes_recomendados)
    _validar_campo_persistible(salida.aprobacion_humana.comentarios)
    if salida.diagnostico_trazabilidad is not None:
        _validar_campo_persistible(salida.diagnostico_trazabilidad.resumen)
        for hallazgo in salida.diagnostico_trazabilidad.hallazgos:
            _validar_campo_persistible(hallazgo.fragmento_post)
            _validar_campo_persistible(hallazgo.descripcion)
            _validar_campo_persistible(hallazgo.soporte_encontrado)

def validar_salida_localdraft_segura(salida: SalidaLocalDraft) -> None:
    validar_modo_dry_run_local(salida)
    salida.estado_publicabilidad = resolver_estado_publicabilidad(
        salida.diagnostico_editorial,
        salida.aprobacion_humana,
        diagnostico_trazabilidad=salida.diagnostico_trazabilidad,
    )
    validar_diagnostico_editorial_publicable(
        salida.diagnostico_editorial,
        salida.aprobacion_humana,
        diagnostico_trazabilidad=salida.diagnostico_trazabilidad,
    )
    validar_textos_persistibles_sin_pii_ni_secretos(salida)
