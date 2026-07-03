import re

# Patrones regex simples
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
# Teléfonos simples: ej +34 123456789, 123-456-789
PHONE_REGEX = re.compile(r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}")

# Patrones para secretos
OPENAI_KEY_REGEX = re.compile(r"sk-[a-zA-Z0-9]{20,}")
BEARER_REGEX = re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.\~]+", re.IGNORECASE)
PASSWORD_ASSIGN = re.compile(r"password\s*=\s*[^\s]+", re.IGNORECASE)
API_KEY_ASSIGN = re.compile(r"api_key\s*=\s*[^\s]+", re.IGNORECASE)

def detectar_email(texto: str) -> bool:
    return bool(EMAIL_REGEX.search(texto))

def detectar_telefono_basico(texto: str) -> bool:
    return bool(PHONE_REGEX.search(texto))

def detectar_secreto_basico(texto: str) -> bool:
    if OPENAI_KEY_REGEX.search(texto):
        return True
    if BEARER_REGEX.search(texto):
        return True
    if PASSWORD_ASSIGN.search(texto):
        return True
    if API_KEY_ASSIGN.search(texto):
        return True
    return False

def validar_texto_sin_pii_basica(texto: str) -> None:
    if detectar_email(texto):
        raise ValueError("Se detectó PII (correo electrónico) en el texto.")
    if detectar_telefono_basico(texto):
        raise ValueError("Se detectó PII (teléfono) en el texto.")

def validar_texto_sin_secretos_basicos(texto: str) -> None:
    if detectar_secreto_basico(texto):
        raise ValueError("Se detectaron secretos o credenciales en el texto.")
