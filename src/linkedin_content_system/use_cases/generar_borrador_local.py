from typing import Callable, Optional
from linkedin_content_system.contracts import (
    EntradaContenido, PostCandidato, DiagnosticoEditorial, AprobacionHumana, ManifestEvidencia
)
from linkedin_content_system.flows import ensamblar_flujo_local_simulado
from linkedin_content_system.publishers import LocalDraftPublisher, PublicationPublisherPort

def generar_borrador_local_desde_simulacion(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    base_dir: str | None = None,
    clock: Optional[Callable[[], str]] = None,
    diagnostico_trazabilidad=None,
    publisher: PublicationPublisherPort | None = None,
    trazabilidad_editorial: dict | None = None,
) -> ManifestEvidencia:
    # 1. Ejecutar flujo local simulado en memoria (aplica validaciones de post y aprobación)
    salida, _ = ensamblar_flujo_local_simulado(
        entrada,
        post,
        diagnostico,
        aprobacion,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
    )
    salida.trazabilidad_editorial = trazabilidad_editorial

    # 2. Resolver publicador desde la composición; si no llega, mantener compatibilidad.
    publisher_resuelto = publisher
    if publisher_resuelto is None:
        if not base_dir:
            raise ValueError("base_dir es obligatorio cuando no se inyecta un publisher.")
        publisher_resuelto = LocalDraftPublisher(base_dir=base_dir, clock=clock)

    # 3. Guardar salida físicamente en disco (aplica validaciones de path traversal y de salida segura)
    manifest = publisher_resuelto.guardar(salida, entrada.id_entrada)

    return manifest
