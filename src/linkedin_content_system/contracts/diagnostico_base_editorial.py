from typing import Literal
from pydantic import BaseModel, Field, field_validator


class DiagnosticoBaseEditorial(BaseModel):
    """
    Contrato que representa el diagnóstico de base editorial para avanzar en el flujo.
    Este diagnóstico es local, estático y heurístico V0.
    """
    estado: Literal["PASS", "WARN", "FAIL"]
    resumen: str
    hallazgos: list[str] = Field(default_factory=list)
    bloqueos: list[str] = Field(default_factory=list)
    recomendaciones: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("resumen")
    @classmethod
    def validar_resumen(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El resumen no puede estar vacío.")
        return v.strip()

    @field_validator("hallazgos", "bloqueos", "recomendaciones", "limites_de_inferencia")
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
