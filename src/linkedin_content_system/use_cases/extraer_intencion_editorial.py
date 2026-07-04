from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.intencion_editorial_clasificada import IntencionEditorialClasificada


def extraer_intencion_editorial(idea: IdeaCentral) -> IntencionEditorialClasificada:
    """
    Extrae de forma determinista y offline la intención editorial inicial a partir de la IdeaCentral.
    """
    if idea is None:
        raise ValueError("La idea central no puede ser None.")

    texto_evaluar = idea.idea_central.lower()

    # Heurística mínima determinista
    if any(k in texto_evaluar for k in ["aprendí", "me di cuenta", "lección", "aprendi"]):
        intencion = "compartir_aprendizaje"
        justificacion = "El texto de origen hace referencia explícita a una lección o aprendizaje adquirido."
        confianza = "media"
    elif any(k in texto_evaluar for k in ["cómo", "guía", "pasos", "explicar", "como"]):
        intencion = "explicar_idea"
        justificacion = "El texto de origen presenta una estructura de guía instructiva o explicación metodológica."
        confianza = "media"
    elif any(k in texto_evaluar for k in ["creo", "opino", "no estoy de acuerdo", "postura"]):
        intencion = "posicionar_opinion"
        justificacion = "El texto de origen establece una opinión personal o toma de postura sobre un tema."
        confianza = "media"
    elif any(k in texto_evaluar for k in ["me pasó", "experiencia", "cuando", "me paso"]):
        intencion = "contar_experiencia"
        justificacion = "El texto de origen describe una anécdota, vivencia o evento vivido por el autor."
        confianza = "media"
    elif any(k in texto_evaluar for k in ["qué opinas", "pregunta", "debate", "que opinas", "¿"]):
        intencion = "abrir_conversacion"
        justificacion = "El texto de origen incluye preguntas dirigidas a incentivar el diálogo con la audiencia."
        confianza = "media"
    else:
        intencion = "indeterminada"
        justificacion = "No se encontraron patrones explícitos de clasificación determinista."
        confianza = "baja"

    fragmento = idea.idea_central.strip()[:100]
    resumen_intencion = f"Intención identificada como {intencion} para el fragmento: {fragmento}"

    return IntencionEditorialClasificada(
        intencion_principal=intencion,
        resumen_intencion=resumen_intencion,
        justificacion=justificacion,
        confianza=confianza,
        limites_de_inferencia=[
            "No derivar pilares ni objetivos de negocio no expresados por la intención principal."
        ]
    )
