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
    assert "--texto" in result.stdout


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
            "--tipo-aprobacion",
            "reforzada",
            "--motivo-revision-reforzada",
            "La evaluación editorial automática requiere revisión humana explícita.",
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
            "--tipo-aprobacion",
            "reforzada",
            "--motivo-revision-reforzada",
            "La evaluación editorial automática requiere revisión humana explícita.",
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


def test_cli_input_inseguro_no_invoca_adapter_y_sanea_error(tmp_path, monkeypatch, capsys):
    from linkedin_content_system.cli import flujo_textual as cli_module

    entrada_insegura = _entrada_json()
    entrada_insegura["texto_base"] = "Escribeme a contacto@dominio.com para compartir el caso real."
    input_path = tmp_path / "entrada_insegura.json"
    input_path.write_text(json.dumps(entrada_insegura, ensure_ascii=False), encoding="utf-8")

    class _SpyAdapter:
        def __init__(self):
            self.invocado = False

        def generar_texto(self, prompt, system_instruction=None):
            self.invocado = True
            return "No deberia ejecutarse"

    adapter = _SpyAdapter()

    def _fake_construir_model_adapter():
        return adapter

    monkeypatch.setattr(cli_module, "construir_model_adapter", _fake_construir_model_adapter)

    exit_code = cli_module.main(
        [
            "--input-json",
            str(input_path),
            "--output-dir",
            str(tmp_path),
            "--estado-aprobacion",
            "aprobado",
            "--revisor",
            "QA Local",
            "--fecha-aprobacion",
            "2026-07-10T12:00:00Z",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert adapter.invocado is False
    assert "ERROR:" in captured.err
    assert "correo electrónico" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""
    assert not (tmp_path / "localdraft_in_cli_001").exists()
    assert list(tmp_path.iterdir()) == [input_path]


def test_cli_texto_genera_borrador_pendiente_sin_aprobacion(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkedin_content_system.cli.flujo_textual",
            "--texto",
            "Automatizar lo repetitivo deja mas tiempo para aplicar criterio humano.",
            "--id-entrada",
            "in_cli_texto_001",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    assert result.returncode == 0
    assert "pendiente de revisión" in result.stdout.lower()
    assert "intención:" in result.stdout.lower()
    assert "perfil:" in result.stdout.lower()
    assert "validación técnica:" in result.stdout.lower()
    assert "validación estructural:" in result.stdout.lower()
    assert "evaluación editorial automática:" in result.stdout.lower()
    assert "decisión humana:" in result.stdout.lower()
    assert (tmp_path / "editorial_in_cli_texto_001" / "versiones" / "v001.md").exists()
    assert not (tmp_path / "localdraft_in_cli_texto_001").exists()


def test_cli_persiste_evidencia_operativa_saneada_en_sesion(tmp_path, monkeypatch):
    from linkedin_content_system.cli import flujo_textual as cli_module

    input_path = tmp_path / "entrada.json"
    input_path.write_text(json.dumps(_entrada_json(), ensure_ascii=False), encoding="utf-8")
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    (profile_dir / "perfil_cli.json").write_text(
        json.dumps(
            {
                "id_perfil": "perfil_cli",
                "voz_marca": {
                    "tono_base": {"descripcion": "Claro y práctico"},
                    "tono_prohibido": {"descripcion": "Promocional"},
                },
            }
        ),
        encoding="utf-8",
    )

    class AdapterConMetadatos:
        proveedor = "ollama"
        modelo = "ollama_chat/modelo-sintetico"
        timeout_seconds = 120.0
        max_tokens = 180

        def generar_texto(self, prompt, system_instruction=None):
            return "Automatizar tareas repetitivas libera tiempo para aplicar criterio humano. ¿Qué decisión conservarías?"

    monkeypatch.setenv("LINKEDIN_CONTENT_AI_ADAPTER", "litellm")
    monkeypatch.setenv("LINKEDIN_CONTENT_PROFILE_DIR", str(profile_dir))
    monkeypatch.setattr(cli_module, "construir_model_adapter", AdapterConMetadatos)

    assert cli_module.main(["--input-json", str(input_path), "--output-dir", str(tmp_path)]) == 0

    sesion = json.loads((tmp_path / "editorial_in_cli_001" / "sesion.json").read_text(encoding="utf-8"))
    evidencia = sesion["evidencia_ejecucion"]
    assert evidencia["proveedor"] == "ollama"
    assert evidencia["modelo"] == "ollama_chat/modelo-sintetico"
    assert evidencia["duracion_ms"] >= 0
    assert evidencia["estado_tecnico"] == "PASS"
    assert evidencia["estado_sesion"] == "pendiente_revision"
    assert evidencia["estado_revision_automatica"] == "WARN"
    assert evidencia["decision_humana"] == "PENDIENTE"
    assert evidencia["sin_publicacion"] is True
    assert evidencia["sin_localdraft"] is True


def test_cli_ciclo_completo_ajusta_aprueba_y_prepara(tmp_path):
    comandos = [
        [
            "--texto",
            "Un borrador revisable ayuda a conservar la intención antes de publicar.",
            "--id-entrada",
            "in_cli_ciclo_001",
            "--output-dir",
            str(tmp_path),
        ],
        [
            "--accion",
            "ajustar",
            "--id-entrada",
            "in_cli_ciclo_001",
            "--feedback",
            "Haz más directa la apertura.",
            "--output-dir",
            str(tmp_path),
        ],
        [
            "--accion",
            "aprobar",
            "--id-entrada",
            "in_cli_ciclo_001",
            "--version",
            "2",
            "--revisor",
            "Revisión Sintética",
            "--tipo-aprobacion",
            "reforzada",
            "--motivo-revision-reforzada",
            "La intención inicial es tentativa y requiere revisión explícita.",
            "--output-dir",
            str(tmp_path),
        ],
        [
            "--accion",
            "preparar",
            "--id-entrada",
            "in_cli_ciclo_001",
            "--output-dir",
            str(tmp_path),
        ],
    ]

    for argumentos in comandos:
        result = subprocess.run(
            [sys.executable, "-m", "linkedin_content_system.cli.flujo_textual", *argumentos],
            capture_output=True,
            text=True,
            env=_cli_env(),
        )
        assert result.returncode == 0, result.stderr

    assert (tmp_path / "editorial_in_cli_ciclo_001" / "versiones" / "v002.md").exists()
    assert (tmp_path / "localdraft_in_cli_ciclo_001" / "post.md").exists()


def test_cli_no_anuncia_aprobacion_simple_si_la_version_requiere_refuerzo(tmp_path):
    from linkedin_content_system.cli import flujo_textual as cli_module

    exit_code = cli_module.main(
        [
            "--texto",
            "Una nota breve para activar el ciclo editorial.",
            "--id-entrada",
            "in_cli_warn_001",
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert exit_code == 0

    exit_code = cli_module.main(
        [
            "--accion",
            "aprobar",
            "--id-entrada",
            "in_cli_warn_001",
            "--version",
            "1",
            "--revisor",
            "Revisor Sintetico",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 1
    assert not (tmp_path / "localdraft_in_cli_warn_001").exists()


def test_cli_documento_y_borrador_generan_sesion_con_fuente_distinta(tmp_path):
    documento = tmp_path / "fuente.md"
    documento.write_text("Un documento sintético conserva los hechos autorizados.", encoding="utf-8")
    for argumento, contenido, entrada_id in (
        ("--documento", str(documento), "cli_documento"),
        ("--borrador", "Un borrador sintético debe quedar pendiente.", "cli_borrador"),
    ):
        result = subprocess.run(
            [
                sys.executable, "-m", "linkedin_content_system.cli.flujo_textual",
                argumento, contenido, "--id-entrada", entrada_id, "--output-dir", str(tmp_path), "--vista", "cliente",
            ], capture_output=True, text=True, env=_cli_env(),
        )
        assert result.returncode == 0
        assert "Administración:" not in result.stdout
        assert (tmp_path / f"editorial_{entrada_id}" / "sesion.json").exists()


def test_cli_vista_cliente_no_expone_evidencia_tecnica(tmp_path):
    result = subprocess.run(
        [
            sys.executable, "-m", "linkedin_content_system.cli.flujo_textual",
            "--texto", "Una vista cliente presenta solo la candidata revisable.",
            "--id-entrada", "cli_cliente", "--output-dir", str(tmp_path), "--vista", "cliente",
        ], capture_output=True, text=True, env=_cli_env(),
    )

    assert result.returncode == 0
    assert "Administración:" not in result.stdout
    assert "Validación técnica:" not in result.stdout
    assert "Evidencia:" not in result.stdout
