from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ResultadoCambioContexto(BaseModel):
    """
    Contrato que representa el resultado de validar un cambio de contexto de trabajo.
    """
    puede_cambiar: bool
    estado: Literal["PASS", "BLOQUEADO"]
    motivo: str
    requiere_limpieza_manual: bool
    advertencias: list[str] = Field(default_factory=list)
    bloqueos: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("motivo")
    @classmethod
    def validar_motivo(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El motivo no puede estar vacío.")
        return v.strip()

    @field_validator("advertencias", "bloqueos", "limites_de_inferencia")
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
    def validar_consistencia(self) -> "ResultadoCambioContexto":
        if self.estado == "BLOQUEADO" and self.puede_cambiar:
            raise ValueError("Si el estado es BLOQUEADO, puede_cambiar debe ser False.")
        if not self.puede_cambiar and not self.bloqueos:
            raise ValueError("Si puede_cambiar es False, debe existir al menos un bloqueo.")
        return self
