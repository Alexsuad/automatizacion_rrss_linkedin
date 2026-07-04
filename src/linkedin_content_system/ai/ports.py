from abc import ABC, abstractmethod
from typing import Optional


class ModelAdapter(ABC):
    """
    Puerto interno para adaptadores de modelos de lenguaje.

    Desacopla el núcleo del sistema de proveedores concretos,
    SDKs externos, credenciales y llamadas de red.
    """

    @abstractmethod
    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Genera texto a partir de un prompt validado."""
        raise NotImplementedError
