import json
import subprocess
import sys


def test_smoke_incremento2_audio_a_external_dry_run(tmp_path):
    env = {
        **__import__("os").environ,
        "PYTHONPATH": __import__("os").path.abspath("src"),
        "LINKEDIN_CONTENT_AI_ADAPTER": "controlled",
    }

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.smoke_incremento2",
            "--audio",
            "tests/fixtures/audio/smoke_incremento2.wav",
            "--metadata-json",
            "tests/fixtures/audio/smoke_incremento2.metadata.json",
            "--transcriber",
            "fake",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    resumen = json.loads((tmp_path / "resumen_final.json").read_text(encoding="utf-8"))
    payload = json.loads((tmp_path / "payload_external_dry_run.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    sanitizada = json.loads((tmp_path / "transcripcion_sanitizada.json").read_text(encoding="utf-8"))

    assert resumen["smoke"] == "incremento_2"
    assert resumen["publicado"] is False
    assert resumen["transcripcion_modo"] == "fake"
    assert payload["no_publicado_realmente"] is True
    assert manifest["id_entrada"] == "smoke_incremento2"
    assert sanitizada["texto_sanitizado"]
    assert (tmp_path / "editorial_smoke_incremento2" / "versiones" / "v001.md").exists()
    assert (tmp_path / "editorial_smoke_incremento2" / "versiones" / "v002.md").exists()


def test_smoke_incremento2_real_pendiente_sanea_error_si_falta_modelo(tmp_path):
    env = {
        **__import__("os").environ,
        "PYTHONPATH": __import__("os").path.abspath("src"),
    }

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.smoke_incremento2",
            "--audio",
            "tests/fixtures/audio/smoke_incremento2.wav",
            "--metadata-json",
            "tests/fixtures/audio/smoke_incremento2.metadata.json",
            "--transcriber",
            "whisper_cpp",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "ERROR:" in result.stderr
    assert "MODEL_PATH" in result.stderr
    assert "Traceback" not in result.stderr
