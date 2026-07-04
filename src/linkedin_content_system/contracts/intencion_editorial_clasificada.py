from typing import Literal

from pydantic import BaseModel, Field, field_validator


TipoIntencionEditorial = Literal[
    "compartir_aprendizaje",
    "explicar_idea",
    "posicionar_opinion",
    "contar_experiencia",
    "abrir_conversacion",
    "indeterminada",
]


class IntencionEditorialClasificada(BaseModel):
    """
    Contrato que representa la intención editorial clasificada a partir de la IdeaCentral.
    Evita colisiones con la intención editorial histórica de entrada.
    """
    intencion_principal: TipoIntencionEditorial
    resumen_intencion: str
    justificacion: str
    confianza: Literal["baja", "media", "alta"] = "baja"
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("resumen_intencion", "justificacion")
    @classmethod
    def no_vacio(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("El campo no puede estar vacío.")
        return value.strip()

    @field_validator("limites_de_inferencia")
    @classmethod
    def limites_sin_elementos_vacios(cls, value: list[str]) -> list[str]:
        for item in value:
            if not item or not item.strip():
                raise ValueError("Los límites de inferencia no pueden contener elementos vacíos.")
        return [item.strip() for item in value]
