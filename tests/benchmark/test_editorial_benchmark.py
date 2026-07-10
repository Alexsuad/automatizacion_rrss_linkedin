import json
from pathlib import Path

import pytest

from linkedin_content_system.benchmark.editorial import ejecutar_benchmark_local


BENCHMARK_DIR = Path("benchmarks/editorial")


def test_benchmark_contiene_cinco_entradas_y_dos_perfiles_sinteticos():
    fixtures = json.loads((BENCHMARK_DIR / "fixtures.json").read_text(encoding="utf-8"))
    perfiles = {item["perfil_narrativo"]["id_perfil"] for item in fixtures}

    assert len(fixtures) == 5
    assert perfiles == {"perfil_claro", "perfil_reflexivo"}
    assert all(item["estado_privacidad"]["sanitizado"] for item in fixtures)


def test_benchmark_local_genera_cinco_sesiones_sin_publicar(tmp_path):
    resultados = ejecutar_benchmark_local(
        fixtures_path=BENCHMARK_DIR / "fixtures.json",
        profiles_dir=BENCHMARK_DIR / "profiles",
        output_dir=tmp_path,
    )

    assert len(resultados) == 5
    assert all(resultado["estado_tecnico"] == "PASS" for resultado in resultados)
    assert len(list(tmp_path.glob("editorial_*"))) == 5
    assert not list(tmp_path.glob("localdraft_*"))


def test_benchmark_bloquea_fixture_con_pii_antes_de_generar(tmp_path):
    fixtures = json.loads((BENCHMARK_DIR / "fixtures.json").read_text(encoding="utf-8"))
    fixtures[0]["texto_base"] = "Contacta con persona@dominio.com para ampliar datos."
    fixture_inseguro = tmp_path / "fixtures_inseguros.json"
    fixture_inseguro.write_text(json.dumps(fixtures), encoding="utf-8")

    with pytest.raises(ValueError, match="correo electrónico"):
        ejecutar_benchmark_local(
            fixtures_path=fixture_inseguro,
            profiles_dir=BENCHMARK_DIR / "profiles",
            output_dir=tmp_path / "salida",
        )

    assert not list((tmp_path / "salida").glob("editorial_*"))


def test_resultado_humano_declara_metadatos_y_no_confunde_base_con_publicacion():
    resultado = json.loads(
        (BENCHMARK_DIR / "results_local_controlled.json").read_text(encoding="utf-8")
    )

    assert resultado["evaluado_por"]
    assert resultado["fecha_evaluacion"]
    assert resultado["version_rubrica"]
    assert resultado["hash_fixture"]
    assert resultado["conclusion"].startswith("5/5 aprovechables como base editable")
