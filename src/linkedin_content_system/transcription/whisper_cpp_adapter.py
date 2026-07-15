from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from linkedin_content_system.contracts.audio_transcripcion import (
    EstadoCompletitudTranscripcion,
    ModoTranscripcion,
    ResultadoTranscripcion,
    SegmentoTranscripcion,
)
from linkedin_content_system.transcription.ports import (
    AudioTranscriber,
    TranscriptionConfigurationError,
    TranscriptionDependencyError,
    TranscriptionExecutionError,
    TranscriptionResponseError,
)


class WhisperCppTranscriptionAdapter(AudioTranscriber):
    nombre = "whisper_cpp"
    modo = ModoTranscripcion.REAL.value
    supported_extensions = {".wav"}

    def __init__(
        self,
        *,
        model_path: str | None = None,
        binary_path: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.binary_path = (binary_path or os.getenv("LINKEDIN_CONTENT_TRANSCRIPTION_BINARY") or "whisper-cli").strip()
        self.model_path = (model_path or os.getenv("LINKEDIN_CONTENT_TRANSCRIPTION_MODEL_PATH") or "").strip()
        self.timeout_seconds = float(timeout_seconds or os.getenv("LINKEDIN_CONTENT_TRANSCRIPTION_TIMEOUT_SECONDS", "120"))

        if self.timeout_seconds <= 0:
            raise TranscriptionConfigurationError("El timeout de transcripción debe ser positivo.")
        if not self.model_path:
            raise TranscriptionConfigurationError(
                "Falta configurar LINKEDIN_CONTENT_TRANSCRIPTION_MODEL_PATH para el adaptador real."
            )
        model_file = Path(self.model_path).expanduser()
        if not model_file.exists() or not model_file.is_file():
            raise TranscriptionConfigurationError(
                "El modelo local de whisper.cpp no existe o no es un archivo."
            )

    def transcribir(
        self,
        audio_path: Path,
        *,
        audio_sha256: str,
        language: str | None = None,
    ) -> ResultadoTranscripcion:
        if shutil.which(self.binary_path) is None:
            raise TranscriptionDependencyError(
                "El binario whisper-cli no está disponible en el entorno local."
            )

        with tempfile.TemporaryDirectory(prefix="whispercpp_") as temp_dir:
            output_prefix = str(Path(temp_dir) / "transcripcion")
            command = [
                self.binary_path,
                "-m",
                self.model_path,
                "-f",
                str(audio_path),
                "-oj",
                "-of",
                output_prefix,
            ]
            if language:
                command.extend(["-l", language])
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise TranscriptionExecutionError(
                    "La transcripción local superó el timeout configurado."
                ) from exc

            if completed.returncode != 0:
                raise TranscriptionExecutionError(
                    "El motor local de transcripción no pudo procesar el audio."
                )

            json_path = Path(f"{output_prefix}.json")
            if not json_path.exists():
                raise TranscriptionResponseError(
                    "El motor local no produjo un JSON de transcripción usable."
                )
            data = json.loads(json_path.read_text(encoding="utf-8"))
            segmentos = []
            for indice, segmento in enumerate(data.get("transcription", []), start=1):
                segmentos.append(
                    SegmentoTranscripcion(
                        indice=indice,
                        texto=str(segmento.get("text") or "").strip(),
                        inicio_segundos=float(segmento["offsets"]["from"]) / 1000
                        if segmento.get("offsets", {}).get("from") is not None
                        else None,
                        fin_segundos=float(segmento["offsets"]["to"]) / 1000
                        if segmento.get("offsets", {}).get("to") is not None
                        else None,
                    )
                )
            texto = str(data.get("text") or "").strip()
            if not texto:
                texto = " ".join(segmento.texto.strip() for segmento in segmentos if segmento.texto.strip()).strip()
            if not texto:
                raise TranscriptionResponseError("La transcripción local quedó vacía.")
            return ResultadoTranscripcion(
                adaptador=self.nombre,
                modo=ModoTranscripcion.REAL,
                modelo=Path(self.model_path).name,
                idioma=language,
                audio_sha256=audio_sha256,
                texto_bruto=texto,
                segmentos=[segmento for segmento in segmentos if segmento.texto],
                advertencias=[],
                estado_completitud=EstadoCompletitudTranscripcion.COMPLETA,
            )
