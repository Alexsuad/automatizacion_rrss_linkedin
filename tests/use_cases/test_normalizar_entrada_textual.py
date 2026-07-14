import hashlib

import pytest

from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoEntrada,
)
from linkedin_content_system.use_cases.normalizar_entrada_textual import (
    cargar_documento_textual,
    normalizar_entrada_textual,
)


def _entrada(tipo=TipoEntrada.TEXTO_MANUAL, texto="Un hecho verificable mejora una candidata revisable."):
    return EntradaContenido(
        id_entrada="fuente_001",
        tipo_entrada=tipo,
        texto_base=texto,
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            idea_central="Los hechos autorizados deben guiar el post.",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_prueba"),
        canales_destino=["linkedin"],
        metadatos_origen={
            "referencia_fuente": "fuente_sintetica_001",
            "hechos_autorizados": ["El equipo revisa cada candidata antes de aprobarla."],
            "experiencias_autorizadas": ["He observado revisiones humanas en el flujo."],
            "no_inferir": ["No atribuir resultados de negocio."],
        },
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


@pytest.mark.parametrize(
    "tipo",
    [
        TipoEntrada.TEXTO_MANUAL,
        TipoEntrada.DOCUMENTO_BASE,
        TipoEntrada.BORRADOR_EXISTENTE,
        TipoEntrada.AUDIO,
        TipoEntrada.TRANSCRIPCION,
    ],
)
def test_las_tres_entradas_textuales_comparten_normalizacion(tipo):
    entrada = _entrada(tipo)

    fuente = normalizar_entrada_textual(entrada)

    assert fuente.tipo_entrada == tipo
    assert fuente.referencia_fuente == "fuente_sintetica_001"
    assert fuente.hechos_explicitos == ["El equipo revisa cada candidata antes de aprobarla."]
    assert fuente.experiencias_autorizadas == ["He observado revisiones humanas en el flujo."]
    assert fuente.hash_contenido == hashlib.sha256(entrada.texto_base.encode("utf-8")).hexdigest()


def test_normalizacion_audio_conserva_segmentos_con_timestamps():
    entrada = _entrada(TipoEntrada.AUDIO, "La revision humana precede a cualquier salida.")
    entrada.metadatos_origen["transcripcion_segmentos"] = [
        {
            "indice": 1,
            "inicio_segundos": 0.0,
            "fin_segundos": 0.5,
            "texto": "La revision humana precede a cualquier salida.",
        }
    ]
    entrada.metadatos_origen["audio_sha256"] = "sha_audio"

    fuente = normalizar_entrada_textual(entrada)

    assert fuente.fragmentos_evidencia[0]["inicio_segundos"] == 0.0
    assert fuente.fragmentos_evidencia[0]["fin_segundos"] == 0.5
    assert fuente.fragmentos_evidencia[0]["audio_sha256"] == "sha_audio"


def test_carga_documento_txt_y_md_de_forma_local(tmp_path):
    documento = tmp_path / "fuente.md"
    documento.write_text("Contenido sintético para revisión.", encoding="utf-8")

    assert cargar_documento_textual(documento) == "Contenido sintético para revisión."


@pytest.mark.parametrize("nombre,contenido,mensaje", [
    ("fuente.pdf", "contenido", "extensión"),
    ("vacio.txt", "", "vacío"),
    ("privado.txt", "Escribe a persona@ejemplo.test", "correo electrónico"),
])
def test_documento_inseguro_o_invalido_se_rechaza(tmp_path, nombre, contenido, mensaje):
    documento = tmp_path / nombre
    documento.write_text(contenido, encoding="utf-8")

    with pytest.raises(ValueError, match=mensaje):
        cargar_documento_textual(documento)


def test_referencia_de_ruta_absoluta_no_se_persiste_como_fuente():
    entrada = _entrada()
    entrada.metadatos_origen["referencia_fuente"] = "/ruta/local/privada.txt"

    with pytest.raises(ValueError, match="no una ruta local"):
        normalizar_entrada_textual(entrada)
