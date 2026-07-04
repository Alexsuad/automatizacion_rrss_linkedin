from typing import Literal
from pydantic import BaseModel, Field, field_validator


class EvidenciaGeneracion(BaseModel):
    """
    Contrato que representa la evidencia estructurada de generación en memoria.
    """
    id_evidencia: str
    fase: str
    entrada_resumen: str
    salida_resumen: str
    estado: Literal["PASS", "WARN", "FAIL", "BLOQUEADO"]
    artefactos: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    bloqueos: list[str] = Field(default_factory=list)

    @field_validator("id_evidencia", "fase", "entrada_resumen", "salida_resumen")
    @classmethod
    def validar_campos_no_vacios(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío o contener solo espacios.")
        return v.strip()

    @field_validator("artefactos", "advertencias", "bloqueos")
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
