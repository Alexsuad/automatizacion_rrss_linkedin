import os
import datetime
import json
from typing import Callable, Optional
from linkedin_content_system.contracts import SalidaLocalDraft, ManifestEvidencia, EstadoEvidencia
from linkedin_content_system.validators import validar_salida_localdraft_segura

class LocalDraftPublisher:
    def __init__(self, base_dir: str, clock: Optional[Callable[[], str]] = None):
        self.base_dir = os.path.abspath(base_dir)
        self.clock = clock

    def guardar(self, salida: SalidaLocalDraft, id_entrada: str) -> ManifestEvidencia:
        # 1. Validar id_entrada contra path traversal
        for char in ("/", "\\", "..", ":"):
            if char in id_entrada:
                raise ValueError(f"id_entrada inválido: contiene caracteres prohibidos '{char}'")

        # 2. Validar que la salida sea segura localmente (PII, secretos, rutas locales, aprobación)
        validar_salida_localdraft_segura(salida)

        # 3. Establecer y crear el directorio destino
        target_dir = os.path.abspath(os.path.join(self.base_dir, f"localdraft_{id_entrada}"))
        
        # Validar que el directorio destino esté estrictamente dentro de base_dir
        if os.path.commonpath([self.base_dir, target_dir]) != self.base_dir:
            raise ValueError("Acceso denegado: intento de escribir fuera del directorio base.")

        os.makedirs(target_dir, exist_ok=True)

        # 4. Definir rutas relativas/ficticias
        post_path = os.path.join(target_dir, "post.md")
        diag_path = os.path.join(target_dir, "diagnostico.json")
        manifest_path = os.path.join(target_dir, "manifest.json")

        # 5. Escribir archivos físicos
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(salida.post.texto)

        with open(diag_path, "w", encoding="utf-8") as f:
            json.dump(salida.diagnostico_editorial.model_dump(), f, indent=2, ensure_ascii=False)

        # 6. Construir ManifestEvidencia
        timestamp = self.clock() if self.clock else datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        manifest = ManifestEvidencia(
            id_evidencia=f"ev_{id_entrada}",
            id_entrada=id_entrada,
            archivos_generados=[
                f"localdraft_{id_entrada}/post.md",
                f"localdraft_{id_entrada}/diagnostico.json",
                f"localdraft_{id_entrada}/manifest.json"
            ],
            estado=EstadoEvidencia.GUARDADO_LOCAL,
            timestamp=timestamp
        )

        # 7. Escribir manifest.json
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)

        return manifest
