import hashlib
from typing import Literal

from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo


def activar_contexto_trabajo(
    cliente_id: str,
    superficie: str,
    campaña: str | None = None,
    fuentes_autorizadas: list[str] | None = None,
    datos_reales_permitidos: bool = False,
) -> ContextoTrabajo:
    """
    Caso de uso determinista que activa un contexto de trabajo aislado
    y previene la contaminación de datos.
    """
    if not cliente_id or not cliente_id.strip():
        raise ValueError("El cliente_id no puede estar vacío.")

    superficies_validas = ["linkedin_personal", "linkedin_empresa", "general"]
    if superficie not in superficies_validas:
        raise ValueError(
            f"Superficie inválida. Debe ser una de: {superficies_validas}"
        )

    # Convertir fuentes_autorizadas None en lista vacía
    fuentes = fuentes_autorizadas if fuentes_autorizadas is not None else []

    # Generar contexto_id determinista usando SHA-256
    datos_hash = f"{cliente_id}|{superficie}|{campaña or ''}|{','.join(fuentes)}|{datos_reales_permitidos}"
    contexto_id = hashlib.sha256(datos_hash.encode("utf-8")).hexdigest()[:12]

    # Notas de seguridad
    notas_seguridad = [
        "Contexto aislado: no mezclar datos de otros clientes, campañas o superficies."
    ]
    if not datos_reales_permitidos:
        notas_seguridad.append("Datos reales no permitidos en este contexto.")

    return ContextoTrabajo(
        contexto_id=contexto_id,
        cliente_id=cliente_id,
        superficie=superficie,  # type: ignore
        campaña=campaña,
        fuentes_autorizadas=fuentes,
        datos_reales_permitidos=datos_reales_permitidos,
        estado="activo",
        notas_seguridad=notas_seguridad,
    )
