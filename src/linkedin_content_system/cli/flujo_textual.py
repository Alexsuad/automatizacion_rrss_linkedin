import argparse
import json
import sys
from datetime import datetime, timezone

from pydantic import ValidationError

from linkedin_content_system.ai import construir_model_adapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    EntradaContenido,
    EstadoAprobacion,
    TipoAprobacion,
)
from linkedin_content_system.use_cases import ejecutar_flujo_textual


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta el flujo textual local hasta LocalDraft.")
    parser.add_argument("--input-json", required=True, help="Ruta al archivo JSON con EntradaContenido.")
    parser.add_argument("--output-dir", required=True, help="Directorio base donde se guardara el LocalDraft.")
    parser.add_argument(
        "--estado-aprobacion",
        required=True,
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


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        entrada = _leer_entrada(args.input_json)
        aprobacion = _build_aprobacion(args)
        manifest = ejecutar_flujo_textual(
            entrada=entrada,
            adapter=construir_model_adapter(),
            aprobacion=aprobacion,
            base_dir=args.output_dir,
        )
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"LocalDraft generado para {manifest.id_entrada}: "
        f"localdraft_{manifest.id_entrada} ({manifest.id_evidencia})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
