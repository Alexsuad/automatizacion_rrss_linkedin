from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ModoTranscripcion(str, Enum):
    FAKE = "fake"
    REAL = "real"
    PENDIENTE = "pendiente"


class EstadoCompletitudTranscripcion(str, Enum):
    COMPLETA = "completa"
    PARCIAL = "parcial"
    PENDIENTE = "pendiente"


class MetadatosAudioLocal(BaseModel):
    referencia_audio: str
    nombre_logico: str
    extension: str
    mime_type: str | None = None
    tamano_bytes: int
    duracion_segundos: float | None = None
    sha256_audio: str
    idioma_declarado: str | None = None

    @model_validator(mode="after")
    def validar_valores(self):
        if self.tamano_bytes <= 0:
            raise ValueError("tamano_bytes debe ser positivo.")
        if self.duracion_segundos is not None and self.duracion_segundos <= 0:
            raise ValueError("duracion_segundos debe ser positiva cuando se informa.")
        return self


class SegmentoTranscripcion(BaseModel):
    indice: int
    texto: str
    inicio_segundos: float | None = None
    fin_segundos: float | None = None

    @model_validator(mode="after")
    def validar_segmento(self):
        if not self.texto.strip():
            raise ValueError("Cada segmento debe contener texto útil.")
        if self.inicio_segundos is not None and self.inicio_segundos < 0:
            raise ValueError("inicio_segundos no puede ser negativo.")
        if self.fin_segundos is not None and self.fin_segundos < 0:
            raise ValueError("fin_segundos no puede ser negativo.")
        if (
            self.inicio_segundos is not None
            and self.fin_segundos is not None
            and self.fin_segundos < self.inicio_segundos
        ):
            raise ValueError("fin_segundos no puede ser menor que inicio_segundos.")
        return self


class ResultadoValidacionAudio(BaseModel):
    audio: MetadatosAudioLocal
    formato_verificado: bool = False
    advertencias: list[str] = Field(default_factory=list)
    tamano_maximo_bytes: int
    duracion_maxima_segundos: float | None = None


class ResultadoTranscripcion(BaseModel):
    adaptador: str
    modo: ModoTranscripcion
    modelo: str | None = None
    idioma: str | None = None
    audio_sha256: str
    texto_bruto: str
    segmentos: list[SegmentoTranscripcion] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    estado_completitud: EstadoCompletitudTranscripcion = EstadoCompletitudTranscripcion.COMPLETA
    causa_saneada: str | None = None

    @model_validator(mode="after")
    def validar_texto(self):
        if self.estado_completitud != EstadoCompletitudTranscripcion.PENDIENTE and not self.texto_bruto.strip():
            raise ValueError("texto_bruto no puede estar vacío cuando existe transcripción.")
        return self


class ResultadoSanitizacionTranscripcion(BaseModel):
    texto_sanitizado: str
    sha256_transcripcion_bruta: str
    sha256_transcripcion_sanitizada: str
    segmentos_sanitizados: list[SegmentoTranscripcion] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    transformaciones: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_resultado(self):
        if not self.texto_sanitizado.strip():
            raise ValueError("texto_sanitizado no puede quedar vacío.")
        return self
