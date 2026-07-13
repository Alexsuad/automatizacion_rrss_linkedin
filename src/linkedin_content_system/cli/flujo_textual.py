import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

from pydantic import ValidationError

from linkedin_content_system.ai import LiteLLMAdapterError, construir_model_adapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    EntradaContenido,
    EstadoAprobacion,
    TipoAprobacion,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoEntrada,
)
from linkedin_content_system.publishers import ExternalDryRunPublisher, LocalDraftPublisher
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
)
from linkedin_content_system.use_cases import (
    FilesystemEditorialSessionStore,
    aprobar_version,
    ejecutar_flujo_textual,
    generar_borrador_pendiente,
    preparar_salida_aprobada,
    rechazar_version,
    solicitar_ajustes,
)
from linkedin_content_system.use_cases.normalizar_entrada_textual import cargar_documento_textual


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta el flujo textual local hasta LocalDraft.")
    entrada = parser.add_mutually_exclusive_group()
    entrada.add_argument("--input-json", help="Ruta al archivo JSON con EntradaContenido.")
    entrada.add_argument("--texto", help="Texto manual para generar sin preparar JSON.")
    entrada.add_argument("--documento", help="Documento .txt o .md para normalizar localmente.")
    entrada.add_argument("--borrador", help="Borrador existente para revisar y mejorar.")
    parser.add_argument("--output-dir", required=True, help="Directorio base donde se guardara el LocalDraft.")
    parser.add_argument(
        "--accion",
        default="generar",
        choices=["generar", "ajustar", "aprobar", "rechazar", "preparar"],
        help="Etapa del ciclo editorial local.",
    )
    parser.add_argument("--id-entrada", help="Identificador seguro de la entrada o sesión.")
    parser.add_argument("--perfil", default="perfil_default", help="Identificador del perfil narrativo.")
    parser.add_argument(
        "--vista",
        choices=["cliente", "administrador"],
        default="administrador",
        help="Nivel de detalle mostrado tras generar o ajustar.",
    )
    parser.add_argument(
        "--publisher",
        choices=["localdraft", "external-dry-run"],
        default="localdraft",
        help="Destino local disponible únicamente después de aprobar.",
    )
    parser.add_argument("--feedback", help="Feedback textual para crear una nueva versión.")
    parser.add_argument("--version", type=int, help="Versión que se desea aprobar.")
    parser.add_argument(
        "--estado-aprobacion",
        required=False,
        choices=["aprobado", "pendiente", "rechazado", "requiere_ajustes"],
        help="Estado de aprobacion humana para el flujo.",
    )
    parser.add_argument("--revisor", help="Nombre del revisor.")
    parser.add_argument("--fecha-aprobacion", help="Fecha ISO8601 de aprobacion.")
    parser.add_argument("--comentarios", help="Comentarios de revision.")
    parser.add_argument(
        "--tipo-aprobacion",
        default="simple",
        choices=["simple", "reforzada"],
        help="Tipo de aprobacion humana.",
    )
    parser.add_argument(
        "--motivo-revision-reforzada",
        help="Motivo obligatorio cuando la aprobacion es reforzada.",
    )
    return parser


def _leer_entrada(path: str) -> EntradaContenido:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return EntradaContenido.model_validate(data)


def _build_aprobacion(args: argparse.Namespace) -> AprobacionHumana:
    if not args.estado_aprobacion:
        raise ValueError("estado_aprobacion es obligatorio en el flujo legacy.")
    estado = {
        "aprobado": EstadoAprobacion.APROBADO,
        "pendiente": EstadoAprobacion.PENDIENTE,
        "rechazado": EstadoAprobacion.RECHAZADO,
        "requiere_ajustes": EstadoAprobacion.REQUIERE_AJUSTES,
    }[args.estado_aprobacion]

    tipo_aprobacion = {
        "simple": TipoAprobacion.SIMPLE,
        "reforzada": TipoAprobacion.REFORZADA,
    }[args.tipo_aprobacion]

    fecha_aprobacion = args.fecha_aprobacion
    if estado == EstadoAprobacion.APROBADO and not fecha_aprobacion:
        fecha_aprobacion = datetime.now(timezone.utc).isoformat()

    return AprobacionHumana(
        estado=estado,
        aprobado_por=args.revisor,
        fecha_aprobacion=fecha_aprobacion,
        comentarios=args.comentarios,
        tipo_aprobacion=tipo_aprobacion,
        revision_reforzada_requerida=(tipo_aprobacion == TipoAprobacion.REFORZADA),
        motivo_revision_reforzada=args.motivo_revision_reforzada,
    )


def _entrada_desde_texto(args: argparse.Namespace) -> EntradaContenido:
    if not args.id_entrada:
        raise ValueError("--id-entrada es obligatorio cuando se usa --texto.")
    return EntradaContenido(
        id_entrada=args.id_entrada,
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base=args.texto,
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.TENTATIVA,
            idea_central=args.texto.strip()[:280],
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil=args.perfil),
        canales_destino=["linkedin"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


def _entrada_desde_documento(args: argparse.Namespace) -> EntradaContenido:
    if not args.id_entrada:
        raise ValueError("--id-entrada es obligatorio cuando se usa --documento.")
    contenido = cargar_documento_textual(args.documento)
    return EntradaContenido(
        id_entrada=args.id_entrada,
        tipo_entrada=TipoEntrada.DOCUMENTO_BASE,
        texto_base=contenido,
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.TENTATIVA,
            idea_central=contenido.strip()[:280],
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil=args.perfil),
        canales_destino=["linkedin"],
        metadatos_origen={"referencia_fuente": f"documento_{args.id_entrada}"},
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


def _entrada_desde_borrador(args: argparse.Namespace) -> EntradaContenido:
    if not args.id_entrada:
        raise ValueError("--id-entrada es obligatorio cuando se usa --borrador.")
    return EntradaContenido(
        id_entrada=args.id_entrada,
        tipo_entrada=TipoEntrada.BORRADOR_EXISTENTE,
        texto_base=args.borrador,
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.TENTATIVA,
            idea_central=args.borrador.strip()[:280],
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil=args.perfil),
        canales_destino=["linkedin"],
        metadatos_origen={"referencia_fuente": f"borrador_{args.id_entrada}"},
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


def _sha256_file(path: str | None) -> str | None:
    if not path:
        return None
    file_path = os.fspath(path)
    if not os.path.isfile(file_path):
        return None
    return hashlib.sha256(open(file_path, "rb").read()).hexdigest()


def _commit_actual() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _evidencia_ejecucion_inicial(args: argparse.Namespace, entrada, adapter) -> dict[str, object]:
    profile_dir = os.getenv("LINKEDIN_CONTENT_PROFILE_DIR")
    profile_path = (
        os.path.join(profile_dir, f"{entrada.perfil_narrativo.id_perfil}.json")
        if profile_dir
        else None
    )
    evidencia = {
        "adapter": os.getenv("LINKEDIN_CONTENT_AI_ADAPTER", "controlado"),
        "proveedor": getattr(adapter, "proveedor", None),
        "modelo": getattr(adapter, "modelo", None),
        "timeout_seconds": getattr(adapter, "timeout_seconds", None),
        "max_tokens": getattr(adapter, "max_tokens", None),
        "commit": _commit_actual(),
        "fixture_sha256": _sha256_file(args.input_json),
        "perfil_sha256": _sha256_file(profile_path),
    }
    return {clave: valor for clave, valor in evidencia.items() if valor is not None}


def _mostrar_sesion_cliente(sesion) -> None:
    version = next(item for item in sesion.versiones if item.numero == sesion.version_actual)
    print(f"Canal: linkedin")
    print(f"Fuente: {sesion.entrada.tipo_entrada.value.replace('_', ' ')}")
    print(f"Versión: v{version.numero:03d}")
    intencion = (
        sesion.entrada.intencion_editorial.objetivo_del_post
        or sesion.entrada.intencion_editorial.estado_intencion_editorial.value
    )
    print(f"Intención: {intencion}")
    print(f"Perfil: {sesion.entrada.perfil_narrativo.id_perfil}")
    estados_legibles = {
        "pendiente_revision": "pendiente de revisión",
        "requiere_ajustes": "requiere ajustes",
    }
    print(f"Estado editorial: {estados_legibles.get(sesion.estado.value, sesion.estado.value)}")
    print("Observación editorial: requiere revisión humana antes de preparar una salida.")
    print("Acciones disponibles: aprobar, ajustar o rechazar.")
    print("\nBorrador:\n")
    print(version.texto)


def _mostrar_sesion_administrador(sesion) -> None:
    version = next(item for item in sesion.versiones if item.numero == sesion.version_actual)
    _mostrar_sesion_cliente(sesion)
    print("\nAdministración:")
    print(f"Entrada: {sesion.id_entrada}")
    print(f"Idea usada: {version.idea_central}")
    print(f"Perfil: {sesion.entrada.perfil_narrativo.id_perfil}")
    print(f"Validación técnica: {(sesion.evidencia_ejecucion or {}).get('estado_tecnico', 'NO_REGISTRADO')}")
    print(f"Validación estructural: {version.diagnostico_editorial.compliance.value}")
    print(f"Evaluación editorial automática: {version.diagnostico_editorial.estado_revision.value}")
    print(f"Decisión humana: {sesion.aprobacion.estado.value if sesion.aprobacion else 'pendiente'}")
    print(f"Trazabilidad: {version.trazabilidad_fuente or {}}")
    print(f"Evidencia: {sesion.evidencia_ejecucion or {}}")


def _mostrar_sesion(sesion, vista: str) -> None:
    if vista == "administrador":
        _mostrar_sesion_administrador(sesion)
    else:
        _mostrar_sesion_cliente(sesion)


def _construir_publisher(args: argparse.Namespace):
    if args.publisher == "external-dry-run":
        return ExternalDryRunPublisher(base_dir=args.output_dir)
    return LocalDraftPublisher(base_dir=args.output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        profile_resolver = FilesystemNarrativeProfileResolver(
            profile_dir=os.getenv("LINKEDIN_CONTENT_PROFILE_DIR")
        )
        channel_strategy = LinkedInTextChannelStrategy()

        # Compatibilidad temporal del flujo anterior: solo se activa si se
        # proporciona explícitamente un estado de aprobación.
        if args.estado_aprobacion:
            if not args.input_json:
                raise ValueError("--input-json es obligatorio en el flujo legacy.")
            entrada = _leer_entrada(args.input_json)
            manifest = ejecutar_flujo_textual(
                entrada=entrada,
                adapter=construir_model_adapter(),
                aprobacion=_build_aprobacion(args),
                base_dir=args.output_dir,
                publisher=LocalDraftPublisher(base_dir=args.output_dir),
                profile_resolver=profile_resolver,
                channel_strategy=channel_strategy,
            )
            print(
                f"LocalDraft generado para {manifest.id_entrada}: "
                f"localdraft_{manifest.id_entrada} ({manifest.id_evidencia})"
            )
            return 0

        store = FilesystemEditorialSessionStore(args.output_dir)
        if args.accion == "generar":
            if not args.input_json and not args.texto and not args.documento and not args.borrador:
                raise ValueError("Debes indicar --input-json, --texto, --documento o --borrador para generar.")
            entrada = (
                _leer_entrada(args.input_json)
                if args.input_json
                else _entrada_desde_documento(args)
                if args.documento
                else _entrada_desde_borrador(args)
                if args.borrador
                else _entrada_desde_texto(args)
            )
            adapter = construir_model_adapter()
            evidencia_ejecucion = _evidencia_ejecucion_inicial(args, entrada, adapter)
            inicio = time.monotonic()
            sesion = generar_borrador_pendiente(
                entrada=entrada,
                adapter=adapter,
                store=store,
                profile_resolver=profile_resolver,
                channel_strategy=channel_strategy,
                evidencia_ejecucion=evidencia_ejecucion,
            )
            version = sesion.versiones[-1]
            evidencia_ejecucion.update(
                {
                    "duracion_ms": round((time.monotonic() - inicio) * 1000),
                    "exit_code": 0,
                    "estado_tecnico": "PASS",
                    "estado_estructural": version.diagnostico_editorial.compliance.value,
                    "estado_editorial": version.diagnostico_editorial.estado_revision.value,
                    "estado_revision_automatica": version.diagnostico_editorial.estado_revision.value,
                    "estado_sesion": sesion.estado.value,
                    "decision_humana": "PENDIENTE",
                    "salida_sha256": hashlib.sha256(version.texto.encode("utf-8")).hexdigest(),
                    "sin_publicacion": True,
                    "sin_localdraft": True,
                }
            )
            sesion.evidencia_ejecucion = evidencia_ejecucion
            store.save(sesion)
            _mostrar_sesion(sesion, args.vista)
            return 0

        if not args.id_entrada:
            raise ValueError("--id-entrada es obligatorio para esta acción.")
        if args.accion == "ajustar":
            sesion = solicitar_ajustes(
                args.id_entrada,
                args.feedback,
                construir_model_adapter(),
                store,
                profile_resolver,
                channel_strategy,
            )
            _mostrar_sesion(sesion, args.vista)
            return 0
        if args.accion == "aprobar":
            if not args.version or not args.revisor:
                raise ValueError("--version y --revisor son obligatorios para aprobar.")
            sesion = aprobar_version(
                args.id_entrada,
                args.version,
                args.revisor,
                args.fecha_aprobacion or datetime.now(timezone.utc).isoformat(),
                store,
                tipo_aprobacion={
                    "simple": TipoAprobacion.SIMPLE,
                    "reforzada": TipoAprobacion.REFORZADA,
                }[args.tipo_aprobacion],
                motivo_revision_reforzada=args.motivo_revision_reforzada,
            )
            print(f"Versión v{sesion.version_aprobada:03d} aprobada para {sesion.id_entrada}.")
            return 0
        if args.accion == "rechazar":
            if not args.version or not args.feedback:
                raise ValueError("--version y --feedback son obligatorios para rechazar.")
            sesion = rechazar_version(
                args.id_entrada,
                args.version,
                args.feedback,
                store,
            )
            print(f"Versión v{sesion.version_actual:03d} rechazada para {sesion.id_entrada}.")
            return 0
        manifest = preparar_salida_aprobada(
            args.id_entrada,
            store,
            _construir_publisher(args),
        )
        print(f"Salida local preparada para {manifest.id_entrada}: {manifest.id_evidencia}.")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError, ValueError, LiteLLMAdapterError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
