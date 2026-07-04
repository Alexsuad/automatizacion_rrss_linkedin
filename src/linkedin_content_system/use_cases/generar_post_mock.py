from linkedin_content_system.ai.ports import ModelAdapter


def generar_post_mock(texto_base: str, adapter: ModelAdapter) -> str:
    """
    Caso de uso mínimo para generar un post LinkedIn simulado usando el adaptador de IA.
    """
    if not texto_base or not texto_base.strip():
        raise ValueError("El texto base no puede estar vacío.")

    if adapter is None:
        raise ValueError("El adapter no puede ser None.")

    return adapter.generar_texto(prompt=texto_base.strip())

