import json
from pathlib import Path

import pytest

from linkedin_content_system.ai.ports import ModelAdapter
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

    assert resultados["total_piezas"] == 5
    assert all(resultado["estado_tecnico"] == "PASS" for resultado in resultados["resultados"])
    assert len(list(tmp_path.glob("editorial_*"))) == 5
    assert not list(tmp_path.glob("localdraft_*"))
    assert (tmp_path / "benchmark_resumen.json").exists()


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


def test_benchmark_puede_usar_adapter_inyectado_y_registrar_feedback(tmp_path):
    class FakeAdapter(ModelAdapter):
        def __init__(self):
            self.calls = []

        def generar_texto(self, prompt: str, system_instruction: str | None = None) -> str:
            self.calls.append({"prompt": prompt, "system_instruction": system_instruction})
            return (
                "Una decisión revisable mejora la automatización.\n"
                "Conviene observar qué se automatiza primero.\n"
                "¿Qué revisarías antes de publicar?"
            )

    adapter = FakeAdapter()
    resultados = ejecutar_benchmark_local(
        fixtures_path=BENCHMARK_DIR / "fixtures.json",
        profiles_dir=BENCHMARK_DIR / "profiles",
        output_dir=tmp_path,
        adapter=adapter,
        feedback_plan=json.loads((BENCHMARK_DIR / "feedback_plan.json").read_text(encoding="utf-8")),
    )

    assert resultados["adapter"] == "FakeAdapter"
    assert resultados["total_piezas"] == 5
    assert resultados["piezas_con_feedback"] == 2
    assert len(adapter.calls) == 7
    assert all(item["decision_humana"] == "PENDIENTE" for item in resultados["resultados"])
    assert all(item["texto_cambio"] is False for item in resultados["feedback_resultados"])
    assert {
        item["id_entrada"] for item in resultados["feedback_resultados"]
    } == {"benchmark_02", "benchmark_04"}

    sesion = json.loads((tmp_path / "editorial_benchmark_02" / "sesion.json").read_text(encoding="utf-8"))
    assert len(sesion["versiones"]) == 2
    assert sesion["evidencia_ejecucion"]["feedback_ciclos"][0]["version_nueva"] == 2


def test_benchmark_falla_si_el_adapter_devuelve_metatexto_visible(tmp_path):
    class FakeAdapter(ModelAdapter):
        def generar_texto(self, prompt: str, system_instruction: str | None = None) -> str:
            return "Aquí tienes un borrador del post:\n\nTexto aparentemente útil."

    with pytest.raises(ValueError, match="metatexto editorial"):
        ejecutar_benchmark_local(
            fixtures_path=BENCHMARK_DIR / "fixtures.json",
            profiles_dir=BENCHMARK_DIR / "profiles",
            output_dir=tmp_path,
            adapter=FakeAdapter(),
        )

    assert not list(tmp_path.glob("localdraft_*"))
