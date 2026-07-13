from enum import Enum

from pydantic import BaseModel, Field


class EstadoAuditoriaEditorial(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    REQUIERE_ATENCION = "REQUIERE_ATENCION"


class SeveridadHallazgoEditorial(str, Enum):
    MENOR = "menor"
    MAYOR = "mayor"
    CRITICA = "critica"


class HallazgoEditorial(BaseModel):
    categoria: str
    severidad: SeveridadHallazgoEditorial
    fragmento: str | None = None
    explicacion: str
    instruccion_correccion: str | None = None
    requiere_regeneracion: bool = False
    referencias_evidencia: list[str] = Field(default_factory=list)
    incertidumbre: str | None = None


class AuditoriaEditorial(BaseModel):
    estado: EstadoAuditoriaEditorial
    hallazgos: list[HallazgoEditorial] = Field(default_factory=list)
    limites: list[str] = Field(default_factory=list)

    @property
    def feedback_estructurado(self) -> str:
        return " | ".join(
            hallazgo.instruccion_correccion
            for hallazgo in self.hallazgos
            if hallazgo.requiere_regeneracion and hallazgo.instruccion_correccion
        )
