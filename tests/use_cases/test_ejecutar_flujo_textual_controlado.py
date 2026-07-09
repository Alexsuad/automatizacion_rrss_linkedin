import pytest

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
from linkedin_content_system.ai import ControlledModelAdapter
from linkedin_content_system.use_cases import ejecutar_flujo_textual


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


def test_ejecutar_flujo_textual_con_adapter_controlado_genera_localdraft_publicable(
    tmp_path,
    entrada_valida,
    aprobacion_aprobada,
):
    manifest = ejecutar_flujo_textual(
        entrada=entrada_valida,
        adapter=ControlledModelAdapter(),
        aprobacion=aprobacion_aprobada,
        base_dir=str(tmp_path),
    )

    draft_dir = tmp_path / "localdraft_in_texto_001"
    post_file = draft_dir / "post.md"
    salida_file = draft_dir / "salida_v1.json"

    assert draft_dir.exists()
    assert post_file.exists()
    assert salida_file.exists()
    assert manifest.id_entrada == "in_texto_001"
    assert "Que opinas?" in post_file.read_text(encoding="utf-8")
