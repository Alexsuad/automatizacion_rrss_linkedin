from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .entrada import EntradaContenido
from .editorial import DiagnosticoEditorial
from .auditoria_editorial import AuditoriaEditorial
from .salida import AprobacionHumana


class EstadoCicloEditorial(str, Enum):
    PENDIENTE_REVISION = "pendiente_revision"
    REQUIERE_AJUSTES = "requiere_ajustes"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    PREPARADO = "preparado"
    REQUIERE_ATENCION = "requiere_atencion"


class TransicionEstadoEditorial(BaseModel):
    estado_origen: EstadoCicloEditorial | None = None
    estado_destino: EstadoCicloEditorial
    ocurrida_en: str
    motivo: str | None = None


class VersionBorradorEditorial(BaseModel):
    numero: int
    texto: str
    idea_central: str
    ideas_candidatas: list[str] = Field(default_factory=list)
    diagnostico_editorial: DiagnosticoEditorial
    creada_en: str
    version_anterior: int | None = None
    feedback_origen: str | None = None
    trazabilidad_fuente: dict[str, Any] | None = None
    auditoria_editorial: AuditoriaEditorial | None = None


class SesionEditorial(BaseModel):
    id_entrada: str
    entrada: EntradaContenido
    estado: EstadoCicloEditorial
    versiones: list[VersionBorradorEditorial]
    version_actual: int
    aprobacion: AprobacionHumana | None = None
    version_aprobada: int | None = None
    historial_estados: list[TransicionEstadoEditorial] = Field(default_factory=list)
    evidencia_ejecucion: dict[str, Any] | None = None
    version_seleccionada: int | None = None
    motivo_seleccion: str | None = None
    mejora_editorial_demostrada: bool = False

    @model_validator(mode="after")
    def validar_version_actual(self):
        numeros = {version.numero for version in self.versiones}
        if self.version_actual not in numeros:
            raise ValueError("version_actual debe identificar una versión existente.")
        if self.version_aprobada is not None and self.version_aprobada not in numeros:
            raise ValueError("version_aprobada debe identificar una versión existente.")
        if self.historial_estados and self.historial_estados[-1].estado_destino != self.estado:
            raise ValueError("El último estado del historial debe coincidir con el estado actual.")
        return self
