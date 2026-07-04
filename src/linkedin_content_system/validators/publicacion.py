from linkedin_content_system.contracts import (
    AprobacionHumana, EstadoAprobacion, SalidaLocalDraft,
    DiagnosticoEditorial, EstadoRevision, NivelRiesgoGenerico, TipoAprobacion
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

def validar_diagnostico_editorial_publicable(diagnostico: DiagnosticoEditorial, aprobacion: AprobacionHumana) -> None:
    # 1. FAIL bloquea siempre
    # 1. bloqueos_criticos no vacío bloquea siempre
    if diagnostico.bloqueos_criticos:
        raise ValueError("Publicación denegada: se detectaron bloqueos críticos en el diagnóstico editorial.")

    # 2. FAIL bloquea siempre
    if diagnostico.estado_revision == EstadoRevision.FAIL:
        raise ValueError("Publicación denegada: estado_revision es FAIL.")


    # 3. riesgo_generico alto bloquea
    if diagnostico.riesgo_generico == NivelRiesgoGenerico.ALTO:
        raise ValueError("Publicación denegada: nivel de riesgo genérico es alto.")

    # 4. compliance FAIL bloquea
    if diagnostico.compliance == EstadoRevision.FAIL:
        raise ValueError("Publicación denegada: compliance es FAIL.")

    # 5. autenticidad FAIL bloquea
    if diagnostico.autenticidad == EstadoRevision.FAIL:
        raise ValueError("Publicación denegada: autenticidad es FAIL.")

    # 6. estado_revision WARN requiere aprobación reforzada
    if diagnostico.estado_revision == EstadoRevision.WARN:
        if aprobacion.tipo_aprobacion != TipoAprobacion.REFORZADA:
            raise ValueError(
                "Publicación denegada: el estado_revision es WARN pero no se cuenta con una aprobación reforzada."
            )

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

def validar_salida_localdraft_segura(salida: SalidaLocalDraft) -> None:
    validar_aprobacion_para_publicacion(salida.aprobacion_humana)
    validar_modo_dry_run_local(salida)
    validar_diagnostico_editorial_publicable(salida.diagnostico_editorial, salida.aprobacion_humana)
    validar_textos_persistibles_sin_pii_ni_secretos(salida)
