from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class EstadoTrazabilidad(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class TipoHallazgoTrazabilidad(str, Enum):
    HECHO_NO_SOPORTADO = "hecho_no_soportado"
    AUTORIDAD_FINGIDA = "autoridad_fingida"
    ANECDOTA_INVENTADA = "anecdota_inventada"
    CIFRA_NO_SOPORTADA = "cifra_no_soportada"
    PROMESA_EXCESIVA = "promesa_excesiva"
    CLAIM_SIN_FUENTE = "claim_sin_fuente"
    INFERENCIA_DEBIL = "inferencia_debil"
    CONTRADICCION_CON_CONTEXTO = "contradiccion_con_contexto"


class HallazgoTrazabilidad(BaseModel):
    tipo: TipoHallazgoTrazabilidad
    fragmento_post: str
    descripcion: str
    soporte_encontrado: Optional[str] = None
    bloqueante: Optional[bool] = None

    @field_validator("fragmento_post", "descripcion")
    @classmethod
    def validar_campos_no_vacios(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("El campo no puede estar vacío.")
        return value.strip()

    @field_validator("soporte_encontrado")
    @classmethod
    def validar_soporte_encontrado(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("soporte_encontrado no puede estar vacío si se proporciona.")
        return value.strip()

    @model_validator(mode="after")
    def validar_bloqueo_coherente(self):
        if self.tipo == TipoHallazgoTrazabilidad.INFERENCIA_DEBIL:
            if self.bloqueante is None:
                self.bloqueante = False
            elif self.bloqueante:
                raise ValueError("inferencia_debil no debe ser bloqueante.")
        else:
            if self.bloqueante is None:
                self.bloqueante = True
            elif not self.bloqueante:
                raise ValueError("Los hallazgos críticos deben ser bloqueantes.")
        return self


class DiagnosticoTrazabilidad(BaseModel):
    estado: EstadoTrazabilidad
    hallazgos: list[HallazgoTrazabilidad] = Field(default_factory=list)
    resumen: Optional[str] = None

    @field_validator("resumen")
    @classmethod
    def validar_resumen(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("El resumen no puede estar vacío si se proporciona.")
        return value.strip()

    @model_validator(mode="after")
    def validar_consistencia(self) -> "DiagnosticoTrazabilidad":
        if self.estado == EstadoTrazabilidad.PASS and self.hallazgos:
            raise ValueError("Si el estado es PASS, no puede haber hallazgos.")

        if self.estado == EstadoTrazabilidad.WARN:
            if not self.hallazgos:
                raise ValueError("Si el estado es WARN, debe haber al menos un hallazgo.")
            if any(h.bloqueante for h in self.hallazgos):
                raise ValueError("Si el estado es WARN, los hallazgos no pueden ser bloqueantes.")
            if any(h.tipo != TipoHallazgoTrazabilidad.INFERENCIA_DEBIL for h in self.hallazgos):
                raise ValueError("Si el estado es WARN, solo se admiten hallazgos de inferencia_debil.")

        if self.estado == EstadoTrazabilidad.FAIL:
            if not self.hallazgos:
                raise ValueError("Si el estado es FAIL, debe haber al menos un hallazgo.")
            if not any(h.bloqueante for h in self.hallazgos):
                raise ValueError("Si el estado es FAIL, debe existir al menos un hallazgo bloqueante.")

        return self
