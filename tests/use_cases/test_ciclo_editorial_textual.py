from datetime import datetime, timezone

import pytest

from linkedin_content_system.ai import ControlledModelAdapter
from linkedin_content_system.contracts import (
    EntradaContenido,
    EstadoCicloEditorial,
    EstadoIntencionEditorial,
    EstadoPrivacidad,
    IntencionEditorial,
    PerfilNarrativoReferencia,
    TipoEntrada,
    TipoAprobacion,
    EstadoRevision,
)
from linkedin_content_system.publishers import LocalDraftPublisher
from linkedin_content_system.publishers import ExternalDryRunPublisher
from linkedin_content_system.use_cases.ciclo_editorial_textual import (
    FilesystemEditorialSessionStore,
    aprobar_version,
    generar_borrador_pendiente,
    preparar_salida_aprobada,
    rechazar_version,
    solicitar_ajustes,
)


@pytest.fixture
def entrada_editorial():
    return EntradaContenido(
        id_entrada="in_ciclo_001",
        tipo_entrada=TipoEntrada.TEXTO_MANUAL,
        texto_base=(
            "Automatizar tareas repetitivas libera tiempo, pero las decisiones editoriales "
            "siguen necesitando criterio humano."
        ),
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="equipos pequenos",
            idea_central="Automatizar sin sustituir el criterio humano",
            cta_intencionado="Que parte mantendrias bajo revision humana",
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_editorial"),
        canales_destino=["linkedin"],
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={},
    )


def test_generar_crea_version_pendiente_sin_localdraft(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)

    sesion = generar_borrador_pendiente(
        entrada=entrada_editorial,
        adapter=ControlledModelAdapter(),
        store=store,
        clock=lambda: "2026-07-10T14:00:00Z",
    )

    assert sesion.estado == EstadoCicloEditorial.PENDIENTE_REVISION
    assert sesion.version_actual == 1
    assert sesion.versiones[0].version_anterior is None
    assert (tmp_path / "editorial_in_ciclo_001" / "versiones" / "v001.md").exists()
    assert not (tmp_path / "localdraft_in_ciclo_001").exists()


def test_generar_persiste_evidencia_operativa_saneada(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    evidencia = {
        "adapter": "litellm",
        "proveedor": "ollama",
        "modelo": "ollama_chat/modelo-sintetico",
        "duracion_ms": 123,
        "commit": "abc123",
        "fixture_sha256": "a" * 64,
        "perfil_sha256": "b" * 64,
    }

    generar_borrador_pendiente(
        entrada=entrada_editorial,
        adapter=ControlledModelAdapter(),
        store=store,
        evidencia_ejecucion=evidencia,
    )

    sesion = store.load(entrada_editorial.id_entrada)
    assert sesion.evidencia_ejecucion == evidencia


def test_salida_contaminada_no_crea_sesion_ni_version(tmp_path, entrada_editorial):
    class AdapterContaminado:
        def generar_texto(self, prompt, system_instruction=None):
            return "Post candidato.\nRevisión inicial: falta más voz."

    store = FilesystemEditorialSessionStore(tmp_path)

    with pytest.raises(ValueError, match="metatexto editorial"):
        generar_borrador_pendiente(entrada_editorial, AdapterContaminado(), store)

    assert not list(tmp_path.glob("editorial_*"))


def test_feedback_crea_nueva_version_trazable(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)

    sesion = solicitar_ajustes(
        id_entrada=entrada_editorial.id_entrada,
        feedback="Haz el inicio mas directo y conserva la pregunta final.",
        adapter=ControlledModelAdapter(),
        store=store,
    )

    assert sesion.estado == EstadoCicloEditorial.PENDIENTE_REVISION
    assert sesion.version_actual == 2
    assert sesion.versiones[-1].version_anterior == 1
    assert sesion.versiones[-1].feedback_origen.startswith("Haz el inicio")
    assert sesion.versiones[-1].texto != sesion.versiones[0].texto
    assert "Haz el inicio" in sesion.versiones[-1].texto
    assert (tmp_path / "editorial_in_ciclo_001" / "versiones" / "v002.md").exists()


def test_solo_version_aprobada_puede_prepararse(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)
    publisher = LocalDraftPublisher(str(tmp_path))

    with pytest.raises(ValueError, match="versión aprobada"):
        preparar_salida_aprobada(entrada_editorial.id_entrada, store, publisher)

    aprobar_version(
        id_entrada=entrada_editorial.id_entrada,
        version=1,
        aprobado_por="Revisor Sintetico",
        fecha_aprobacion="2026-07-10T14:30:00Z",
        store=store,
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        motivo_revision_reforzada="La pieza requiere revisión humana explícita.",
    )
    manifest = preparar_salida_aprobada(entrada_editorial.id_entrada, store, publisher)

    assert manifest.id_entrada == entrada_editorial.id_entrada
    assert (tmp_path / "localdraft_in_ciclo_001" / "post.md").exists()
    assert store.load(entrada_editorial.id_entrada).estado == EstadoCicloEditorial.PREPARADO


def test_aprobar_version_inexistente_falla(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)

    with pytest.raises(ValueError, match="no existe"):
        aprobar_version(
            entrada_editorial.id_entrada,
            3,
            "Revisor Sintetico",
            datetime.now(timezone.utc).isoformat(),
            store,
        )


def test_aprobacion_simple_de_version_warn_falla_y_mantiene_pendiente(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    sesion = generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)
    sesion.versiones[0].diagnostico_editorial.estado_revision = EstadoRevision.WARN
    store.save(sesion)

    with pytest.raises(ValueError, match="aprobación reforzada"):
        aprobar_version(
            entrada_editorial.id_entrada,
            1,
            "Revisor Sintetico",
            "2026-07-11T10:00:00Z",
            store,
        )

    sesion_persistida = store.load(entrada_editorial.id_entrada)
    assert sesion_persistida.estado == EstadoCicloEditorial.PENDIENTE_REVISION
    assert sesion_persistida.version_aprobada is None


def test_rechazar_version_conserva_la_sesion_y_bloquea_preparacion(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)

    sesion = rechazar_version(
        entrada_editorial.id_entrada,
        1,
        "La pieza no representa el enfoque deseado.",
        store,
    )

    assert sesion.estado == EstadoCicloEditorial.RECHAZADO
    assert sesion.version_actual == 1
    assert sesion.versiones[0].feedback_origen.startswith("La pieza no representa")
    with pytest.raises(ValueError, match="versión aprobada"):
        preparar_salida_aprobada(
            entrada_editorial.id_entrada,
            store,
            LocalDraftPublisher(str(tmp_path)),
        )


def test_preparado_no_admite_ajustes_ni_rechazo(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)
    aprobar_version(
        entrada_editorial.id_entrada,
        1,
        "Revisor Sintetico",
        "2026-07-11T10:00:00Z",
        store,
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        motivo_revision_reforzada="La pieza requiere revisión humana explícita.",
    )
    preparar_salida_aprobada(
        entrada_editorial.id_entrada,
        store,
        LocalDraftPublisher(str(tmp_path)),
    )

    with pytest.raises(ValueError, match="no permite la transición"):
        solicitar_ajustes(
            entrada_editorial.id_entrada,
            "Quiero otra versión.",
            ControlledModelAdapter(),
            store,
        )
    with pytest.raises(ValueError, match="no permite la transición"):
        rechazar_version(
            entrada_editorial.id_entrada,
            1,
            "No debe cambiarse una versión preparada.",
            store,
        )


def test_ajustes_registran_transicion_real_en_historial(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)

    sesion = solicitar_ajustes(
        entrada_editorial.id_entrada,
        "Aclara la idea central.",
        ControlledModelAdapter(),
        store,
    )

    assert [item.estado_destino for item in sesion.historial_estados][-2:] == [
        EstadoCicloEditorial.REQUIERE_AJUSTES,
        EstadoCicloEditorial.PENDIENTE_REVISION,
    ]


def test_documento_y_borrador_usan_el_mismo_ciclo_y_guardan_trazabilidad(tmp_path, entrada_editorial):
    for tipo in (TipoEntrada.DOCUMENTO_BASE, TipoEntrada.BORRADOR_EXISTENTE):
        entrada = entrada_editorial.model_copy(
            update={
                "id_entrada": f"in_{tipo.value}",
                "tipo_entrada": tipo,
                "metadatos_origen": {
                    "referencia_fuente": f"fixture_{tipo.value}",
                    "hechos_autorizados": ["La revisión humana precede a la salida."],
                },
            }
        )
        sesion = generar_borrador_pendiente(entrada, ControlledModelAdapter(), FilesystemEditorialSessionStore(tmp_path))

        assert sesion.versiones[0].trazabilidad_fuente["tipo_entrada"] == tipo.value
        assert sesion.versiones[0].trazabilidad_fuente["hechos_explicitos"]


def test_dos_regeneraciones_es_el_limite_y_luego_requiere_atencion(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)
    solicitar_ajustes(entrada_editorial.id_entrada, "Hazlo más breve.", ControlledModelAdapter(), store)
    solicitar_ajustes(entrada_editorial.id_entrada, "Hazlo más directo.", ControlledModelAdapter(), store)

    sesion = solicitar_ajustes(entrada_editorial.id_entrada, "Una tercera iteración no procede.", ControlledModelAdapter(), store)

    assert len(sesion.versiones) == 3
    assert sesion.estado == EstadoCicloEditorial.REQUIERE_ATENCION


def test_aprobado_puede_preparar_external_dry_run_sin_publicar(tmp_path, entrada_editorial):
    store = FilesystemEditorialSessionStore(tmp_path)
    generar_borrador_pendiente(entrada_editorial, ControlledModelAdapter(), store)
    aprobar_version(
        entrada_editorial.id_entrada, 1, "Revisor Sintetico", "2026-07-13T10:00:00Z", store,
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        motivo_revision_reforzada="Revisión humana explícita.",
    )

    manifest = preparar_salida_aprobada(
        entrada_editorial.id_entrada, store, ExternalDryRunPublisher(str(tmp_path))
    )

    payload = tmp_path / f"external_dryrun_{entrada_editorial.id_entrada}" / "publicacion_simulada.json"
    assert manifest.id_entrada == entrada_editorial.id_entrada
    assert '"no_publicado_realmente": true' in payload.read_text(encoding="utf-8")


def test_revisor_inyectado_evalua_sin_aprobar_la_sesion(tmp_path, entrada_editorial):
    from linkedin_content_system.use_cases.revisar_candidata_editorial import RevisorEditorialConservador

    class SpyReviewer:
        def __init__(self):
            self.invocado = False
            self.base = RevisorEditorialConservador()

        def revisar(self, **kwargs):
            self.invocado = True
            return self.base.revisar(**kwargs)

    revisor = SpyReviewer()
    sesion = generar_borrador_pendiente(
        entrada_editorial, ControlledModelAdapter(), FilesystemEditorialSessionStore(tmp_path), revisor=revisor
    )

    assert revisor.invocado is True
    assert sesion.aprobacion is None
    assert sesion.estado == EstadoCicloEditorial.PENDIENTE_REVISION
    assert sesion.versiones[0].trazabilidad_fuente["perfil_estado_completitud"] == "fallback"
