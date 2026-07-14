from __future__ import annotations

import os

from linkedin_content_system.transcription.fake_adapter import FakeFixtureTranscriptionAdapter
from linkedin_content_system.transcription.ports import (
    AudioTranscriber,
    TranscriptionAdapterError,
    TranscriptionConfigurationError,
    TranscriptionDependencyError,
    TranscriptionExecutionError,
    TranscriptionInputError,
    TranscriptionResponseError,
)
from linkedin_content_system.transcription.whisper_cpp_adapter import WhisperCppTranscriptionAdapter


def construir_transcriber(modo: str | None = None) -> AudioTranscriber:
    modo_resuelto = (modo or os.getenv("LINKEDIN_CONTENT_TRANSCRIPTION_ADAPTER", "fake")).strip().lower()
    if modo_resuelto == "fake":
        return FakeFixtureTranscriptionAdapter()
    if modo_resuelto in {"whisper_cpp", "whisper-cpp"}:
        return WhisperCppTranscriptionAdapter()
    raise TranscriptionConfigurationError(
        "Modo de transcripción desconocido. Valores admitidos: fake, whisper_cpp."
    )


__all__ = [
    "AudioTranscriber",
    "FakeFixtureTranscriptionAdapter",
    "WhisperCppTranscriptionAdapter",
    "TranscriptionAdapterError",
    "TranscriptionConfigurationError",
    "TranscriptionDependencyError",
    "TranscriptionExecutionError",
    "TranscriptionInputError",
    "TranscriptionResponseError",
    "construir_transcriber",
]
