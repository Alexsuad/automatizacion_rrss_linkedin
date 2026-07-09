from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator

class TipoEntrada(str, Enum):
    TEXTO_MANUAL = "texto_manual"
    AUDIO = "audio"
    TRANSCRIPCION = "transcripcion"
    BORRADOR_EXISTENTE = "borrador_existente"
    DOCUMENTO_BASE = "documento_base"

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
    pii_detectada: bool = False
    advertencias: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_sanitizado(self):
        if not self.sanitizado:
            raise ValueError("El estado de privacidad debe estar sanitizado (sanitizado=True).")
        return self

class EntradaContenido(BaseModel):
    id_entrada: str
    tipo_entrada: TipoEntrada
    fecha_creacion: Optional[str] = None
    texto_base: str
    intencion_editorial: IntencionEditorial
    perfil_narrativo: PerfilNarrativoReferencia
    canales_destino: List[str] = Field(default_factory=lambda: ["linkedin"])
    metadatos_origen: dict = Field(default_factory=dict)
    estado_privacidad: EstadoPrivacidad
    restricciones: dict

    @model_validator(mode="after")
    def validar_insumos_suficientes(self):
        if not self.texto_base or not self.texto_base.strip():
            raise ValueError("texto_base siempre debe tener contenido útil (no puede estar vacío ni contener solo espacios).")

        if not self.canales_destino:
            raise ValueError("canales_destino no puede estar vacío.")

        canales_normalizados: List[str] = []
        for canal in self.canales_destino:
            if not isinstance(canal, str) or not canal.strip():
                raise ValueError("canales_destino solo puede contener strings no vacíos.")
            canal_normalizado = canal.strip().lower()
            if canal_normalizado in canales_normalizados:
                raise ValueError("canales_destino no puede contener canales duplicados.")
            canales_normalizados.append(canal_normalizado)
        self.canales_destino = canales_normalizados

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
