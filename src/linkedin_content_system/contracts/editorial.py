from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

class EstadoRevision(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

class NivelRiesgoGenerico(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

class TipoBloqueoCritico(str, Enum):
    PII = "PII"
    SECRETO = "SECRETO"
    CLAIM_SIN_FUENTE = "CLAIM_SIN_FUENTE"
    RIESGO_REPUTACIONAL = "RIESGO_REPUTACIONAL"
    COMPLIANCE = "COMPLIANCE"
    TRAZABILIDAD = "TRAZABILIDAD"
    SIN_APROBACION = "SIN_APROBACION"

class BloqueoCritico(BaseModel):
    tipo: TipoBloqueoCritico
    descripcion: str

class DiagnosticoEditorial(BaseModel):
    claridad_idea: EstadoRevision
    audiencia: EstadoRevision
    hook: EstadoRevision
    voz_cliente: EstadoRevision
    autenticidad: EstadoRevision
    cta: EstadoRevision
    compliance: EstadoRevision
    riesgo_generico: NivelRiesgoGenerico
    estado_revision: EstadoRevision
    motivo: Optional[str] = None
    ajustes_recomendados: Optional[str] = None
    bloqueos_criticos: List[BloqueoCritico] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_bloqueos_criticos(self):
        if self.bloqueos_criticos and self.estado_revision != EstadoRevision.FAIL:
            raise ValueError(
                "Inconsistencia de contrato: estado_revision debe ser FAIL si hay bloqueos_criticos."
            )
        return self
