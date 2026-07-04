import datetime
from linkedin_content_system.contracts import (
    EntradaContenido, PostCandidato, DiagnosticoEditorial, AprobacionHumana,
    SalidaLocalDraft, ManifestEvidencia, ModoPublicacion, AdaptadorActivo,
    EstadoSalidaLocal, EstadoEvidencia
)
from linkedin_content_system.validators import validar_salida_localdraft_segura

def ensamblar_flujo_local_simulado(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana
) -> tuple[SalidaLocalDraft, ManifestEvidencia]:
    # 1. Ensamblar SalidaLocalDraft
    salida = SalidaLocalDraft(
        post=post,
        diagnostico_editorial=diagnostico,
        aprobacion_humana=aprobacion,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        fecha_objetivo_sugerida=entrada.restricciones.get("fecha_objetivo_sugerida")
    )

    # 2. Validar que la salida sea completamente segura (aprobación, editorial, sanitización)
    validar_salida_localdraft_segura(salida)

    # 3. Ensamblar ManifestEvidencia simulado (en memoria, sin escribir archivos)
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
