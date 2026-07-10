from __future__ import annotations

import argparse
import json
from pathlib import Path

from linkedin_content_system.ai import ControlledModelAdapter
from linkedin_content_system.contracts import EntradaContenido
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore,
    generar_borrador_pendiente,
)
from linkedin_content_system.use_cases.ejecutar_flujo_textual import (
    validar_entrada_generable,
)
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
)


def ejecutar_benchmark_local(
    fixtures_path: str | Path,
    profiles_dir: str | Path,
    output_dir: str | Path,
) -> list[dict[str, object]]:
    fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
    entradas = [EntradaContenido.model_validate(item) for item in fixtures]

    # El lote completo pasa el gate antes de invocar el adapter para evitar
    # evidencia parcial si un fixture resulta inseguro.
    for entrada in entradas:
        validar_entrada_generable(entrada)

    store = FilesystemEditorialSessionStore(output_dir)
    resolver = FilesystemNarrativeProfileResolver(profiles_dir)
    strategy = LinkedInTextChannelStrategy()
    resultados = []
    for entrada in entradas:
        sesion = generar_borrador_pendiente(
            entrada=entrada,
            adapter=ControlledModelAdapter(),
            store=store,
            profile_resolver=resolver,
            channel_strategy=strategy,
        )
        version = sesion.versiones[-1]
        resultados.append(
            {
                "id_entrada": entrada.id_entrada,
                "version": version.numero,
                "estado_tecnico": "PASS",
                "estado_editorial": "PENDIENTE_REVISION_HUMANA",
                "evidencia_relativa": (
                    f"editorial_{entrada.id_entrada}/versiones/v{version.numero:03d}.md"
                ),
            }
        )
    return resultados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta el benchmark editorial local sintético.")
    parser.add_argument("--fixtures", default="benchmarks/editorial/fixtures.json")
    parser.add_argument("--profiles-dir", default="benchmarks/editorial/profiles")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    resultados = ejecutar_benchmark_local(args.fixtures, args.profiles_dir, args.output_dir)
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
