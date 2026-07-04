import hashlib

from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.contracts.evidencia_contexto_usado import EvidenciaContextoUsado


def construir_evidencia_contexto_usado(
    contexto: ContextoTrabajo,
    nombre_operacion: str,
    resultado_operacion: str,
    artefactos_generados: list[str] | None = None,
    advertencias: list[str] | None = None,
    bloqueos: list[str] | None = None,
) -> EvidenciaContextoUsado:
    """
    Caso de uso determinista que construye la evidencia estructurada de
    un contexto de trabajo utilizado en una operación específica.
    """
    if contexto is None:
        raise ValueError("El contexto no puede ser None.")
    if not nombre_operacion or not nombre_operacion.strip():
        raise ValueError("El nombre de la operación no puede estar vacío.")

    resultados_validos = ["PASS", "WARN", "BLOQUEADO", "FAIL"]
    if resultado_operacion not in resultados_validos:
        raise ValueError(
            f"Resultado de operación inválido. Debe ser uno de: {resultados_validos}"
        )

    # Convertir listas None a vacías
    artefactos = artefactos_generados if artefactos_generados is not None else []
    advs = advertencias if advertencias is not None else []
    bloqs = bloqueos if bloqueos is not None else []

    # Generar id_evidencia determinista
    datos_hash = "|".join([
        contexto.contexto_id,
        contexto.cliente_id,
        contexto.superficie,
        contexto.campaña or "",
        nombre_operacion,
        resultado_operacion,
        ",".join(contexto.fuentes_autorizadas),
        ",".join(artefactos),
        ",".join(advs),
        ",".join(bloqs),
    ])
    id_evidencia = hashlib.sha256(datos_hash.encode("utf-8")).hexdigest()[:12]

    limites_de_inferencia = [
        "La evidencia registra el contexto declarado; no verifica por sí sola el contenido interno de fuentes externas."
    ]

    return EvidenciaContextoUsado(
        id_evidencia=id_evidencia,
        contexto_id=contexto.contexto_id,
        cliente_id=contexto.cliente_id,
        superficie=contexto.superficie,
        campaña=contexto.campaña,
        nombre_operacion=nombre_operacion,
        resultado_operacion=resultado_operacion,  # type: ignore
        datos_reales_permitidos=contexto.datos_reales_permitidos,
        fuentes_autorizadas=contexto.fuentes_autorizadas,
        artefactos_generados=artefactos,
        advertencias=advs,
        bloqueos=bloqs,
        limites_de_inferencia=limites_de_inferencia,
    )
