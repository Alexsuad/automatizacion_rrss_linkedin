import json

import pytest

from linkedin_content_system.ai import MockModelAdapter
from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    AprobacionHumana,
    EntradaContenido,
    EstadoAprobacion,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoEntrada,
)
from linkedin_content_system.use_cases import ejecutar_flujo_textual
from linkedin_content_system.use_cases.flujo_textual_runtime import (
    PerfilNarrativoRuntime,
    SolicitudGeneracionTextual,
)


@pytest.fixture
def entrada_valida():
    return EntradaContenido(
        id_entrada="in_texto_001",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Aprendi que una automatizacion util empieza con un flujo simple y revisable.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="equipos pequenos B2B",
            idea_central="Empezar simple mejora la utilidad del sistema",
            cta_intencionado="Que opinas",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_fundador"),
        canales_destino=["linkedin", "x"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"fecha_objetivo_sugerida": "2026-07-15T09:00:00Z"},
    )


@pytest.fixture
def aprobacion_aprobada():
    return AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex Revisor",
        fecha_aprobacion="2026-07-08T12:00:00Z",
    )


def test_ejecutar_flujo_textual_genera_localdraft(tmp_path, entrada_valida, aprobacion_aprobada):
    class SafeAdapter(ModelAdapter):
        def generar_texto(self, prompt: str, system_instruction: str = None) -> str:
            return (
                "Automatizacion segura para equipos pequenos B2B.\n"
                "Empezar simple mejora la utilidad del sistema.\n"
                "Que opinas?"
            )

    manifest = ejecutar_flujo_textual(
        entrada=entrada_valida,
        adapter=SafeAdapter(),
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
    )

    draft_dir = tmp_path / "localdraft_in_texto_001"
    post_file = draft_dir / "post.md"
    manifest_file = draft_dir / "manifest.json"

    assert draft_dir.exists()
    assert post_file.exists()
    assert manifest_file.exists()
    assert "Que opinas?" in post_file.read_text(encoding="utf-8")
    assert manifest.id_entrada == entrada_valida.id_entrada


def test_ejecutar_flujo_textual_funciona_con_mock_adapter(tmp_path, entrada_valida, aprobacion_aprobada):
    manifest = ejecutar_flujo_textual(
        entrada=entrada_valida,
        adapter=MockModelAdapter(),
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
    )

    post_file = tmp_path / "localdraft_in_texto_001" / "post.md"
    salida_file = tmp_path / "localdraft_in_texto_001" / "salida_v1.json"
    contenido = post_file.read_text(encoding="utf-8")
    salida_persistida = json.loads(salida_file.read_text(encoding="utf-8"))

    assert manifest.id_entrada == "in_texto_001"
    assert "[BORRADOR SIMULADO DE POST]" in contenido
    assert salida_persistida["estado_publicabilidad"] == "no_publicable"


def test_ejecutar_flujo_textual_rechaza_entrada_no_textual(tmp_path, entrada_valida, aprobacion_aprobada):
    entrada_audio = entrada_valida.model_copy(update={"tipo_entrada": TipoEntrada.AUDIO})

    with pytest.raises(ValueError, match="solo admite entradas de texto manual"):
        ejecutar_flujo_textual(
            entrada=entrada_audio,
            adapter=MockModelAdapter(),
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path),
        )


def test_ejecutar_flujo_textual_rechaza_si_no_esta_linkedin(tmp_path, entrada_valida, aprobacion_aprobada):
    entrada_sin_linkedin = entrada_valida.model_copy(update={"canales_destino": ["x"]})

    with pytest.raises(ValueError, match="linkedin"):
        ejecutar_flujo_textual(
            entrada=entrada_sin_linkedin,
            adapter=MockModelAdapter(),
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path),
        )


def test_ejecutar_flujo_textual_no_crea_artefactos_sin_aprobacion(tmp_path, entrada_valida):
    aprobacion_pendiente = AprobacionHumana(estado=EstadoAprobacion.PENDIENTE)

    with pytest.raises(ValueError, match="Publicación denegada"):
        ejecutar_flujo_textual(
            entrada=entrada_valida,
            adapter=MockModelAdapter(),
            aprobacion=aprobacion_pendiente,
            base_dir=str(tmp_path),
        )

    assert not (tmp_path / "localdraft_in_texto_001").exists()


def test_ejecutar_flujo_textual_compone_prompt_con_senales_derivadas(tmp_path, entrada_valida, aprobacion_aprobada):
    class SpyAdapter(ModelAdapter):
        def __init__(self):
            self.prompt_recibido = None
            self.system_instruction_recibida = None

        def generar_texto(self, prompt: str, system_instruction: str = None) -> str:
            self.prompt_recibido = prompt
            self.system_instruction_recibida = system_instruction
            return (
                "Empezar simple mejora la utilidad del sistema para equipos pequenos B2B.\n"
                "Que opinas?"
            )

    adapter = SpyAdapter()

    ejecutar_flujo_textual(
        entrada=entrada_valida,
        adapter=adapter,
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
    )

    assert adapter.prompt_recibido is not None
    assert adapter.system_instruction_recibida is not None
    assert entrada_valida.texto_base in adapter.prompt_recibido
    assert entrada_valida.intencion_editorial.idea_central in adapter.prompt_recibido
    assert "Intención identificada como compartir_aprendizaje" in adapter.prompt_recibido
    assert "Tono base:" in adapter.system_instruction_recibida


def test_ejecutar_flujo_textual_bloquea_entrada_insegura_antes_del_adapter(
    tmp_path,
    entrada_valida,
    aprobacion_aprobada,
):
    class SpyAdapter(ModelAdapter):
        def __init__(self):
            self.invocado = False

        def generar_texto(self, prompt: str, system_instruction: str = None) -> str:
            self.invocado = True
            return "No deberia generarse"

    adapter = SpyAdapter()
    entrada_insegura = entrada_valida.model_copy(
        update={"texto_base": "Escribeme a correo@dominio.com para contarte el caso"}
    )

    with pytest.raises(ValueError, match="correo electrónico"):
        ejecutar_flujo_textual(
            entrada=entrada_insegura,
            adapter=adapter,
            aprobacion=aprobacion_aprobada,
            base_dir=str(tmp_path),
        )

    assert adapter.invocado is False
    assert not (tmp_path / "localdraft_in_texto_001").exists()


def test_ejecutar_flujo_textual_admite_strategy_inyectado_para_otro_canal(
    tmp_path,
    entrada_valida,
    aprobacion_aprobada,
):
    class CanalXStrategy:
        canal_destino = "x"

        def supports(self, entrada):
            return "x" in entrada.canales_destino

        def build_request(self, entrada, idea_central, resumen_intencion, perfil):
            return SolicitudGeneracionTextual(
                canal_destino="x",
                prompt=f"Texto base original: {entrada.texto_base}\nIdea central: {idea_central}",
                system_instruction=f"Tono base: {perfil.tono_base}",
            )

    class ResolverFalso:
        def resolve(self, id_perfil: str) -> PerfilNarrativoRuntime:
            return PerfilNarrativoRuntime(
                id_perfil=id_perfil,
                tono_base="Directo y tecnico",
                tono_prohibido="Promocional hueco",
            )

    class SafeAdapter(ModelAdapter):
        def generar_texto(self, prompt: str, system_instruction: str = None) -> str:
            return "Empezar simple mejora la utilidad del sistema en otro canal.\nQue opinas?"

    entrada_x = entrada_valida.model_copy(update={"canales_destino": ["x"]})

    manifest = ejecutar_flujo_textual(
        entrada=entrada_x,
        adapter=SafeAdapter(),
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
        profile_resolver=ResolverFalso(),
        channel_strategy=CanalXStrategy(),
    )

    assert manifest.id_entrada == "in_texto_001"
    assert (tmp_path / "localdraft_in_texto_001" / "post.md").exists()
