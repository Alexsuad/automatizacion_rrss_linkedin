import datetime
from linkedin_content_system.contracts import (
    EntradaContenido, PostCandidato, DiagnosticoEditorial, AprobacionHumana,
    SalidaLocalDraft, ManifestEvidencia, ModoPublicacion, AdaptadorActivo,
    EstadoSalidaLocal, EstadoEvidencia
)
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.validators.trazabilidad import validar_trazabilidad_fuerte
from linkedin_content_system.validators import validar_salida_localdraft_segura

def ensamblar_flujo_local_simulado(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    diagnostico_trazabilidad=None,
) -> tuple[SalidaLocalDraft, ManifestEvidencia]:
    if diagnostico_trazabilidad is None:
        idea_texto = entrada.intencion_editorial.idea_central or entrada.texto_base
        diagnostico_trazabilidad = validar_trazabilidad_fuerte(
            entrada=entrada,
            idea_central=IdeaCentral(
                idea_central=idea_texto,
                resumen_operativo=idea_texto,
                puntos_de_soporte=[entrada.texto_base],
                limites_de_inferencia=entrada.restricciones.get("limites_de_inferencia", []),
            ),
            post=post,
            contexto_permitido=entrada.restricciones.get("contexto_permitido"),
        )

    # 1. Ensamblar SalidaLocalDraft
    salida = SalidaLocalDraft(
        post=post,
        diagnostico_editorial=diagnostico,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
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
