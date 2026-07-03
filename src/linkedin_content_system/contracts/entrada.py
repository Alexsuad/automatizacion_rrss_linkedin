from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

class TipoEntrada(str, Enum):
    AUDIO = "audio"
    TEXTO_BRUTO = "texto_bruto"
    BORRADOR_EXISTENTE = "borrador_existente"

class EstadoIntencionEditorial(str, Enum):
    COMPLETA = "completa"
    PARCIAL = "parcial"
    TENTATIVA = "tentativa"

class NivelPromocion(str, Enum):
    NULO = "nulo"
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

class IntencionEditorial(BaseModel):
    estado_intencion_editorial: EstadoIntencionEditorial
    audiencia_objetivo: Optional[str] = None
    objetivo_del_post: Optional[str] = None
    pilar_contenido: Optional[str] = None
    tipo_de_post: Optional[str] = None
    dolor_o_tension: Optional[str] = None
    idea_central: Optional[str] = None
    cta_intencionado: Optional[str] = None
    nivel_de_promocion: Optional[NivelPromocion] = None

class PerfilNarrativoReferencia(BaseModel):
    id_perfil: str

class EstadoPrivacidad(BaseModel):
    sanitizado: bool

    @model_validator(mode="after")
    def validar_sanitizado(self):
        if not self.sanitizado:
            raise ValueError("El estado de privacidad debe estar sanitizado (sanitizado=True).")
        return self

class EntradaContenido(BaseModel):
    id_entrada: str
    tipo_entrada: TipoEntrada
    texto_base: str
    intencion_editorial: IntencionEditorial
    perfil_narrativo: PerfilNarrativoReferencia
    canales_destino: List[str] = Field(default_factory=lambda: ["linkedin"])
    estado_privacidad: EstadoPrivacidad
    restricciones: dict

    @model_validator(mode="after")
    def validar_insumos_suficientes(self):
        if not self.texto_base or not self.texto_base.strip():
            raise ValueError("texto_base siempre debe tener contenido útil (no puede estar vacío ni contener solo espacios).")

        if self.canales_destino != ["linkedin"]:
            raise ValueError("canales_destino debe ser exactamente ['linkedin'].")

        ie = self.intencion_editorial
        if ie.estado_intencion_editorial in (EstadoIntencionEditorial.PARCIAL, EstadoIntencionEditorial.TENTATIVA):
            if not self.texto_base or not self.texto_base.strip():
                raise ValueError(
                    "Insumo insuficiente: no se puede derivar una intención editorial parcial o tentativa sin texto_base."
                )
        
        campos_editorial = [
            ie.audiencia_objetivo, ie.objetivo_del_post, ie.pilar_contenido,
            ie.tipo_de_post, ie.dolor_o_tension, ie.idea_central, ie.cta_intencionado
        ]
        if all(c is None or (isinstance(c, str) and not c.strip()) for c in campos_editorial) and (not self.texto_base or not self.texto_base.strip()):
            raise ValueError(
                "Insumo insuficiente: intención editorial vacía y sin texto_base."
            )
        return self
