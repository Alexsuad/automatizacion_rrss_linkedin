from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ContextoTrabajo(BaseModel):
    """
    Contrato que representa un contexto activo de trabajo aislado
    para prevenir contaminación de PII o clientes cruzados.
    """
    contexto_id: str
    cliente_id: str
    superficie: Literal["linkedin_personal", "linkedin_empresa", "general"]
    campaña: str | None = None
    fuentes_autorizadas: list[str] = Field(default_factory=list)
    datos_reales_permitidos: bool = False
    estado: Literal["activo", "bloqueado"]
    notas_seguridad: list[str] = Field(default_factory=list)

    @field_validator("contexto_id", "cliente_id")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("campaña")
    @classmethod
    def campaña_no_vacia(cls, v: str | None) -> str | None:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("La campaña, si se proporciona, no puede estar vacía.")
            return v.strip()
        return v

    @field_validator("fuentes_autorizadas", "notas_seguridad")
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
