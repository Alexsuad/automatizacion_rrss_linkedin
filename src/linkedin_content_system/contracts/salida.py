from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator
from .editorial import DiagnosticoEditorial

class EstadoAprobacion(str, Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    REQUIERE_AJUSTES = "requiere_ajustes"

class TipoAprobacion(str, Enum):
    SIMPLE = "simple"
    REFORZADA = "reforzada"

class ModoPublicacion(str, Enum):
    DRY_RUN = "dry_run"

class AdaptadorActivo(str, Enum):
    LOCALDRAFT = "localdraft"

class EstadoSalidaLocal(str, Enum):
    BORRADOR_LOCAL = "borrador_local"

class EstadoPublicabilidad(str, Enum):
    PUBLICABLE = "publicable"
    REQUIERE_REVISION = "requiere_revision"
    RECHAZADO_EDITORIAL = "rechazado_editorial"
    NO_PUBLICABLE = "no_publicable"

class PostCandidato(BaseModel):
    texto: str

class AprobacionHumana(BaseModel):
    estado: EstadoAprobacion
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[str] = None
    comentarios: Optional[str] = None
    tipo_aprobacion: TipoAprobacion = TipoAprobacion.SIMPLE
    revision_reforzada_requerida: bool = False
    motivo_revision_reforzada: Optional[str] = None

    @model_validator(mode="after")
    def validar_aprobacion(self):
        if self.estado == EstadoAprobacion.APROBADO:
            if not self.aprobado_por or not self.aprobado_por.strip():
                raise ValueError("aprobado_por es obligatorio cuando el estado es aprobado.")
            if not self.fecha_aprobacion or not self.fecha_aprobacion.strip():
                raise ValueError("fecha_aprobacion es obligatoria cuando el estado es aprobado.")
            
            # Validación: Si revision_reforzada_requerida == True:
            # - tipo_aprobacion debe ser reforzada
            # - motivo_revision_reforzada debe ser no vacío
            if self.revision_reforzada_requerida:
                if self.tipo_aprobacion != TipoAprobacion.REFORZADA:
                    raise ValueError(
                        "Se requiere revisión reforzada. El tipo de aprobación debe ser 'reforzada'."
                    )
                if not self.motivo_revision_reforzada or not self.motivo_revision_reforzada.strip():
                    raise ValueError(
                        "Debe especificarse el motivo_revision_reforzada al usar aprobación reforzada."
                    )
            
            # Validación: Si tipo_aprobacion == reforzada:
            # - motivo_revision_reforzada debe ser no vacío
            if self.tipo_aprobacion == TipoAprobacion.REFORZADA:
                if not self.motivo_revision_reforzada or not self.motivo_revision_reforzada.strip():
                    raise ValueError(
                        "Debe especificarse el motivo_revision_reforzada al usar aprobación reforzada."
                    )
        return self

class SalidaLocalDraft(BaseModel):
    post: PostCandidato
    diagnostico_editorial: DiagnosticoEditorial
    aprobacion_humana: AprobacionHumana
    modo_publicacion: ModoPublicacion
    adaptador_activo: AdaptadorActivo
    estado: EstadoSalidaLocal
    estado_publicabilidad: EstadoPublicabilidad = EstadoPublicabilidad.NO_PUBLICABLE
    fecha_objetivo_sugerida: Optional[str] = None


