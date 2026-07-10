from linkedin_content_system.contracts.idea_central import IdeaCentral


def _extraer_candidatas(texto: str) -> list[str]:
    fragmentos = [
        fragmento.strip()
        for fragmento in texto.replace("\n", " ").split(".")
        if len(fragmento.strip().split()) >= 5
    ]
    candidatas = fragmentos[:3]
    return candidatas or [texto[:280]]


def extraer_idea_central(texto_base: str) -> IdeaCentral:
    """
    Extrae de forma determinista y offline una representación estructurada de la idea central.
    """
    if not texto_base or not texto_base.strip():
        raise ValueError("El texto base no puede estar vacío.")

    texto_limpio = texto_base.strip()
    
    # Aplicar límites acordados para la extracción determinista
    ideas_candidatas = _extraer_candidatas(texto_limpio)
    idea_central = ideas_candidatas[0][:280]
    fragmento = texto_limpio[:120]
    resumen_operativo = f"Extracción operativa basada en el texto: {fragmento}"
    
    # Derivar punto de soporte inicial
    punto_soporte = texto_limpio[:150]
    
    return IdeaCentral(
        idea_central=idea_central,
        resumen_operativo=resumen_operativo,
        puntos_de_soporte=[punto_soporte],
        ideas_candidatas=[candidata[:280] for candidata in ideas_candidatas],
        limites_de_inferencia=[
            "No inventar hechos ni cifras que no estén explícitamente detallados en el texto original."
        ]
    )
