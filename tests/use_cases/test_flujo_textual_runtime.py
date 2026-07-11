import json

import pytest

from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
    LinkedInTextChannelStrategy,
    PerfilNarrativoRuntime,
)


def test_filesystem_profile_resolver_carga_perfil_desde_profile_dir(tmp_path):
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    profile_path = profile_dir / "perfil_valido.json"
    profile_path.write_text(
        json.dumps(
            {
                "id_perfil": "perfil_valido",
                "voz_marca": {
                    "tono_base": {"descripcion": "Claro y técnico"},
                    "tono_prohibido": {"descripcion": "Humo comercial"},
                },
                "lenguaje": {
                    "palabras_frecuentes": ["flujo"],
                    "expresiones_propias": ["paso revisable"],
                    "frases_prohibidas": ["hola red"],
                },
                "cta": {"cta_preferidos": ["pregunta final concreta"]},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    resolver = FilesystemNarrativeProfileResolver(profile_dir=profile_dir)
    perfil = resolver.resolve("perfil_valido")

    assert perfil.id_perfil == "perfil_valido"
    assert perfil.tono_base == "Claro y técnico"
    assert perfil.tono_prohibido == "Humo comercial"
    assert perfil.palabras_clave == ("flujo", "paso revisable")
    assert perfil.frases_prohibidas == ("hola red",)
    assert perfil.cta_preferidos == ("pregunta final concreta",)


@pytest.mark.parametrize(
    "id_perfil",
    [
        "../escape",
        "..\\escape",
        "/absoluto",
        "C:/Users/test",
        "perfil/con-separador",
        "perfil\\con-separador",
        "perfil con espacios",
        "perfil.json",
        "perfil:mal",
    ],
)
def test_filesystem_profile_resolver_rechaza_ids_peligrosos(tmp_path, id_perfil):
    resolver = FilesystemNarrativeProfileResolver(profile_dir=tmp_path / "profiles")

    with pytest.raises(ValueError, match="id_perfil inválido"):
        resolver.resolve(id_perfil)


def test_filesystem_profile_resolver_fallback_si_no_existe_el_perfil(tmp_path):
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    resolver = FilesystemNarrativeProfileResolver(profile_dir=profile_dir)

    perfil = resolver.resolve("perfil_inexistente")

    assert perfil.id_perfil == "perfil_inexistente"
    assert "Profesional, claro y directo" in perfil.tono_base


def test_filesystem_profile_resolver_rechaza_id_vacio(tmp_path):
    resolver = FilesystemNarrativeProfileResolver(profile_dir=tmp_path / "profiles")

    with pytest.raises(ValueError, match="id_perfil no puede estar vacío"):
        resolver.resolve("   ")


def test_linkedin_strategy_exige_solo_post_candidato_sin_metatexto():
    from linkedin_content_system.contracts import (
        EntradaContenido,
        EstadoIntencionEditorial,
        EstadoPrivacidad,
        IntencionEditorial,
        PerfilNarrativoReferencia,
        TipoEntrada,
    )

    entrada = EntradaContenido(
        id_entrada="in_prompt_001",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base="Una idea sencilla requiere criterio humano.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            idea_central="El criterio humano sigue siendo necesario.",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_prompt"),
        canales_destino=["linkedin"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )

    solicitud = LinkedInTextChannelStrategy().build_request(
        entrada,
        "El criterio humano sigue siendo necesario.",
        "Intención identificada como compartir_aprendizaje.",
        PerfilNarrativoRuntime("perfil_prompt", "Claro", "Grandilocuente"),
    )

    assert "Devuelve exclusivamente el post candidato" in solicitud.prompt
    assert "No incluyas análisis" in solicitud.prompt
