from typing import Callable, Optional
from linkedin_content_system.contracts import (
    EntradaContenido, PostCandidato, DiagnosticoEditorial, AprobacionHumana, ManifestEvidencia
)
from linkedin_content_system.flows import ensamblar_flujo_local_simulado
from linkedin_content_system.publishers import LocalDraftPublisher

def generar_borrador_local_desde_simulacion(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    base_dir: str,
    clock: Optional[Callable[[], str]] = None
) -> ManifestEvidencia:
    # 1. Ejecutar flujo local simulado en memoria (aplica validaciones de post y aprobación)
    salida, _ = ensamblar_flujo_local_simulado(entrada, post, diagnostico, aprobacion)

    # 2. Instanciar publicador localdraft
    publisher = LocalDraftPublisher(base_dir=base_dir, clock=clock)

    # 3. Guardar salida físicamente en disco (aplica validaciones de path traversal y de salida segura)
    manifest = publisher.guardar(salida, entrada.id_entrada)

    return manifest
