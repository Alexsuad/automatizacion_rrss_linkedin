from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    EntradaContenido, EstadoCicloEditorial, EstadoIntencionEditorial, EstadoPrivacidad,
    IntencionEditorial, PerfilNarrativoReferencia, TipoEntrada,
)
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore, aprobar_version, generar_borrador_pendiente,
)
from linkedin_content_system.use_cases.revisar_candidata_editorial import RevisorEditorialDeterminista


def _entrada():
    return EntradaContenido(
        id_entrada="auto_001", tipo_entrada=TipoEntrada.DOCUMENTO_BASE,
        texto_base="La fuente confirma que la revisión humana precede a la salida.",
        intencion_editorial=IntencionEditorial(estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA, idea_central="La revisión humana precede a la salida"),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_auto"), canales_destino=["linkedin"],
        metadatos_origen={"referencia_fuente": "documento_auto", "hechos_autorizados": ["La revisión humana precede a la salida."]},
        estado_privacidad=EstadoPrivacidad(sanitizado=True), restricciones={},
    )


def test_defecto_corregible_genera_v2_y_selecciona_la_mejor(tmp_path):
    class AdapterSecuencial(ModelAdapter):
        def __init__(self): self.respuestas = iter([
            "En un mundo donde todo cambia, revisar es importante.",
            "La revisión humana precede a la salida. ¿Qué revisarías antes de aprobar?",
        ])
        def generar_texto(self, prompt, system_instruction=None): return next(self.respuestas)

    sesion = generar_borrador_pendiente(_entrada(), AdapterSecuencial(), FilesystemEditorialSessionStore(tmp_path))

    assert len(sesion.versiones) == 2
    assert sesion.version_seleccionada == 2
    assert sesion.mejora_editorial_demostrada is True
    assert sesion.versiones[1].version_anterior == 1
    assert sesion.versiones[1].feedback_origen


def test_defecto_persistente_se_detiene_en_dos_regeneraciones(tmp_path):
    class AdapterPersistente(ModelAdapter):
        def generar_texto(self, prompt, system_instruction=None):
            return "En un mundo donde todo cambia, revisar es importante."

    sesion = generar_borrador_pendiente(_entrada(), AdapterPersistente(), FilesystemEditorialSessionStore(tmp_path))

    assert len(sesion.versiones) == 3
    assert sesion.version_seleccionada is None
    assert sesion.estado == EstadoCicloEditorial.REQUIERE_ATENCION
    assert sesion.mejora_editorial_demostrada is False


def test_version_no_seleccionada_no_puede_aprobarse(tmp_path):
    class AdapterSecuencial(ModelAdapter):
        def __init__(self): self.respuestas = iter(["En un mundo donde todo cambia, revisar es importante.", "La revisión humana precede a la salida. ¿Qué revisarías?"])
        def generar_texto(self, prompt, system_instruction=None): return next(self.respuestas)
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(_entrada(), AdapterSecuencial(), store)

    try:
        aprobar_version("auto_001", 1, "Revisor", "2026-07-13T12:00:00Z", store)
    except ValueError as exc:
        assert "seleccionada" in str(exc)
    else:
        raise AssertionError("La versión no seleccionada no puede aprobarse.")


def test_revisor_devuelve_hallazgo_estructurado_de_genericidad():
    from linkedin_content_system.use_cases.normalizar_entrada_textual import normalizar_entrada_textual
    from linkedin_content_system.use_cases.flujo_textual_runtime import FilesystemNarrativeProfileResolver
    fuente = normalizar_entrada_textual(_entrada())
    audit = RevisorEditorialDeterminista().revisar(fuente, FilesystemNarrativeProfileResolver().resolve("perfil_auto"), "En un mundo donde todo cambia, revisar es importante.")
    assert audit.estado.value == "WARN"
    assert audit.hallazgos[0].categoria == "genericidad"
    assert audit.hallazgos[0].requiere_regeneracion is True


def test_revisor_devuelve_pass_solo_con_candidata_sin_hallazgos_verificables():
    from linkedin_content_system.use_cases.normalizar_entrada_textual import normalizar_entrada_textual
    from linkedin_content_system.use_cases.flujo_textual_runtime import FilesystemNarrativeProfileResolver
    audit = RevisorEditorialDeterminista().revisar(
        normalizar_entrada_textual(_entrada()),
        FilesystemNarrativeProfileResolver().resolve("perfil_auto"),
        "La revisión humana precede a la salida. ¿Qué revisarías antes de aprobar?",
    )
    assert audit.estado.value == "PASS"
    assert audit.hallazgos == []
