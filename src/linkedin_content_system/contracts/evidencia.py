from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class EstadoEvidencia(str, Enum):
    GUARDADO_LOCAL = "guardado_local"
    PENDIENTE = "pendiente"
    ERROR = "error"

class ManifestEvidencia(BaseModel):
    id_evidencia: str
    id_entrada: str
    archivos_generados: List[str] = Field(..., min_length=1)
    estado: EstadoEvidencia
    timestamp: str
    checksum_opcional: Optional[str] = None
