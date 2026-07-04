from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.intencion_editorial_clasificada import IntencionEditorialClasificada
from linkedin_content_system.contracts.diagnostico_base_editorial import DiagnosticoBaseEditorial
from linkedin_content_system.contracts.evidencia_contexto_usado import EvidenciaContextoUsado


class ResultadoPipelineContextoOffline(BaseModel):
    """
    Contrato que representa el resultado consolidado del pipeline offline con contexto.
    """
    estado: Literal["PASS", "WARN", "BLOQUEADO", "FAIL"]
    contexto_id: str
    idea_central: IdeaCentral | None = None
    intencion_editorial: IntencionEditorialClasificada | None = None
    diagnostico_base: DiagnosticoBaseEditorial | None = None
    evidencia_contexto: EvidenciaContextoUsado
    bloqueos: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("contexto_id")
    @classmethod
    def validar_contexto_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El contexto_id no puede estar vacío.")
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
    def validar_consistencia(self) -> "ResultadoPipelineContextoOffline":
        if self.estado == "BLOQUEADO":
            if not self.bloqueos:
                raise ValueError("Si el estado es BLOQUEADO, debe existir al menos un bloqueo.")
            if self.idea_central is not None or self.intencion_editorial is not None or self.diagnostico_base is not None:
                raise ValueError("Si el estado es BLOQUEADO, idea_central, intencion_editorial y diagnostico_base deben ser None.")
        elif self.estado == "PASS":
            if self.idea_central is None or self.intencion_editorial is None or self.diagnostico_base is None:
                raise ValueError("Si el estado es PASS, idea_central, intencion_editorial y diagnostico_base deben existir.")
        return self
