from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    EntradaContenido,
    EstadoAprobacion,
    EstadoCicloEditorial,
    ManifestEvidencia,
    PostCandidato,
    SesionEditorial,
    VersionBorradorEditorial,
    TipoAprobacion,
    TransicionEstadoEditorial,
)
from linkedin_content_system.flows import ensamblar_flujo_local_simulado
from linkedin_content_system.publishers import PublicationPublisherPort
from linkedin_content_system.use_cases.ejecutar_flujo_textual import generar_candidato_textual
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    NarrativeProfileResolver,
    TextChannelStrategy,
)
from linkedin_content_system.use_cases.generar_borrador_local import (
    generar_borrador_local_desde_simulacion,
)
from linkedin_content_system.validators import (
    validar_sin_rutas_locales,
    validar_texto_sin_pii_basica,
    validar_texto_sin_secretos_basicos,
)


_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_TRANSICIONES_VALIDAS = {
    EstadoCicloEditorial.PENDIENTE_REVISION: {
        EstadoCicloEditorial.REQUIERE_AJUSTES,
        EstadoCicloEditorial.APROBADO,
        EstadoCicloEditorial.RECHAZADO,
    },
    EstadoCicloEditorial.REQUIERE_AJUSTES: {
        EstadoCicloEditorial.PENDIENTE_REVISION,
        EstadoCicloEditorial.RECHAZADO,
    },
    EstadoCicloEditorial.APROBADO: {EstadoCicloEditorial.PREPARADO},
    EstadoCicloEditorial.RECHAZADO: set(),
    EstadoCicloEditorial.PREPARADO: set(),
}


def _now(clock: Callable[[], str] | None = None) -> str:
    return clock() if clock else datetime.now(timezone.utc).isoformat()


def _validar_texto_controlado(texto: str, nombre: str) -> str:
    limpio = (texto or "").strip()
    if not limpio:
        raise ValueError(f"{nombre} no puede estar vacío.")
    validar_texto_sin_pii_basica(limpio)
    validar_texto_sin_secretos_basicos(limpio)
    validar_sin_rutas_locales(limpio)
    return limpio


def _transicionar(
    sesion: SesionEditorial,
    destino: EstadoCicloEditorial,
    clock: Callable[[], str] | None = None,
    motivo: str | None = None,
) -> None:
    origen = sesion.estado
    if destino not in _TRANSICIONES_VALIDAS[origen]:
        raise ValueError(
            f"La sesión en estado '{origen.value}' no permite la transición a '{destino.value}'."
        )
    sesion.estado = destino
    sesion.historial_estados.append(
        TransicionEstadoEditorial(
            estado_origen=origen,
            estado_destino=destino,
            ocurrida_en=_now(clock),
            motivo=motivo,
        )
    )


class FilesystemEditorialSessionStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, id_entrada: str) -> Path:
        if not _ID_PATTERN.fullmatch((id_entrada or "").strip()):
            raise ValueError("id_entrada inválido para la sesión editorial.")
        target = (self.base_dir / f"editorial_{id_entrada}").resolve()
        if target.parent != self.base_dir:
            raise ValueError("La sesión editorial sale del directorio base.")
        return target

    def create(self, sesion: SesionEditorial) -> None:
        target = self._session_dir(sesion.id_entrada)
        if target.exists():
            raise ValueError(f"La sesión editorial '{sesion.id_entrada}' ya existe.")
        (target / "versiones").mkdir(parents=True)
        self.save(sesion)

    def load(self, id_entrada: str) -> SesionEditorial:
        path = self._session_dir(id_entrada) / "sesion.json"
        if not path.exists():
            raise ValueError(f"La sesión editorial '{id_entrada}' no existe.")
        return SesionEditorial.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, sesion: SesionEditorial) -> None:
        target = self._session_dir(sesion.id_entrada)
        versiones_dir = target / "versiones"
        versiones_dir.mkdir(parents=True, exist_ok=True)
        version = sesion.versiones[-1]
        version_path = versiones_dir / f"v{version.numero:03d}.md"
        if not version_path.exists():
            fd_version, temp_version_path = tempfile.mkstemp(
                prefix=f".v{version.numero:03d}_", suffix=".md", dir=versiones_dir
            )
            try:
                with os.fdopen(fd_version, "w", encoding="utf-8") as handle:
                    handle.write(version.texto)
                os.replace(temp_version_path, version_path)
            finally:
                if os.path.exists(temp_version_path):
                    os.unlink(temp_version_path)

        fd, temp_path = tempfile.mkstemp(prefix=".sesion_", suffix=".json", dir=target)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(sesion.model_dump_json(indent=2))
            os.replace(temp_path, target / "sesion.json")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def generar_borrador_pendiente(
    entrada: EntradaContenido,
    adapter: ModelAdapter,
    store: FilesystemEditorialSessionStore,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
    clock: Callable[[], str] | None = None,
) -> SesionEditorial:
    post, diagnostico, idea = generar_candidato_textual(
        entrada, adapter, profile_resolver, channel_strategy
    )
    version = VersionBorradorEditorial(
        numero=1,
        texto=post.texto,
        idea_central=idea.idea_central,
        ideas_candidatas=idea.ideas_candidatas,
        diagnostico_editorial=diagnostico,
        creada_en=_now(clock),
    )
    sesion = SesionEditorial(
        id_entrada=entrada.id_entrada,
        entrada=entrada,
        estado=EstadoCicloEditorial.PENDIENTE_REVISION,
        versiones=[version],
        version_actual=1,
        historial_estados=[
            TransicionEstadoEditorial(
                estado_destino=EstadoCicloEditorial.PENDIENTE_REVISION,
                ocurrida_en=_now(clock),
                motivo="Borrador inicial generado.",
            )
        ],
    )
    store.create(sesion)
    return sesion


def solicitar_ajustes(
    id_entrada: str,
    feedback: str,
    adapter: ModelAdapter,
    store: FilesystemEditorialSessionStore,
    profile_resolver: NarrativeProfileResolver | None = None,
    channel_strategy: TextChannelStrategy | None = None,
    clock: Callable[[], str] | None = None,
) -> SesionEditorial:
    feedback_limpio = _validar_texto_controlado(feedback, "feedback")
    sesion = store.load(id_entrada)
    _transicionar(
        sesion,
        EstadoCicloEditorial.REQUIERE_AJUSTES,
        clock=clock,
        motivo=feedback_limpio,
    )
    anterior = sesion.versiones[-1]

    class _FeedbackAdapter:
        def generar_texto(self, prompt: str, system_instruction: str | None = None) -> str:
            prompt_revision = (
                f"Objetivo del post: Revisión solicitada: {feedback_limpio}\n"
                f"{prompt}\nBorrador anterior: {anterior.texto}\n"
                f"Feedback de revisión: {feedback_limpio}\n"
                "Genera una nueva versión que aplique el feedback sin inventar datos."
            )
            return adapter.generar_texto(prompt_revision, system_instruction)

    post, diagnostico, idea = generar_candidato_textual(
        sesion.entrada, _FeedbackAdapter(), profile_resolver, channel_strategy
    )
    numero = anterior.numero + 1
    sesion.versiones.append(
        VersionBorradorEditorial(
            numero=numero,
            texto=post.texto,
            idea_central=idea.idea_central,
            ideas_candidatas=idea.ideas_candidatas,
            diagnostico_editorial=diagnostico,
            creada_en=_now(clock),
            version_anterior=anterior.numero,
            feedback_origen=feedback_limpio,
        )
    )
    sesion.version_actual = numero
    _transicionar(sesion, EstadoCicloEditorial.PENDIENTE_REVISION, clock=clock)
    sesion.aprobacion = None
    sesion.version_aprobada = None
    store.save(sesion)
    return sesion


def aprobar_version(
    id_entrada: str,
    version: int,
    aprobado_por: str,
    fecha_aprobacion: str,
    store: FilesystemEditorialSessionStore,
    tipo_aprobacion: TipoAprobacion = TipoAprobacion.SIMPLE,
    motivo_revision_reforzada: str | None = None,
) -> SesionEditorial:
    sesion = store.load(id_entrada)
    versiones = {item.numero: item for item in sesion.versiones}
    if version not in versiones:
        raise ValueError(f"La versión {version} no existe.")
    motivo_limpio = (
        _validar_texto_controlado(motivo_revision_reforzada, "motivo_revision_reforzada")
        if tipo_aprobacion == TipoAprobacion.REFORZADA
        else None
    )
    aprobacion = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por=_validar_texto_controlado(aprobado_por, "aprobado_por"),
        fecha_aprobacion=fecha_aprobacion,
        tipo_aprobacion=tipo_aprobacion,
        revision_reforzada_requerida=(tipo_aprobacion == TipoAprobacion.REFORZADA),
        motivo_revision_reforzada=motivo_limpio,
    )
    # Ejecuta las mismas reglas en memoria que se aplicarán al preparar la
    # salida; la sesión no se anuncia aprobada si la versión no es preparable.
    ensamblar_flujo_local_simulado(
        sesion.entrada,
        PostCandidato(texto=versiones[version].texto),
        versiones[version].diagnostico_editorial,
        aprobacion,
    )
    _transicionar(sesion, EstadoCicloEditorial.APROBADO)
    sesion.aprobacion = aprobacion
    sesion.version_aprobada = version
    sesion.version_actual = version
    sesion.estado = EstadoCicloEditorial.APROBADO
    store.save(sesion)
    return sesion


def rechazar_version(
    id_entrada: str,
    version: int,
    motivo: str,
    store: FilesystemEditorialSessionStore,
) -> SesionEditorial:
    sesion = store.load(id_entrada)
    versiones = {item.numero: item for item in sesion.versiones}
    if version not in versiones:
        raise ValueError(f"La versión {version} no existe.")
    versiones[version].feedback_origen = _validar_texto_controlado(motivo, "motivo")
    sesion.version_actual = version
    sesion.version_aprobada = None
    aprobacion = AprobacionHumana(
        estado=EstadoAprobacion.RECHAZADO,
        comentarios=versiones[version].feedback_origen,
    )
    _transicionar(
        sesion,
        EstadoCicloEditorial.RECHAZADO,
        motivo=versiones[version].feedback_origen,
    )
    sesion.aprobacion = aprobacion
    store.save(sesion)
    return sesion


def preparar_salida_aprobada(
    id_entrada: str,
    store: FilesystemEditorialSessionStore,
    publisher: PublicationPublisherPort,
) -> ManifestEvidencia:
    sesion = store.load(id_entrada)
    if (
        sesion.estado != EstadoCicloEditorial.APROBADO
        or sesion.aprobacion is None
        or sesion.version_aprobada is None
    ):
        raise ValueError("Solo una versión aprobada puede prepararse para el publisher.")
    version = next(item for item in sesion.versiones if item.numero == sesion.version_aprobada)
    manifest = generar_borrador_local_desde_simulacion(
        entrada=sesion.entrada,
        post=PostCandidato(texto=version.texto),
        diagnostico=version.diagnostico_editorial,
        aprobacion=sesion.aprobacion,
        publisher=publisher,
    )
    _transicionar(sesion, EstadoCicloEditorial.PREPARADO)
    store.save(sesion)
    return manifest
