from linkedin_content_system.contracts import AprobacionHumana, EstadoAprobacion, SalidaLocalDraft
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

def validar_salida_localdraft_segura(salida: SalidaLocalDraft) -> None:
    validar_aprobacion_para_publicacion(salida.aprobacion_humana)
    validar_modo_dry_run_local(salida)
    # Validar que el texto del post no tiene PII, secretos o rutas absolutas
    post_texto = salida.post.texto
    validar_texto_sin_pii_basica(post_texto)
    validar_texto_sin_secretos_basicos(post_texto)
    validar_sin_rutas_locales(post_texto)
