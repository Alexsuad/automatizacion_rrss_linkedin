from __future__ import annotations

import json
from pathlib import Path

from linkedin_content_system.contracts.audio_transcripcion import (
    EstadoCompletitudTranscripcion,
    ModoTranscripcion,
    ResultadoTranscripcion,
    SegmentoTranscripcion,
)
from linkedin_content_system.transcription.ports import (
    AudioTranscriber,
    TranscriptionInputError,
    TranscriptionResponseError,
)


class FakeFixtureTranscriptionAdapter(AudioTranscriber):
    nombre = "fake_fixture"
    modo = ModoTranscripcion.FAKE.value
    supported_extensions = {".wav", ".ogg", ".mp3"}

    def transcribir(
        self,
        audio_path: Path,
        *,
        audio_sha256: str,
        language: str | None = None,
    ) -> ResultadoTranscripcion:
        sidecar = audio_path.with_name(f"{audio_path.name}.transcription.json")
        if not sidecar.exists():
            raise TranscriptionInputError(
                "El adaptador fake requiere un fixture de transcripción junto al audio."
            )

        data = json.loads(sidecar.read_text(encoding="utf-8"))
        if data.get("audio_sha256") != audio_sha256:
            raise TranscriptionResponseError(
                "La transcripción fake no corresponde al hash del audio suministrado."
            )
        texto = str(data.get("texto") or "").strip()
        if not texto:
            raise TranscriptionResponseError("La transcripción fake está vacía.")
        segmentos = [
            SegmentoTranscripcion.model_validate(segmento)
            for segmento in data.get("segmentos", [])
        ]
        return ResultadoTranscripcion(
            adaptador=self.nombre,
            modo=ModoTranscripcion.FAKE,
            modelo="fixture_sidecar_v1",
            idioma=str(data.get("idioma") or language or "").strip() or None,
            audio_sha256=audio_sha256,
            texto_bruto=texto,
            segmentos=segmentos,
            advertencias=[str(item) for item in data.get("advertencias", []) if str(item).strip()],
            estado_completitud=EstadoCompletitudTranscripcion(
                data.get("estado_completitud", EstadoCompletitudTranscripcion.COMPLETA.value)
            ),
            causa_saneada=str(data.get("causa_saneada")).strip() if data.get("causa_saneada") else None,
        )
