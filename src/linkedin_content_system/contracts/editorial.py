from enum import Enum
from typing import Optional
from pydantic import BaseModel

class EstadoRevision(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

class NivelRiesgoGenerico(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

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
