from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoAprobacion,
    TipoEntrada,
)
from linkedin_content_system.publishers import ExternalDryRunPublisher
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore,
    aprobar_version,
    generar_borrador_pendiente,
    preparar_salida_aprobada,
)
from linkedin_content_system.use_cases.normalizar_entrada_textual import normalizar_entrada_textual


class AdapterSmokeIncremento1(ModelAdapter):
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
    parser = argparse.ArgumentParser(description="Ejecuta el smoke offline reproducible del Incremento 1.")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directorio raiz donde se guardara la evidencia saneada del smoke.",
    )
    return parser


def _entrada_smoke() -> EntradaContenido:
    return EntradaContenido(
        id_entrada="smoke_incremento1",
        tipo_entrada=TipoEntrada.DOCUMENTO_BASE,
        texto_base="El documento confirma que la revision humana precede a cualquier salida.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            idea_central="La revision humana precede a cualquier salida",
            cta_intencionado="Que revisarias antes de aprobar?",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_smoke"),
        canales_destino=["linkedin"],
        metadatos_origen={
            "referencia_fuente": "smoke_documento_sintetico",
            "hechos_autorizados": ["La revision humana precede a cualquier salida."],
            "opiniones_explicitas": ["La automatizacion no sustituye el criterio."],
            "experiencias_autorizadas": [],
            "afirmaciones_pendientes": ["No afirmar resultados de negocio."],
        },
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    entrada = _entrada_smoke()
    adapter = AdapterSmokeIncremento1()
    store = FilesystemEditorialSessionStore(output_dir)
    sesion = generar_borrador_pendiente(entrada, adapter, store)
    aprobada = aprobar_version(
        entrada.id_entrada,
        sesion.version_seleccionada or sesion.version_actual,
        "Revisor Sintetico",
        "2026-07-13T12:00:00Z",
        store,
        TipoAprobacion.REFORZADA,
        "Revision humana simulada.",
    )
    manifest = preparar_salida_aprobada(
        entrada.id_entrada,
        store,
        ExternalDryRunPublisher(base_dir=str(output_dir)),
    )

    sesion_path = output_dir / f"editorial_{entrada.id_entrada}" / "sesion.json"
    fuente = normalizar_entrada_textual(entrada)
    dry_run_path = output_dir / f"external_dryrun_{entrada.id_entrada}" / "publicacion_simulada.json"
    payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
    versiones = [
        {
            "numero": version.numero,
            "archivo": f"editorial_{entrada.id_entrada}/versiones/v{version.numero:03d}.md",
            "auditoria": version.auditoria_editorial.model_dump(mode="json") if version.auditoria_editorial else None,
            "feedback_origen": version.feedback_origen,
        }
        for version in aprobada.versiones
    ]
    resumen = {
        "smoke": "incremento_1",
        "ejecutado_en": datetime.now(timezone.utc).isoformat(),
        "publicado": False,
        "id_entrada": entrada.id_entrada,
        "sesion_estado": aprobada.estado.value,
        "version_actual": aprobada.version_actual,
        "version_seleccionada": aprobada.version_seleccionada,
        "version_aprobada": aprobada.version_aprobada,
        "mejora_editorial_demostrada": aprobada.mejora_editorial_demostrada,
        "manifest_path": manifest.archivos_generados[0] if manifest.archivos_generados else None,
        "payload_external_dry_run": str(dry_run_path.relative_to(output_dir)),
        "sesion_path": str(sesion_path.relative_to(output_dir)),
        "fuente_normalizada_path": "fuente_normalizada.json",
        "feedback_path": "feedback.json",
        "versiones_path": "versiones_auditorias.json",
        "aprobacion_path": "aprobacion_simulada.json",
    }

    _write_json(output_dir / "manifest.json", manifest.model_dump(mode="json"))
    _write_json(output_dir / "fuente_normalizada.json", fuente.model_dump(mode="json"))
    _write_json(
        output_dir / "feedback.json",
        {
            "feedback_interno": [v.feedback_origen for v in aprobada.versiones if v.feedback_origen],
            "motivo_seleccion": aprobada.motivo_seleccion,
        },
    )
    _write_json(output_dir / "versiones_auditorias.json", versiones)
    _write_json(output_dir / "version_seleccionada.json", {"version_seleccionada": aprobada.version_seleccionada})
    _write_json(output_dir / "aprobacion_simulada.json", aprobada.aprobacion.model_dump(mode="json"))
    _write_json(output_dir / "resumen_final.json", resumen)

    print(str(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
