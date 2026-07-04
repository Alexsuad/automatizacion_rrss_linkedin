from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class EvidenciaContextoUsado(BaseModel):
    """
    Contrato que representa la evidencia del contexto de trabajo utilizado en una operación.
    Permite auditar el cumplimiento de límites de contaminación y aislamiento de datos.
    """
    id_evidencia: str
    contexto_id: str
    cliente_id: str
    superficie: Literal["linkedin_personal", "linkedin_empresa", "general"]
    campaña: str | None = None
    nombre_operacion: str
    resultado_operacion: Literal["PASS", "WARN", "BLOQUEADO", "FAIL"]
    datos_reales_permitidos: bool
    fuentes_autorizadas: list[str] = Field(default_factory=list)
    artefactos_generados: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    bloqueos: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("id_evidencia", "contexto_id", "cliente_id", "nombre_operacion")
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

    @field_validator(
        "fuentes_autorizadas",
        "artefactos_generados",
        "advertencias",
        "bloqueos",
        "limites_de_inferencia",
    )
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
    def validar_consistencia_resultado(self) -> "EvidenciaContextoUsado":
        if self.resultado_operacion == "BLOQUEADO":
            if not self.bloqueos:
                raise ValueError(
                    "Si el resultado es BLOQUEADO, debe existir al menos un bloqueo."
                )
        elif self.resultado_operacion == "FAIL":
            if not self.bloqueos and not self.advertencias:
                raise ValueError(
                    "Si el resultado es FAIL, debe existir al menos un bloqueo o advertencia."
                )
        return self
