from pydantic import BaseModel, Field, field_validator


class IdeaCentral(BaseModel):
    """
    Contrato que representa la estructura de la idea central expresada por el autor.
    Evita alucinaciones semánticas estructurando los conceptos antes del post.
    """
    idea_central: str
    resumen_operativo: str
    puntos_de_soporte: list[str] = Field(default_factory=list)
    limites_de_inferencia: list[str] = Field(default_factory=list)

    @field_validator("idea_central", "resumen_operativo")
    @classmethod
    def validar_campo_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v.strip()

    @field_validator("puntos_de_soporte")
    @classmethod
    def validar_puntos_de_soporte(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Debe existir al menos un punto de soporte.")
        cleaned = []
        for item in v:
            if not item or not item.strip():
                raise ValueError("Un punto de soporte no puede estar vacío.")
            cleaned.append(item.strip())
        return cleaned

    @field_validator("limites_de_inferencia")
    @classmethod
    def validar_limites_de_inferencia(cls, v: list[str]) -> list[str]:
        cleaned = []
        for item in v:
            if not item or not item.strip():
                raise ValueError("Un límite de inferencia no puede estar vacío.")
            cleaned.append(item.strip())
        return cleaned
