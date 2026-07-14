from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import TipoAprobacion
from linkedin_content_system.publishers import ExternalDryRunPublisher
from linkedin_content_system.transcription import TranscriptionAdapterError, construir_transcriber
from linkedin_content_system.use_cases import (
    FilesystemEditorialSessionStore,
    aprobar_version,
    construir_entrada_desde_audio,
    cargar_metadatos_autorizados,
    generar_borrador_pendiente,
    normalizar_entrada_textual,
    preparar_salida_aprobada,
)


class AdapterSmokeIncremento2(ModelAdapter):
    def __init__(self) -> None:
        self._respuestas = iter(
            [
                "En un mundo donde todo cambia, revisar es importante.",
                "La revision humana precede a la salida. Que revisarias antes de aprobar?",
            ]
        )

    def generar_texto(self, prompt: str, system_instruction: str | None = None) -> str:
        return next(self._respuestas)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta el smoke reproducible del Incremento 2.")
    parser.add_argument("--audio", required=True, help="Archivo de audio sintético o local autorizado.")
    parser.add_argument("--output-dir", required=True, help="Directorio de evidencia del smoke.")
    parser.add_argument("--transcriber", default="fake", choices=["fake", "whisper_cpp"])
    parser.add_argument("--metadata-json", help="JSON de metadatos autorizados; si no se informa se busca junto al audio.")
    parser.add_argument("--perfil", default="perfil_smoke_audio")
    parser.add_argument("--idioma", default="es")
    return parser


def _metadata_por_defecto(audio_path: Path) -> str | None:
    candidate = audio_path.with_name(f"{audio_path.stem}.metadata.json")
    return str(candidate) if candidate.exists() else None


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_parser().parse_args(argv)
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = Path(args.audio).expanduser()

        metadata_path = args.metadata_json or _metadata_por_defecto(audio_path)
        metadata = cargar_metadatos_autorizados(metadata_path)
        transcriber = construir_transcriber(args.transcriber)
        preparacion = construir_entrada_desde_audio(
            audio_path=audio_path,
            transcriber=transcriber,
            profile_id=args.perfil,
            id_entrada="smoke_incremento2",
            canales_destino=["linkedin"],
            language=args.idioma,
            metadatos_autorizados=metadata,
        )

        store = FilesystemEditorialSessionStore(output_dir)
        sesion = generar_borrador_pendiente(
            preparacion.entrada,
            AdapterSmokeIncremento2(),
            store,
            evidencia_ejecucion={
                "estado_tecnico": "PASS",
                "transcripcion_adapter": preparacion.transcripcion.adaptador,
                "transcripcion_modo": preparacion.transcripcion.modo.value,
                "audio_sha256": preparacion.validacion.audio.sha256_audio,
                "transcripcion_sha256": preparacion.sanitizacion.sha256_transcripcion_sanitizada,
                "sin_publicacion": True,
                "sin_localdraft": True,
            },
        )
        aprobada = aprobar_version(
            "smoke_incremento2",
            sesion.version_seleccionada or sesion.version_actual,
            "Revisor Sintetico Audio",
            "2026-07-13T18:00:00Z",
            store,
            TipoAprobacion.REFORZADA,
            "Revision humana simulada para smoke del Incremento 2.",
        )
        manifest = preparar_salida_aprobada(
            "smoke_incremento2",
            store,
            ExternalDryRunPublisher(base_dir=str(output_dir)),
        )

        dry_run_path = output_dir / "external_dryrun_smoke_incremento2" / "publicacion_simulada.json"
        payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
        fuente = normalizar_entrada_textual(preparacion.entrada)
        versiones = [
            {
                "numero": version.numero,
                "archivo": f"editorial_smoke_incremento2/versiones/v{version.numero:03d}.md",
                "auditoria": version.auditoria_editorial.model_dump(mode="json") if version.auditoria_editorial else None,
                "feedback_origen": version.feedback_origen,
            }
            for version in aprobada.versiones
        ]
        resumen = {
            "smoke": "incremento_2",
            "ejecutado_en": datetime.now(timezone.utc).isoformat(),
            "publicado": False,
            "id_entrada": preparacion.entrada.id_entrada,
            "transcripcion_modo": preparacion.transcripcion.modo.value,
            "transcripcion_adapter": preparacion.transcripcion.adaptador,
            "sesion_estado": aprobada.estado.value,
            "version_actual": aprobada.version_actual,
            "version_seleccionada": aprobada.version_seleccionada,
            "version_aprobada": aprobada.version_aprobada,
            "manifest_path": manifest.archivos_generados[0] if manifest.archivos_generados else None,
            "payload_external_dry_run": str(dry_run_path.relative_to(output_dir)),
            "sesion_path": "editorial_smoke_incremento2/sesion.json",
            "audio_path": "metadatos_audio.json",
            "transcripcion_path": "transcripcion_sanitizada.json",
            "fuente_normalizada_path": "fuente_normalizada.json",
        }

        _write_json(output_dir / "manifest.json", manifest.model_dump(mode="json"))
        _write_json(output_dir / "metadatos_audio.json", preparacion.validacion.model_dump(mode="json"))
        _write_json(output_dir / "resultado_validacion.json", preparacion.validacion.model_dump(mode="json"))
        _write_json(output_dir / "transcripcion_sanitizada.json", preparacion.sanitizacion.model_dump(mode="json"))
        _write_json(output_dir / "fuente_normalizada.json", fuente.model_dump(mode="json"))
        _write_json(output_dir / "versiones_auditorias.json", versiones)
        _write_json(
            output_dir / "feedback.json",
            {
                "feedback_interno": [v.feedback_origen for v in aprobada.versiones if v.feedback_origen],
                "motivo_seleccion": aprobada.motivo_seleccion,
            },
        )
        _write_json(output_dir / "version_seleccionada.json", {"version_seleccionada": aprobada.version_seleccionada})
        _write_json(output_dir / "aprobacion_simulada.json", aprobada.aprobacion.model_dump(mode="json"))
        _write_json(output_dir / "resumen_final.json", resumen)
        _write_json(output_dir / "transcripcion_operativa.json", preparacion.transcripcion.model_dump(mode="json"))
        _write_json(output_dir / "payload_external_dry_run.json", payload)

        print(str(output_dir))
        return 0
    except (ValueError, json.JSONDecodeError, OSError, TranscriptionAdapterError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
