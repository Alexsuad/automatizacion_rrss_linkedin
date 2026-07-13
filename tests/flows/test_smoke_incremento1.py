import json

from linkedin_content_system.ai.ports import ModelAdapter
from linkedin_content_system.contracts import (
    EntradaContenido, EstadoCicloEditorial, EstadoIntencionEditorial, EstadoPrivacidad,
    IntencionEditorial, PerfilNarrativoReferencia, TipoAprobacion, TipoEntrada,
)
from linkedin_content_system.publishers import ExternalDryRunPublisher
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore, aprobar_version, generar_borrador_pendiente,
    preparar_salida_aprobada,
)


class AdapterSmokeIncremento1(ModelAdapter):
    def __init__(self):
        self.respuestas = iter([
            "En un mundo donde todo cambia, revisar es importante.",
            "La revisión humana precede a la salida. ¿Qué revisarías antes de aprobar?",
        ])

    def generar_texto(self, prompt, system_instruction=None):
        return next(self.respuestas)


def test_smoke_incremento1_documento_a_external_dry_run(tmp_path):
    entrada = EntradaContenido(
        id_entrada="smoke_incremento1", tipo_entrada=TipoEntrada.DOCUMENTO_BASE,
        texto_base="El documento confirma que la revisión humana precede a cualquier salida.",
        intencion_editorial=IntencionEditorial(estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA, idea_central="La revisión humana precede a cualquier salida", cta_intencionado="¿Qué revisarías antes de aprobar?"),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_smoke"), canales_destino=["linkedin"],
        metadatos_origen={"referencia_fuente": "smoke_documento_sintetico", "hechos_autorizados": ["La revisión humana precede a cualquier salida."], "opiniones_explicitas": ["La automatización no sustituye el criterio."], "experiencias_autorizadas": [], "afirmaciones_pendientes": ["No afirmar resultados de negocio."]},
        estado_privacidad=EstadoPrivacidad(sanitizado=True), restricciones={},
    )
    store = FilesystemEditorialSessionStore(tmp_path)
    sesion = generar_borrador_pendiente(entrada, AdapterSmokeIncremento1(), store)

    assert sesion.version_seleccionada == 2
    assert len(sesion.versiones) == 2
    assert sesion.versiones[0].auditoria_editorial.feedback_estructurado
    assert sesion.versiones[0].trazabilidad_fuente["fragmentos_evidencia"]
    assert sesion.estado == EstadoCicloEditorial.PENDIENTE_REVISION
    aprobar_version("smoke_incremento1", 2, "Revisor Sintético", "2026-07-13T12:00:00Z", store, TipoAprobacion.REFORZADA, "Revisión humana simulada.")
    manifest = preparar_salida_aprobada("smoke_incremento1", store, ExternalDryRunPublisher(str(tmp_path)))

    payload = json.loads((tmp_path / "external_dryrun_smoke_incremento1" / "publicacion_simulada.json").read_text(encoding="utf-8"))
    assert manifest.id_entrada == "smoke_incremento1"
    assert payload["no_publicado_realmente"] is True
    assert payload["salida_origen"]["trazabilidad_editorial"]["version_seleccionada"] == 2
    assert payload["salida_origen"]["trazabilidad_editorial"]["referencia_fuente"] == "smoke_documento_sintetico"
    assert not (tmp_path / "localdraft_smoke_incremento1").exists()
