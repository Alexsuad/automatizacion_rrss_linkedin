import json

import pytest

from linkedin_content_system.contracts import (
    EstadoCompletitudTranscripcion,
    ModoTranscripcion,
    ResultadoTranscripcion,
    SegmentoTranscripcion,
    TipoEntrada,
)
from linkedin_content_system.transcription import (
    FakeFixtureTranscriptionAdapter,
    TranscriptionConfigurationError,
    TranscriptionDependencyError,
    WhisperCppTranscriptionAdapter,
)
from linkedin_content_system.transcription.ports import TranscriptionInputError, TranscriptionResponseError
from linkedin_content_system.use_cases.preparar_entrada_audio import (
    construir_entrada_desde_audio,
    sanitizar_transcripcion,
    validar_audio_local,
)


@pytest.fixture
def audio_fixture_path():
    return "tests/fixtures/audio/smoke_incremento2.wav"


@pytest.fixture
def audio_ogg_fixture_path():
    return "tests/fixtures/audio/smoke_incremento2.ogg"


def test_validar_audio_local_acepta_wav_valido(audio_fixture_path):
    resultado = validar_audio_local(audio_fixture_path, allowed_extensions={".wav"})

    assert resultado.audio.extension == ".wav"
    assert resultado.audio.sha256_audio
    assert resultado.audio.tamano_bytes > 0
    assert resultado.audio.duracion_segundos is None or resultado.audio.duracion_segundos > 0


def test_validar_audio_local_acepta_formato_adicional_soportado(audio_ogg_fixture_path):
    resultado = validar_audio_local(audio_ogg_fixture_path, allowed_extensions={".ogg"})

    assert resultado.audio.extension == ".ogg"
    assert resultado.audio.sha256_audio


@pytest.mark.parametrize(
    "nombre,contenido,mensaje",
    [
        ("invalido.txt", b"no-audio", "no está soportado"),
        ("vacio.wav", b"", "no puede estar vacío"),
    ],
)
def test_validar_audio_local_rechaza_archivos_invalidos(tmp_path, nombre, contenido, mensaje):
    audio = tmp_path / nombre
    audio.write_bytes(contenido)

    with pytest.raises(TranscriptionInputError, match=mensaje):
        validar_audio_local(audio, allowed_extensions={".wav", ".ogg"})


def test_validar_audio_local_rechaza_inexistente():
    with pytest.raises(TranscriptionInputError, match="no existe"):
        validar_audio_local("tests/fixtures/audio/no_existe.wav", allowed_extensions={".wav"})


def test_fake_transcriber_carga_sidecar_y_segmentos(audio_fixture_path):
    validacion = validar_audio_local(audio_fixture_path, allowed_extensions={".wav", ".ogg", ".mp3"})
    resultado = FakeFixtureTranscriptionAdapter().transcribir(
        __import__("pathlib").Path(audio_fixture_path),
        audio_sha256=validacion.audio.sha256_audio,
        language="es",
    )

    assert resultado.modo == ModoTranscripcion.FAKE
    assert resultado.idioma == "es"
    assert resultado.segmentos
    assert resultado.texto_bruto.startswith("La revision humana")


def test_fake_transcriber_rechaza_hash_inconsistente(audio_fixture_path):
    with pytest.raises(TranscriptionResponseError, match="hash del audio"):
        FakeFixtureTranscriptionAdapter().transcribir(
            __import__("pathlib").Path(audio_fixture_path),
            audio_sha256="hash_incorrecto",
            language="es",
        )


def test_fake_transcriber_rechaza_transcripcion_vacia(tmp_path, audio_fixture_path):
    from pathlib import Path

    audio_target = tmp_path / "audio.wav"
    audio_target.write_bytes(Path(audio_fixture_path).read_bytes())
    sidecar = audio_target.with_name(f"{audio_target.name}.transcription.json")
    sidecar.write_text(
        json.dumps(
            {
                "audio_sha256": validar_audio_local(audio_target, allowed_extensions={".wav"}).audio.sha256_audio,
                "idioma": "es",
                "texto": "   ",
                "segmentos": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(TranscriptionResponseError, match="vacía"):
        FakeFixtureTranscriptionAdapter().transcribir(
            audio_target,
            audio_sha256=validar_audio_local(audio_target, allowed_extensions={".wav"}).audio.sha256_audio,
            language="es",
        )


def test_sanitizar_transcripcion_redacta_pii_secretos_y_rutas():
    resultado = ResultadoTranscripcion(
        adaptador="fake",
        modo=ModoTranscripcion.FAKE,
        audio_sha256="sha",
        texto_bruto="Escribeme a persona@test.com, usa sk-12345678901234567890 y mira /home/alex/audio.wav",
        segmentos=[
            SegmentoTranscripcion(indice=1, texto="Llamame al 123-456-789 y revisa C:\\Users\\alex\\audio.wav")
        ],
        estado_completitud=EstadoCompletitudTranscripcion.COMPLETA,
    )

    sanitizada = sanitizar_transcripcion(resultado)

    assert "[EMAIL_REDACTED]" in sanitizada.texto_sanitizado
    assert "[SECRET_REDACTED]" in sanitizada.texto_sanitizado
    assert "[LOCAL_PATH_REDACTED]" in sanitizada.texto_sanitizado
    assert sanitizada.segmentos_sanitizados
    assert "telefono_redactado" in sanitizada.transformaciones


def test_construir_entrada_desde_audio_reutiliza_contrato_comun(audio_fixture_path):
    preparacion = construir_entrada_desde_audio(
        audio_path=audio_fixture_path,
        transcriber=FakeFixtureTranscriptionAdapter(),
        profile_id="perfil_audio",
        id_entrada="audio_001",
        language="es",
        metadatos_autorizados=json.loads(
            open("tests/fixtures/audio/smoke_incremento2.metadata.json", "r", encoding="utf-8").read()
        ),
    )

    assert preparacion.entrada.tipo_entrada == TipoEntrada.AUDIO
    assert preparacion.entrada.texto_base.startswith("La revision humana")
    assert preparacion.entrada.metadatos_origen["audio_sha256"] == preparacion.validacion.audio.sha256_audio
    assert preparacion.entrada.metadatos_origen["transcripcion_segmentos"]
    assert preparacion.entrada.estado_privacidad.sanitizado is True


def test_whisper_cpp_adapter_requiere_modelo_local():
    with pytest.raises(TranscriptionConfigurationError, match="MODEL_PATH"):
        WhisperCppTranscriptionAdapter(model_path="")


def test_whisper_cpp_adapter_falla_si_binario_no_esta(tmp_path):
    model = tmp_path / "modelo.bin"
    model.write_bytes(b"fake-model")
    adapter = WhisperCppTranscriptionAdapter(model_path=str(model), binary_path="binario-inexistente")

    with pytest.raises(TranscriptionDependencyError, match="whisper-cli"):
        adapter.transcribir(tmp_path / "audio.wav", audio_sha256="sha", language="es")
