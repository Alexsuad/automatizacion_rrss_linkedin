import datetime
import json
import os
import shutil
import tempfile
from typing import Callable, Optional
from linkedin_content_system.contracts import (
    SalidaLocalDraft,
    ManifestEvidencia,
    EstadoEvidencia,
    EstadoPublicabilidad,
)
from linkedin_content_system.validators import validar_salida_localdraft_segura


_MARCADOR_MOCK_POST = "[BORRADOR SIMULADO DE POST]"

class LocalDraftPublisher:
    def __init__(self, base_dir: str, clock: Optional[Callable[[], str]] = None):
        self.base_dir = os.path.abspath(base_dir)
        self.clock = clock

    def guardar(self, salida: SalidaLocalDraft, id_entrada: str) -> ManifestEvidencia:
        if not id_entrada or not id_entrada.strip():
            raise ValueError("id_entrada inválido: no puede estar vacío.")

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

        if os.path.exists(target_dir):
            raise ValueError(
                f"Acceso denegado: el directorio destino '{os.path.basename(target_dir)}' ya existe."
            )
        temp_dir = tempfile.mkdtemp(prefix=f".localdraft_{id_entrada}_", dir=self.base_dir)

        # Un borrador generado por el mock puede guardarse localmente para revisión,
        # pero no debe persistirse como "publicable".
        if _MARCADOR_MOCK_POST in salida.post.texto:
            salida.estado_publicabilidad = EstadoPublicabilidad.NO_PUBLICABLE

        try:
            # 4. Definir rutas relativas/ficticias
            post_path = os.path.join(temp_dir, "post.md")
            diag_path = os.path.join(temp_dir, "diagnostico.json")
            salida_path = os.path.join(temp_dir, "salida_v1.json")
            manifest_path = os.path.join(temp_dir, "manifest.json")

            # 5. Escribir archivos físicos
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(salida.post.texto)

            with open(diag_path, "w", encoding="utf-8") as f:
                json.dump(salida.diagnostico_editorial.model_dump(), f, indent=2, ensure_ascii=False)

            with open(salida_path, "w", encoding="utf-8") as f:
                json.dump(salida.model_dump(), f, indent=2, ensure_ascii=False)

            # 6. Construir ManifestEvidencia
            timestamp = self.clock() if self.clock else datetime.datetime.now(datetime.timezone.utc).isoformat()

            manifest = ManifestEvidencia(
                id_evidencia=f"ev_{id_entrada}",
                id_entrada=id_entrada,
                archivos_generados=[
                    f"localdraft_{id_entrada}/post.md",
                    f"localdraft_{id_entrada}/diagnostico.json",
                    f"localdraft_{id_entrada}/salida_v1.json",
                    f"localdraft_{id_entrada}/manifest.json"
                ],
                estado=EstadoEvidencia.GUARDADO_LOCAL,
                timestamp=timestamp
            )

            # 7. Escribir manifest.json
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)

            os.replace(temp_dir, target_dir)
            temp_dir = None
            return manifest
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
