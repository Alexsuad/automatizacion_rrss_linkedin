from __future__ import annotations

import hashlib
from pathlib import Path

from linkedin_content_system.contracts import EntradaContenido, FuenteTextualNormalizada, TipoEntrada
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


_EXTENSIONES_TEXTUALES = {".txt", ".md"}
_MAX_BYTES_DOCUMENTO = 512 * 1024


def _lista_textual(valor: object) -> list[str]:
    if not valor:
        return []
    if isinstance(valor, str):
        valor = [valor]
    if not isinstance(valor, list):
        raise ValueError("Los metadatos editoriales deben ser una lista de textos.")
    resultado = [str(item).strip() for item in valor if str(item).strip()]
    for texto in resultado:
        validar_texto_sin_pii_basica(texto)
        validar_texto_sin_secretos_basicos(texto)
        validar_sin_rutas_locales(texto)
    return resultado


def cargar_documento_textual(ruta: str | Path) -> str:
    """Carga solo documentos textuales pequenos y legibles localmente."""
    path = Path(ruta).expanduser()
    if not path.exists() or not path.is_file():
        raise ValueError("El documento textual indicado no existe o no es un archivo.")
    if path.suffix.lower() not in _EXTENSIONES_TEXTUALES:
        raise ValueError("El documento textual debe tener extensión .txt o .md.")
    if path.stat().st_size > _MAX_BYTES_DOCUMENTO:
        raise ValueError("El documento textual supera el tamaño máximo permitido.")
    try:
        contenido = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("El documento textual debe estar codificado en UTF-8.") from exc
    if not contenido.strip():
        raise ValueError("El documento textual no puede estar vacío.")
    validar_texto_sin_pii_basica(contenido)
    validar_texto_sin_secretos_basicos(contenido)
    validar_sin_rutas_locales(contenido)
    return contenido


def normalizar_entrada_textual(entrada: EntradaContenido) -> FuenteTextualNormalizada:
    """Normaliza los tres orígenes textuales sin abrir rutas desde el core."""
    if entrada.tipo_entrada not in {
        TipoEntrada.TEXTO_MANUAL,
        TipoEntrada.DOCUMENTO_BASE,
        TipoEntrada.BORRADOR_EXISTENTE,
    }:
        raise ValueError(
            "Este flujo solo admite entradas de texto manual, documento base o borrador existente."
        )

    contenido = entrada.texto_base.strip()
    validar_texto_sin_pii_basica(contenido)
    validar_texto_sin_secretos_basicos(contenido)
    validar_sin_rutas_locales(contenido)
    metadata = entrada.metadatos_origen or {}
    referencia = str(metadata.get("referencia_fuente") or entrada.id_entrada).strip()
    if not referencia:
        raise ValueError("La fuente normalizada requiere una referencia reproducible.")
    # La referencia es un identificador, no una ruta local que vaya a persistirse.
    if any(fragment in referencia for fragment in ("/", "\\", ":")):
        raise ValueError("La referencia de fuente debe ser un identificador relativo, no una ruta local.")

    idea = entrada.intencion_editorial.idea_central
    hechos = _lista_textual(metadata.get("hechos_autorizados"))
    opiniones = _lista_textual(metadata.get("opiniones_explicitas"))
    experiencias = _lista_textual(metadata.get("experiencias_autorizadas"))
    instrucciones = _lista_textual(metadata.get("instrucciones_editoriales"))
    no_inferir = _lista_textual(metadata.get("no_inferir"))

    return FuenteTextualNormalizada(
        tipo_entrada=entrada.tipo_entrada,
        referencia_fuente=referencia,
        hash_contenido=hashlib.sha256(contenido.encode("utf-8")).hexdigest(),
        contenido_normalizado=contenido,
        idea_central=idea,
        hechos_explicitos=hechos,
        opiniones_explicitas=opiniones,
        experiencias_autorizadas=experiencias,
        instrucciones_editoriales=instrucciones,
        no_inferir=no_inferir,
    )
