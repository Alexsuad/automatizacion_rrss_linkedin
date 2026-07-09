from typing import Protocol, runtime_checkable

from linkedin_content_system.contracts import ManifestEvidencia, SalidaLocalDraft


@runtime_checkable
class PublicationPublisherPort(Protocol):
    def guardar(self, salida: SalidaLocalDraft, id_entrada: str) -> ManifestEvidencia:
        """Persiste o prepara una salida de publicacion en modo seguro y local."""
