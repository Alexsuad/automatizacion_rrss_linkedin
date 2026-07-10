import json
import os
import subprocess
import sys

from linkedin_content_system.ai import LiteLLMProviderError
from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoEntrada,
)


def _entrada_json():
    entrada = EntradaContenido(
        id_entrada="in_cli_001",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Aprendi que un flujo pequeno y local acelera la validacion del producto.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="fundadores B2B",
            idea_central="El flujo textual local sirve para validar utilidad real",
            cta_intencionado="Que opinas",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_cli"),
        canales_destino=["linkedin"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )
    return entrada.model_dump(mode="json")


def _entrada_json_realista():
    entrada = EntradaContenido(
        id_entrada="in_cli_005",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Hoy vi que muchos equipos quieren usar IA para contenido, pero primero necesitan un flujo simple, revisable y seguro antes de automatizar mas.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="fundadores y equipos pequenos B2B",
            idea_central="La utilidad real empieza con un flujo simple y seguro",
            cta_intencionado="¿Te pasa lo mismo?",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_cli_realista"),
        canales_destino=["linkedin"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )
    return entrada.model_dump(mode="json")


def _cli_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath("src")
    env["LINKEDIN_CONTENT_AI_ADAPTER"] = "controlled"
    return env


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "linkedin_content_system.cli.flujo_textual", "--help"],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode == 0
    assert "input-json" in result.stdout


def test_cli_aprobado_genera_localdraft(tmp_path):
    input_path = tmp_path / "entrada.json"
    input_path.write_text(json.dumps(_entrada_json(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.flujo_textual",
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "aprobado",
            "--revisor",
            "Alex Revisor",
            "--fecha-aprobacion",
            "2026-07-08T12:30:00Z",
        ],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode == 0
    assert "in_cli_001" in result.stdout
    assert (tmp_path / "localdraft_in_cli_001").exists()


def test_cli_pendiente_falla_y_no_escribe_localdraft(tmp_path):
    input_path = tmp_path / "entrada.json"
    input_path.write_text(json.dumps(_entrada_json(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.flujo_textual",
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "pendiente",
        ],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode != 0
    assert not (tmp_path / "localdraft_in_cli_001").exists()
    assert "error" in result.stderr.lower()


def test_cli_json_invalido_falla(tmp_path):
    input_path = tmp_path / "entrada_invalida.json"
    input_path.write_text("{no_es_json}", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.flujo_textual",
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "aprobado",
            "--revisor",
            "Alex Revisor",
            "--fecha-aprobacion",
            "2026-07-08T12:30:00Z",
        ],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode != 0
    assert "error" in result.stderr.lower()


def test_cli_aprobado_con_entrada_realista_genera_localdraft_util(tmp_path):
    input_path = tmp_path / "entrada_realista.json"
    input_path.write_text(json.dumps(_entrada_json_realista(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.flujo_textual",
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "aprobado",
            "--revisor",
            "QA Local",
            "--fecha-aprobacion",
            "2026-07-10T10:00:00Z",
        ],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode == 0
    assert (tmp_path / "localdraft_in_cli_005").exists()
    contenido = (tmp_path / "localdraft_in_cli_005" / "post.md").read_text(encoding="utf-8")
    assert "[BORRADOR SIMULADO DE POST]" not in contenido
    assert "La utilidad real empieza con un flujo simple y seguro" in contenido
    assert "¿Te pasa lo mismo?" in contenido


def test_cli_sanea_litellm_provider_error_sin_traceback_ni_artefactos(tmp_path, monkeypatch, capsys):
    from linkedin_content_system.cli import flujo_textual as cli_module

    input_path = tmp_path / "entrada_error.json"
    input_path.write_text(json.dumps(_entrada_json(), ensure_ascii=False), encoding="utf-8")

    class _AdapterQueFalla:
        def generar_texto(self, prompt, system_instruction=None):
            raise AssertionError("No deberia invocarse directamente en este test")

    def _fake_construir_model_adapter():
        return _AdapterQueFalla()

    def _fake_ejecutar_flujo_textual(**kwargs):
        raise LiteLLMProviderError(
            "No se pudo generar texto con el proveedor IA configurado."
        ) from RuntimeError("provider-secret-detail")

    monkeypatch.setattr(cli_module, "construir_model_adapter", _fake_construir_model_adapter)
    monkeypatch.setattr(cli_module, "ejecutar_flujo_textual", _fake_ejecutar_flujo_textual)

    exit_code = cli_module.main(
        [
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "aprobado",
            "--revisor",
            "Smoke Local",
            "--fecha-aprobacion",
            "2026-07-10T12:00:00Z",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ERROR: No se pudo generar texto con el proveedor IA configurado." in captured.err
    assert "provider-secret-detail" not in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""
    assert not (tmp_path / "localdraft_in_cli_001").exists()
    assert list(tmp_path.iterdir()) == [input_path]
