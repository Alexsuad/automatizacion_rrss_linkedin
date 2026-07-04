from typing import Literal
from pydantic import BaseModel, Field, model_validator, field_validator


class ResultadoCompatibilidadContexto(BaseModel):
    compatible: bool
    estado: Literal["PASS", "WARN", "BLOQUEADO"]
    motivo: str
    bloqueos: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("motivo")
    @classmethod
    def validar_motivo(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El motivo no puede estar vacío.")
        return v.strip()

    @field_validator("bloqueos", "advertencias", "limites_de_inferencia")
    @classmethod
    def validar_listas(cls, v: list[str]) -> list[str]:
        cleaned = []
        for item in v:
            if not isinstance(item, str):
                raise ValueError("Todos los elementos de la lista deben ser strings.")
            if not item or not item.strip():
                raise ValueError("La lista no puede contener strings vacíos o con solo espacios.")
            cleaned.append(item.strip())
        return cleaned

    @model_validator(mode="after")
    def validar_consistencia(self) -> "ResultadoCompatibilidadContexto":
        if self.estado == "BLOQUEADO" and self.compatible:
            raise ValueError("Si el estado es BLOQUEADO, compatible debe ser False.")
        if not self.compatible and not self.bloqueos:
            raise ValueError("Si compatible es False, debe existir al menos un bloqueo.")
        return self
