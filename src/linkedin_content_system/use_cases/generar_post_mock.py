from linkedin_content_system.ai.ports import ModelAdapter


def generar_post_mock(
    texto_base: str,
    adapter: ModelAdapter,
    system_instruction: str | None = None,
) -> str:
    """
    Wrapper de compatibilidad para generar texto a través del seam ModelAdapter.
    """
    if not texto_base or not texto_base.strip():
        raise ValueError("El texto base no puede estar vacío.")

    if adapter is None:
        raise ValueError("El adapter no puede ser None.")

    return adapter.generar_texto(
        prompt=texto_base.strip(),
        system_instruction=system_instruction.strip() if system_instruction else None,
    )
