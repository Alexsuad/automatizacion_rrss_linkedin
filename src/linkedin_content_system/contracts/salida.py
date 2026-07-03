from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator
from .editorial import DiagnosticoEditorial

class EstadoAprobacion(str, Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    REQUIERE_AJUSTES = "requiere_ajustes"

class ModoPublicacion(str, Enum):
    DRY_RUN = "dry_run"

class AdaptadorActivo(str, Enum):
    LOCALDRAFT = "localdraft"

class EstadoSalidaLocal(str, Enum):
    BORRADOR_LOCAL = "borrador_local"

class PostCandidato(BaseModel):
    texto: str

class AprobacionHumana(BaseModel):
    estado: EstadoAprobacion
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[str] = None
    comentarios: Optional[str] = None

    @model_validator(mode="after")
    def validar_aprobacion(self):
        if self.estado == EstadoAprobacion.APROBADO:
            if not self.aprobado_por or not self.aprobado_por.strip():
                raise ValueError("aprobado_por es obligatorio cuando el estado es aprobado.")
            if not self.fecha_aprobacion or not self.fecha_aprobacion.strip():
                raise ValueError("fecha_aprobacion es obligatoria cuando el estado es aprobado.")
        return self

class SalidaLocalDraft(BaseModel):
    post: PostCandidato
    diagnostico_editorial: DiagnosticoEditorial
    aprobacion_humana: AprobacionHumana
    modo_publicacion: ModoPublicacion
    adaptador_activo: AdaptadorActivo
    estado: EstadoSalidaLocal
    fecha_objetivo_sugerida: Optional[str] = None
