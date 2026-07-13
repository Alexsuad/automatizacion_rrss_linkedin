from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from linkedin_content_system.ai import ControlledModelAdapter, construir_model_adapter
from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import EntradaContenido
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore,
    generar_borrador_pendiente,
    solicitar_ajustes,
)
from linkedin_content_system.use_cases.ejecutar_flujo_textual import (
    validar_entrada_generable,
)
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
)


def _sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha256_text(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


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


def ejecutar_benchmark_local(
    fixtures_path: str | Path,
    profiles_dir: str | Path,
    output_dir: str | Path,
    adapter: ModelAdapter | None = None,
    feedback_plan: dict[str, str] | None = None,
) -> dict[str, object]:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    entradas = [EntradaContenido.model_validate(item) for item in fixtures]

    # El lote completo pasa el gate antes de invocar el adapter para evitar
    # evidencia parcial si un fixture resulta inseguro.
    for entrada in entradas:
        validar_entrada_generable(entrada)

    store = FilesystemEditorialSessionStore(output_dir)
    resolver = FilesystemNarrativeProfileResolver(profiles_dir)
    strategy = LinkedInTextChannelStrategy()
    adapter_resuelto = adapter or ControlledModelAdapter()
    feedback_resuelto = feedback_plan or {}
    commit = _commit_actual()
    fixture_sha256 = _sha256_file(fixtures_path)
    resultados = []
    feedback_resultados = []

    for entrada in entradas:
        profile_path = Path(profiles_dir) / f"{entrada.perfil_narrativo.id_perfil}.json"
        inicio = time.monotonic()
        sesion = generar_borrador_pendiente(
            entrada=entrada,
            adapter=adapter_resuelto,
            store=store,
            profile_resolver=resolver,
            channel_strategy=strategy,
            evidencia_ejecucion={
                "adapter": adapter_resuelto.__class__.__name__,
                "proveedor": getattr(adapter_resuelto, "proveedor", None),
                "modelo": getattr(adapter_resuelto, "modelo", None),
                "timeout_seconds": getattr(adapter_resuelto, "timeout_seconds", None),
                "max_tokens": getattr(adapter_resuelto, "max_tokens", None),
                "commit": commit,
                "fixture_sha256": fixture_sha256,
                "perfil_sha256": _sha256_file(profile_path),
                "sin_publicacion": True,
                "sin_localdraft": True,
            },
        )
        version = sesion.versiones[-1]
        evidencia = sesion.evidencia_ejecucion or {}
        evidencia.update(
            {
                "duracion_ms": round((time.monotonic() - inicio) * 1000),
                "exit_code": 0,
                "estado_tecnico": "PASS",
                "estado_estructural": version.diagnostico_editorial.compliance.value,
                "estado_editorial": version.diagnostico_editorial.estado_revision.value,
                "estado_revision_automatica": version.diagnostico_editorial.estado_revision.value,
                "estado_sesion": sesion.estado.value,
                "decision_humana": "PENDIENTE",
                "salida_sha256": _sha256_text(version.texto),
            }
        )
        sesion.evidencia_ejecucion = {k: v for k, v in evidencia.items() if v is not None}
        store.save(sesion)
        resultados.append(
            {
                "id_entrada": entrada.id_entrada,
                "version": version.numero,
                "duracion_ms": sesion.evidencia_ejecucion["duracion_ms"],
                "estado_tecnico": "PASS",
                "estado_estructural": version.diagnostico_editorial.compliance.value,
                "estado_editorial": version.diagnostico_editorial.estado_revision.value,
                "decision_humana": "PENDIENTE",
                "evidencia_relativa": (
                    f"editorial_{entrada.id_entrada}/versiones/v{version.numero:03d}.md"
                ),
                "sesion_relativa": f"editorial_{entrada.id_entrada}/sesion.json",
                "salida_sha256": sesion.evidencia_ejecucion["salida_sha256"],
            }
        )

        feedback = feedback_resuelto.get(entrada.id_entrada)
        if not feedback:
            continue

        inicio_feedback = time.monotonic()
        sesion_ajustada = solicitar_ajustes(
            id_entrada=entrada.id_entrada,
            feedback=feedback,
            adapter=adapter_resuelto,
            store=store,
            profile_resolver=resolver,
            channel_strategy=strategy,
        )
        version_v2 = sesion_ajustada.versiones[-1]
        evidencia_ajuste = sesion_ajustada.evidencia_ejecucion or {}
        feedback_ciclos = evidencia_ajuste.setdefault("feedback_ciclos", [])
        ciclo = {
            "id_entrada": entrada.id_entrada,
            "feedback": feedback,
            "version_origen": version.numero,
            "version_nueva": version_v2.numero,
            "duracion_ms": round((time.monotonic() - inicio_feedback) * 1000),
            "estado_tecnico": "PASS",
            "estado_estructural": version_v2.diagnostico_editorial.compliance.value,
            "estado_editorial": version_v2.diagnostico_editorial.estado_revision.value,
            "decision_humana": "PENDIENTE",
            "texto_cambio": version.texto != version_v2.texto,
            "delta_caracteres": len(version_v2.texto) - len(version.texto),
            "salida_sha256": _sha256_text(version_v2.texto),
            "evidencia_relativa": (
                f"editorial_{entrada.id_entrada}/versiones/v{version_v2.numero:03d}.md"
            ),
        }
        feedback_ciclos.append(ciclo)
        sesion_ajustada.evidencia_ejecucion = evidencia_ajuste
        store.save(sesion_ajustada)
        feedback_resultados.append(ciclo)

    resumen = {
        "adapter": adapter_resuelto.__class__.__name__,
        "proveedor": getattr(adapter_resuelto, "proveedor", None),
        "modelo": getattr(adapter_resuelto, "modelo", None),
        "commit": commit,
        "fixtures_sha256": fixture_sha256,
        "feedback_sha256": _sha256_text(json.dumps(feedback_resuelto, sort_keys=True)),
        "total_piezas": len(resultados),
        "piezas_con_feedback": len(feedback_resultados),
        "resultados": resultados,
        "feedback_resultados": feedback_resultados,
    }
    Path(output_dir, "benchmark_resumen.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return resumen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta el benchmark editorial local sintético.")
    parser.add_argument("--fixtures", default="benchmarks/editorial/fixtures.json")
    parser.add_argument("--profiles-dir", default="benchmarks/editorial/profiles")
    parser.add_argument("--feedback-json", help="Ruta opcional con feedback por id_entrada.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    feedback_plan = None
    if args.feedback_json:
        feedback_plan = json.loads(Path(args.feedback_json).read_text(encoding="utf-8"))
    resultados = ejecutar_benchmark_local(
        args.fixtures,
        args.profiles_dir,
        args.output_dir,
        adapter=construir_model_adapter(),
        feedback_plan=feedback_plan,
    )
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
