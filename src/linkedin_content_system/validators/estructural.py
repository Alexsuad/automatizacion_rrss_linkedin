from typing import List

RUTAS_LOCALES_PATTERNS = [
    "file:///",
    "C:/Users",
    "C:\\Users",
    "/home/",
    "/mnt/data",
    "\\\\wsl$",
    "\\wsl$"
]

def detectar_ruta_local(texto: str) -> bool:
    for pattern in RUTAS_LOCALES_PATTERNS:
        if pattern in texto:
            return True
    return False

def validar_sin_rutas_locales(texto: str) -> None:
    if detectar_ruta_local(texto):
        raise ValueError("Se detectaron rutas locales absolutas o referencias de entorno en el texto.")

def validar_texto_no_vacio(texto: str) -> None:
    if not texto or not texto.strip():
        raise ValueError("El texto no puede estar vacío ni contener solo espacios.")

def validar_lista_no_vacia(lista: List) -> None:
    if not lista:
        raise ValueError("La lista no puede estar vacía.")
