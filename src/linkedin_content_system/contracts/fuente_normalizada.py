from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .entrada import TipoEntrada


class FuenteTextualNormalizada(BaseModel):
    """Representacion comun de una fuente textual apta para el flujo editorial."""

    tipo_entrada: Literal[
        TipoEntrada.TEXTO_MANUAL,
        TipoEntrada.DOCUMENTO_BASE,
        TipoEntrada.BORRADOR_EXISTENTE,
        TipoEntrada.AUDIO,
        TipoEntrada.TRANSCRIPCION,
    ]
    referencia_fuente: str
    hash_contenido: str
    contenido_normalizado: str
    idea_central: str | None = None
    hechos_explicitos: list[str] = Field(default_factory=list)
    opiniones_explicitas: list[str] = Field(default_factory=list)
    experiencias_autorizadas: list[str] = Field(default_factory=list)
    instrucciones_editoriales: list[str] = Field(default_factory=list)
    no_inferir: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    fragmentos_evidencia: list[dict[str, object]] = Field(default_factory=list)
    elementos_pendientes: list[str] = Field(default_factory=list)
