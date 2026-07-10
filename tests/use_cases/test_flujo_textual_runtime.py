import json

import pytest

from linkedin_content_system.use_cases.flujo_textual_runtime import (
    FilesystemNarrativeProfileResolver,
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
