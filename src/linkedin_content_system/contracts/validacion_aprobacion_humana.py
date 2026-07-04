from typing import Literal, Optional
from pydantic import BaseModel, model_validator


class DecisionAprobacionHumana(BaseModel):
    estado: Literal["pendiente", "aprobado_simple", "aprobado_reforzado", "rechazado"]
    revisor: Optional[str] = None
    motivo: Optional[str] = None
    confirmacion_explicita: bool = False

    @model_validator(mode="after")
    def validar_campos(self) -> "DecisionAprobacionHumana":
        if self.revisor is not None and not self.revisor.strip():
            raise ValueError("revisor, si se proporciona, no puede estar vacío.")
        if self.motivo is not None and not self.motivo.strip():
            raise ValueError("motivo, si se proporciona, no puede estar vacío.")
        return self


class ResultadoValidacionAprobacionHumana(BaseModel):
    puede_avanzar: bool
    requiere_revision_adicional: bool
    estado_publicabilidad: Literal[
        "no_publicable",
        "publicable_con_aprobacion_simple",
        "publicable_con_aprobacion_reforzada",
    ]
    motivo: str

    @model_validator(mode="after")
    def validar_resultado(self) -> "ResultadoValidacionAprobacionHumana":
        if not self.motivo or not self.motivo.strip():
            raise ValueError("motivo del resultado no puede estar vacío.")
        return self
