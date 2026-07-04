from typing import Optional

from linkedin_content_system.ai.ports import ModelAdapter


class MockModelAdapter(ModelAdapter):
    """
    Adaptador determinista offline.

    No requiere credenciales, llamadas de red ni SDKs externos.
    Se usa para pruebas y desarrollo local antes de conectar proveedores reales.
    """

    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")

        fragmento_origen = prompt.strip()[:80]
        tiene_system_instruction = "sí" if system_instruction and system_instruction.strip() else "no"

        return (
            "[BORRADOR SIMULADO DE POST]\n"
            f"Contexto de sistema recibido: {tiene_system_instruction}\n"
            f"Fragmento de origen: {fragmento_origen}\n"
            "--- Contenido generado determinista para LinkedIn ---"
        )

