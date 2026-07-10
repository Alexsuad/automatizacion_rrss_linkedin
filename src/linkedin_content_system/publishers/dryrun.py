import datetime
import json
import os
import shutil
import tempfile
from typing import Callable, Optional

from linkedin_content_system.contracts import (
    EstadoEvidencia,
    ManifestEvidencia,
    SalidaLocalDraft,
)
from linkedin_content_system.publishers.ports import PublicationPublisherPort
from linkedin_content_system.validators import validar_salida_localdraft_segura


_PROVEEDOR_SIMULADO = "simulated_external"
_MODO_DRY_RUN = "dry_run"


class ExternalDryRunPublisher(PublicationPublisherPort):
    def __init__(
        self,
        base_dir: str,
        clock: Optional[Callable[[], str]] = None,
        canal_destino: str = "linkedin",
    ):
        self.base_dir = os.path.abspath(base_dir)
        self.clock = clock
        self.canal_destino = canal_destino.strip().lower() if canal_destino and canal_destino.strip() else "linkedin"

    def guardar(self, salida: SalidaLocalDraft, id_entrada: str) -> ManifestEvidencia:
        if not id_entrada or not id_entrada.strip():
            raise ValueError("id_entrada inválido: no puede estar vacío.")

        for char in ("/", "\\", "..", ":"):
            if char in id_entrada:
                raise ValueError(f"id_entrada inválido: contiene caracteres prohibidos '{char}'")

        validar_salida_localdraft_segura(salida)

        target_dir = os.path.abspath(os.path.join(self.base_dir, f"external_dryrun_{id_entrada}"))
        if os.path.commonpath([self.base_dir, target_dir]) != self.base_dir:
            raise ValueError("Acceso denegado: intento de escribir fuera del directorio base.")

        if os.path.exists(target_dir):
            raise ValueError(
                f"Acceso denegado: el directorio destino '{os.path.basename(target_dir)}' ya existe."
            )
        temp_dir = tempfile.mkdtemp(prefix=f".external_dryrun_{id_entrada}_", dir=self.base_dir)

        try:
            canal_destino = getattr(salida, "canal_destino", None) or self.canal_destino
            timestamp = self.clock() if self.clock else datetime.datetime.now(datetime.timezone.utc).isoformat()
            id_externo_simulado = f"dryrun-{id_entrada}"

            payload = {
                "modo": _MODO_DRY_RUN,
                "proveedor": _PROVEEDOR_SIMULADO,
                "canal_destino": canal_destino,
                "no_publicado_realmente": True,
                "id_entrada": id_entrada,
                "id_externo_simulado": id_externo_simulado,
                "timestamp": timestamp,
                "estado_publicabilidad_origen": salida.estado_publicabilidad.value,
                "salida_origen": salida.model_dump(),
            }

            payload_path = os.path.join(temp_dir, "publicacion_simulada.json")
            manifest_path = os.path.join(temp_dir, "manifest.json")

            with open(payload_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            manifest = ManifestEvidencia(
                id_evidencia=f"ev_external_{id_entrada}",
                id_entrada=id_entrada,
                archivos_generados=[
                    f"external_dryrun_{id_entrada}/publicacion_simulada.json",
                    f"external_dryrun_{id_entrada}/manifest.json",
                ],
                estado=EstadoEvidencia.GUARDADO_LOCAL,
                timestamp=timestamp,
            )

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)

            os.replace(temp_dir, target_dir)
            temp_dir = None
            return manifest
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
