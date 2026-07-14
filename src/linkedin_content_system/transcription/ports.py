from __future__ import annotations

from pathlib import Path
from typing import Protocol

from linkedin_content_system.contracts.audio_transcripcion import ResultadoTranscripcion


class TranscriptionAdapterError(RuntimeError):
    """Error base para la transcripción local."""


class TranscriptionConfigurationError(TranscriptionAdapterError):
    """Configuración inválida del adaptador de transcripción."""


class TranscriptionInputError(TranscriptionAdapterError):
    """Entrada de audio inválida o no autorizada."""


class TranscriptionDependencyError(TranscriptionAdapterError):
    """Dependencia local ausente para el adaptador real."""


class TranscriptionExecutionError(TranscriptionAdapterError):
    """Fallo del motor local durante la ejecución."""


class TranscriptionResponseError(TranscriptionAdapterError):
    """La respuesta del motor local no es usable."""


class AudioTranscriber(Protocol):
    nombre: str
    modo: str
    supported_extensions: set[str]

    def transcribir(
        self,
        audio_path: Path,
        *,
        audio_sha256: str,
        language: str | None = None,
    ) -> ResultadoTranscripcion:
        """Transcribe un audio local previamente validado."""
