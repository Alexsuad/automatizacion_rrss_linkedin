import hashlib
from linkedin_content_system.contracts.evidencia_generacion import EvidenciaGeneracion


def construir_evidencia_generacion(
    fase: str,
    entrada_resumen: str,
    salida_resumen: str,
    estado: str,
    artefactos: list[str] | None = None,
    advertencias: list[str] | None = None,
    bloqueos: list[str] | None = None,
) -> EvidenciaGeneracion:
    """
    Construye de manera determinista y en memoria una EvidenciaGeneracion.
    No realiza escrituras en disco, no usa red ni IA.
    """
    # Convertir listas None en listas vacías
    artefactos_val = artefactos if artefactos is not None else []
    advertencias_val = advertencias if advertencias is not None else []
    bloqueos_val = bloqueos if bloqueos is not None else []

    # Generar id_evidencia determinista
    id_source = f"{fase}|{entrada_resumen}|{salida_resumen}|{estado}"
    id_evidencia = hashlib.sha256(id_source.encode("utf-8")).hexdigest()[:12]

    return EvidenciaGeneracion(
        id_evidencia=id_evidencia,
        fase=fase,
        entrada_resumen=entrada_resumen,
        salida_resumen=salida_resumen,
        estado=estado,  # type: ignore
        artefactos=artefactos_val,
        advertencias=advertencias_val,
        bloqueos=bloqueos_val,
    )
