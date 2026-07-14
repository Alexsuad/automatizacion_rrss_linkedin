from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    MetadatosAudioLocal,
    PerfilNarrativoReferencia,
    ResultadoSanitizacionTranscripcion,
    ResultadoTranscripcion,
    ResultadoValidacionAudio,
    SegmentoTranscripcion,
    TipoEntrada,
)
from linkedin_content_system.transcription import AudioTranscriber
from linkedin_content_system.transcription.ports import (
    TranscriptionInputError,
    TranscriptionResponseError,
)


_EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_REGEX = re.compile(r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}")
_OPENAI_KEY_REGEX = re.compile(r"sk-[a-zA-Z0-9]{20,}")
_BEARER_REGEX = re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.\~]+", re.IGNORECASE)
_PASSWORD_ASSIGN = re.compile(r"password\s*=\s*[^\s]+", re.IGNORECASE)
_API_KEY_ASSIGN = re.compile(r"api_key\s*=\s*[^\s]+", re.IGNORECASE)
_RUTA_LOCAL_REGEXES = (
    re.compile(r"file:///[^ \n]+", re.IGNORECASE),
    re.compile(r"/home/[^\s]+"),
    re.compile(r"/mnt/data/[^\s]+"),
    re.compile(r"[A-Za-z]:\\\\[^\s]+"),
    re.compile(r"\\\\wsl\$\\[^\s]+", re.IGNORECASE),
)
_MAX_AUDIO_BYTES_DEFAULT = 2 * 1024 * 1024
_MAX_AUDIO_SECONDS_DEFAULT = 180.0
_VALID_ID = re.compile(r"[^A-Za-z0-9_-]+")


@dataclass(frozen=True)
class PreparacionEntradaAudio:
    entrada: EntradaContenido
    validacion: ResultadoValidacionAudio
    transcripcion: ResultadoTranscripcion
    sanitizacion: ResultadoSanitizacionTranscripcion


def _slug_seguro(texto: str) -> str:
    limpio = _VALID_ID.sub("_", (texto or "").strip().lower()).strip("_")
    return limpio or "audio"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parsear_entero_positivo(valor: str | None, default: int) -> int:
    raw = (valor or "").strip()
    if not raw:
        return default
    try:
        numero = int(raw)
    except ValueError as exc:
        raise ValueError("El límite máximo de audio debe ser un entero positivo.") from exc
    if numero <= 0:
        raise ValueError("El límite máximo de audio debe ser un entero positivo.")
    return numero


def _parsear_float_positivo(valor: str | None, default: float) -> float:
    raw = (valor or "").strip()
    if not raw:
        return default
    try:
        numero = float(raw)
    except ValueError as exc:
        raise ValueError("La duración máxima de audio debe ser numérica y positiva.") from exc
    if numero <= 0:
        raise ValueError("La duración máxima de audio debe ser numérica y positiva.")
    return numero


def _duracion_y_formato_audio(path: Path) -> tuple[float | None, bool, list[str]]:
    advertencias: list[str] = []
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as wav_file:
                frames = wav_file.getnframes()
                framerate = wav_file.getframerate()
                if frames <= 0 or framerate <= 0:
                    raise ValueError("WAV sin frames válidos.")
                return frames / framerate, True, advertencias
        except wave.Error:
            advertencias.append("No se pudo verificar el formato WAV con la librería estándar.")

    if shutil.which("ffprobe"):
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode == 0:
            try:
                return float(completed.stdout.strip()), True, advertencias
            except ValueError:
                advertencias.append("ffprobe no devolvió una duración interpretable.")
        else:
            advertencias.append("ffprobe no pudo validar el archivo de audio.")
    return None, False, advertencias
def cargar_metadatos_autorizados(path: str | None) -> dict:
    if not path:
        return {}
    metadata_path = Path(path).expanduser()
    if not metadata_path.exists() or not metadata_path.is_file():
        raise ValueError("El JSON de metadatos autorizados no existe o no es un archivo.")
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("El JSON de metadatos autorizados debe contener un objeto.")
    return data


def validar_audio_local(
    ruta_audio: str | Path,
    *,
    allowed_extensions: set[str],
    language: str | None = None,
    max_bytes: int | None = None,
    max_seconds: float | None = None,
) -> ResultadoValidacionAudio:
    path = Path(ruta_audio).expanduser()
    size_limit = max_bytes or _parsear_entero_positivo(
        os.getenv("LINKEDIN_CONTENT_AUDIO_MAX_BYTES"),
        _MAX_AUDIO_BYTES_DEFAULT,
    )
    seconds_limit = max_seconds or _parsear_float_positivo(
        os.getenv("LINKEDIN_CONTENT_AUDIO_MAX_SECONDS"),
        _MAX_AUDIO_SECONDS_DEFAULT,
    )

    if not path.exists() or not path.is_file() or path.is_symlink():
        raise TranscriptionInputError("El archivo de audio no existe o no es un archivo regular autorizado.")
    if path.stat().st_size <= 0:
        raise TranscriptionInputError("El archivo de audio no puede estar vacío.")
    if path.stat().st_size > size_limit:
        raise TranscriptionInputError("El archivo de audio supera el tamaño máximo permitido.")

    extension = path.suffix.lower()
    if extension not in allowed_extensions:
        raise TranscriptionInputError(
            f"El formato de audio no está soportado para este adaptador. Extensiones admitidas: {', '.join(sorted(allowed_extensions))}."
        )

    try:
        with path.open("rb") as handle:
            if not handle.read(1):
                raise TranscriptionInputError("El archivo de audio no contiene datos legibles.")
    except OSError as exc:
        raise TranscriptionInputError("No se pudo leer el archivo de audio autorizado.") from exc

    duration_seconds, verified_format, warnings = _duracion_y_formato_audio(path)
    if duration_seconds is not None and duration_seconds > seconds_limit:
        raise TranscriptionInputError("El archivo de audio supera la duración máxima permitida.")

    metadata = MetadatosAudioLocal(
        referencia_audio=f"audio_{_slug_seguro(path.stem)}",
        nombre_logico=_slug_seguro(path.stem),
        extension=extension,
        mime_type=mimetypes.guess_type(path.name)[0],
        tamano_bytes=path.stat().st_size,
        duracion_segundos=duration_seconds,
        sha256_audio=_sha256_file(path),
        idioma_declarado=(language or "").strip() or None,
    )
    return ResultadoValidacionAudio(
        audio=metadata,
        formato_verificado=verified_format,
        advertencias=warnings,
        tamano_maximo_bytes=size_limit,
        duracion_maxima_segundos=seconds_limit,
    )


def _sanitizar_fragmento(texto: str) -> tuple[str, list[str]]:
    transformaciones: list[str] = []
    sanitizado = texto

    for regex, reemplazo, etiqueta in (
        (_EMAIL_REGEX, "[EMAIL_REDACTED]", "email_redactado"),
        (_OPENAI_KEY_REGEX, "[SECRET_REDACTED]", "secret_redactado"),
        (_BEARER_REGEX, "[SECRET_REDACTED]", "bearer_redactado"),
        (_PASSWORD_ASSIGN, "password=[SECRET_REDACTED]", "password_redactado"),
        (_API_KEY_ASSIGN, "api_key=[SECRET_REDACTED]", "api_key_redactado"),
        (_PHONE_REGEX, "[PHONE_REDACTED]", "telefono_redactado"),
    ):
        nuevo = regex.sub(reemplazo, sanitizado)
        if nuevo != sanitizado:
            transformaciones.append(etiqueta)
            sanitizado = nuevo

    for regex in _RUTA_LOCAL_REGEXES:
        nuevo = regex.sub("[LOCAL_PATH_REDACTED]", sanitizado)
        if nuevo != sanitizado:
            transformaciones.append("ruta_local_redactada")
            sanitizado = nuevo
    return sanitizado.strip(), transformaciones


def sanitizar_transcripcion(resultado: ResultadoTranscripcion) -> ResultadoSanitizacionTranscripcion:
    texto_sanitizado, transformaciones = _sanitizar_fragmento(resultado.texto_bruto)
    if not texto_sanitizado:
        raise TranscriptionResponseError("La transcripción sanitizada quedó vacía.")

    segmentos_sanitizados: list[SegmentoTranscripcion] = []
    for segmento in resultado.segmentos:
        texto_segmento, transformaciones_segmento = _sanitizar_fragmento(segmento.texto)
        transformaciones.extend(transformaciones_segmento)
        if not texto_segmento:
            continue
        segmentos_sanitizados.append(
            SegmentoTranscripcion(
                indice=segmento.indice,
                texto=texto_segmento,
                inicio_segundos=segmento.inicio_segundos,
                fin_segundos=segmento.fin_segundos,
            )
        )

    advertencias = list(resultado.advertencias)
    if transformaciones:
        advertencias.append("La transcripción se sanitizó antes de entrar al pipeline editorial.")
    return ResultadoSanitizacionTranscripcion(
        texto_sanitizado=texto_sanitizado,
        sha256_transcripcion_bruta=hashlib.sha256(resultado.texto_bruto.encode("utf-8")).hexdigest(),
        sha256_transcripcion_sanitizada=hashlib.sha256(texto_sanitizado.encode("utf-8")).hexdigest(),
        segmentos_sanitizados=segmentos_sanitizados,
        advertencias=advertencias,
        transformaciones=sorted(set(transformaciones)),
    )


def construir_entrada_desde_audio(
    *,
    audio_path: str | Path,
    transcriber: AudioTranscriber,
    profile_id: str,
    id_entrada: str | None = None,
    canales_destino: list[str] | None = None,
    language: str | None = None,
    intencion_editorial: IntencionEditorial | None = None,
    metadatos_autorizados: dict | None = None,
    restricciones: dict | None = None,
) -> PreparacionEntradaAudio:
    metadata = dict(metadatos_autorizados or {})
    validacion = validar_audio_local(
        audio_path,
        allowed_extensions=transcriber.supported_extensions,
        language=language,
    )
    transcripcion = transcriber.transcribir(
        Path(audio_path).expanduser(),
        audio_sha256=validacion.audio.sha256_audio,
        language=language,
    )
    sanitizacion = sanitizar_transcripcion(transcripcion)

    referencia_fuente = str(
        metadata.get("referencia_fuente") or validacion.audio.referencia_audio
    ).strip()
    metadata["referencia_fuente"] = referencia_fuente
    metadata["audio_sha256"] = validacion.audio.sha256_audio
    metadata["audio_nombre_logico"] = validacion.audio.nombre_logico
    metadata["audio_extension"] = validacion.audio.extension
    metadata["audio_mime_type"] = validacion.audio.mime_type
    metadata["audio_tamano_bytes"] = validacion.audio.tamano_bytes
    metadata["audio_duracion_segundos"] = validacion.audio.duracion_segundos
    metadata["procedencia_transcripcion"] = transcripcion.adaptador
    metadata["transcripcion_modo"] = transcripcion.modo.value
    metadata["transcripcion_modelo"] = transcripcion.modelo
    metadata["transcripcion_idioma"] = transcripcion.idioma
    metadata["transcripcion_bruta_sha256"] = sanitizacion.sha256_transcripcion_bruta
    metadata["transcripcion_sanitizada_sha256"] = sanitizacion.sha256_transcripcion_sanitizada
    metadata["transcripcion_advertencias"] = sanitizacion.advertencias
    metadata["transcripcion_transformaciones"] = sanitizacion.transformaciones
    metadata["transcripcion_segmentos"] = [
        segmento.model_dump(mode="json") for segmento in sanitizacion.segmentos_sanitizados
    ]

    idea_base = sanitizacion.texto_sanitizado[:280]
    entrada = EntradaContenido(
        id_entrada=id_entrada or f"{validacion.audio.nombre_logico}_audio",
        tipo_entrada=TipoEntrada.AUDIO,
        texto_base=sanitizacion.texto_sanitizado,
        intencion_editorial=intencion_editorial
        or IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.TENTATIVA,
            idea_central=idea_base,
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil=profile_id),
        canales_destino=canales_destino or ["linkedin"],
        metadatos_origen=metadata,
        estado_privacidad=EstadoPrivacidad(
            sanitizado=True,
            pii_detectada=bool(sanitizacion.transformaciones),
            advertencias=sanitizacion.advertencias,
        ),
        restricciones=restricciones or {},
    )
    return PreparacionEntradaAudio(
        entrada=entrada,
        validacion=validacion,
        transcripcion=transcripcion,
        sanitizacion=sanitizacion,
    )
