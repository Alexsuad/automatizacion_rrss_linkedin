import pytest
from unittest.mock import patch
from linkedin_content_system.contracts.contexto_trabajo import ContextoTrabajo
from linkedin_content_system.use_cases.validar_compatibilidad_contexto import validar_compatibilidad_contexto


@pytest.fixture
def contexto_valido():
    return ContextoTrabajo(
        contexto_id="ctx_123",
        cliente_id="cliente_abc",
        superficie="linkedin_personal",
        campaña="campaña_test",
        fuentes_autorizadas=["audio_original", "transcripcion_v1"],
        datos_reales_permitidos=False,
        estado="activo",
        notas_seguridad=[]
    )


def test_s7_caso_compatible_devuelve_pass(contexto_valido):
    # S7 — Caso compatible devuelve PASS.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=["audio_original"],
        datos_reales_detectados=False
    )
    assert res.compatible is True
    assert res.estado == "PASS"
    assert len(res.bloqueos) == 0


def test_s8_rechaza_contexto_none():
    # S8 — Rechaza contexto None.
    with pytest.raises(ValueError, match="El contexto no puede ser None"):
        validar_compatibilidad_contexto(
            contexto=None,  # type: ignore
            cliente_id_operacion="cliente_abc",
            superficie_operacion="linkedin_personal"
        )


def test_s9_rechaza_cliente_id_operacion_vacio(contexto_valido):
    # S9 — Rechaza cliente_id_operacion vacío.
    with pytest.raises(ValueError, match="cliente_id_operacion no puede estar vacío"):
        validar_compatibilidad_contexto(
            contexto=contexto_valido,
            cliente_id_operacion="",
            superficie_operacion="linkedin_personal"
        )
    with pytest.raises(ValueError, match="cliente_id_operacion no puede estar vacío"):
        validar_compatibilidad_contexto(
            contexto=contexto_valido,
            cliente_id_operacion="   ",
            superficie_operacion="linkedin_personal"
        )


def test_s10_rechaza_superficie_operacion_vacia(contexto_valido):
    # S10 — Rechaza superficie_operacion vacía.
    with pytest.raises(ValueError, match="superficie_operacion no puede estar vacía"):
        validar_compatibilidad_contexto(
            contexto=contexto_valido,
            cliente_id_operacion="cliente_abc",
            superficie_operacion=""
        )
    with pytest.raises(ValueError, match="superficie_operacion no puede estar vacía"):
        validar_compatibilidad_contexto(
            contexto=contexto_valido,
            cliente_id_operacion="cliente_abc",
            superficie_operacion="   "
        )


def test_s11_bloquea_cliente_distinto(contexto_valido):
    # S11 — Bloquea cliente distinto.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_distinto",
        superficie_operacion="linkedin_personal"
    )
    assert res.compatible is False
    assert res.estado == "BLOQUEADO"
    assert any("cliente_id_operacion" in b for b in res.bloqueos)


def test_s12_bloquea_superficie_distinta(contexto_valido):
    # S12 — Bloquea superficie distinta.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_empresa"
    )
    assert res.compatible is False
    assert res.estado == "BLOQUEADO"
    assert any("superficie_operacion" in b for b in res.bloqueos)


def test_s13_bloquea_datos_reales_si_el_contexto_no_los_permite(contexto_valido):
    # S13 — Bloquea datos reales si el contexto no los permite.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        datos_reales_detectados=True
    )
    assert res.compatible is False
    assert res.estado == "BLOQUEADO"
    assert any("datos reales" in b for b in res.bloqueos)


def test_s14_bloquea_fuente_no_autorizada(contexto_valido):
    # S14 — Bloquea fuente no autorizada.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=["fuente_no_permitida"]
    )
    assert res.compatible is False
    assert res.estado == "BLOQUEADO"
    assert any("fuente_no_permitida" in b for b in res.bloqueos)


def test_s15_fuentes_usadas_none_se_convierte_en_lista_vacia(contexto_valido):
    # S15 — fuentes_usadas None se convierte en lista vacía.
    res = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=None
    )
    assert res.compatible is True
    assert res.estado == "PASS"


def test_s16_no_escribe_archivos(contexto_valido):
    # S16 — No escribe archivos.
    with patch("builtins.open") as mock_open:
        validar_compatibilidad_contexto(
            contexto=contexto_valido,
            cliente_id_operacion="cliente_abc",
            superficie_operacion="linkedin_personal"
        )
        mock_open.assert_not_called()


def test_s17_es_determinista(contexto_valido):
    # S17 — Es determinista.
    res1 = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=["audio_original"],
        datos_reales_detectados=False
    )
    res2 = validar_compatibilidad_contexto(
        contexto=contexto_valido,
        cliente_id_operacion="cliente_abc",
        superficie_operacion="linkedin_personal",
        fuentes_usadas=["audio_original"],
        datos_reales_detectados=False
    )
    assert res1.compatible == res2.compatible
    assert res1.estado == res2.estado
    assert res1.motivo == res2.motivo
    assert res1.bloqueos == res2.bloqueos
