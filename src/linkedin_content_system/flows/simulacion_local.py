import datetime
from linkedin_content_system.contracts import (
    EntradaContenido, PostCandidato, DiagnosticoEditorial, AprobacionHumana,
    SalidaLocalDraft, ManifestEvidencia, ModoPublicacion, AdaptadorActivo,
    EstadoSalidaLocal, EstadoEvidencia
)
from linkedin_content_system.validators import (
    validar_texto_sin_pii_basica, validar_texto_sin_secretos_basicos,
    validar_sin_rutas_locales, validar_texto_no_vacio,
    validar_aprobacion_para_publicacion
)

def ensamblar_flujo_local_simulado(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana
) -> tuple[SalidaLocalDraft, ManifestEvidencia]:
    # 1. Validar texto del post candidato
    validar_texto_no_vacio(post.texto)
    validar_texto_sin_pii_basica(post.texto)
    validar_texto_sin_secretos_basicos(post.texto)
    validar_sin_rutas_locales(post.texto)

    # 2. Validar aprobación
    validar_aprobacion_para_publicacion(aprobacion)

    # 3. Ensamblar SalidaLocalDraft
    salida = SalidaLocalDraft(
        post=post,
        diagnostico_editorial=diagnostico,
        aprobacion_humana=aprobacion,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        fecha_objetivo_sugerida=entrada.restricciones.get("fecha_objetivo_sugerida")
    )

    # 4. Ensamblar ManifestEvidencia simulado (en memoria, sin escribir archivos)
    manifest = ManifestEvidencia(
        id_evidencia=f"ev_{entrada.id_entrada}",
        id_entrada=entrada.id_entrada,
        archivos_generados=[
            "output/simulado/post.md",
            "output/simulado/manifest.json"
        ],
        estado=EstadoEvidencia.GUARDADO_LOCAL,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    return salida, manifest
