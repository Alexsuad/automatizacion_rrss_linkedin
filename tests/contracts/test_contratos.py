import pytest
from pydantic import ValidationError
from linkedin_content_system.contracts import (
    EntradaContenido, IntencionEditorial, PerfilNarrativoReferencia, EstadoIntencionEditorial, TipoEntrada, EstadoPrivacidad,
    DiagnosticoEditorial, EstadoRevision, NivelRiesgoGenerico,
    SalidaLocalDraft, AprobacionHumana, PostCandidato, EstadoAprobacion, ModoPublicacion, AdaptadorActivo, EstadoSalidaLocal,
    ManifestEvidencia, EstadoEvidencia
)

def test_entrada_valida_con_intencion_completa():
    entrada = EntradaContenido(
        id_entrada="in_001",
        tipo_entrada=TipoEntrada.AUDIO,
        texto_base="Este es el texto base de la nota de voz.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
            audiencia_objetivo="desarrolladores",
            idea_central="Whisper local funciona offline"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"no_inventar": True}
    )
    assert entrada.id_entrada == "in_001"
    assert entrada.intencion_editorial.estado_intencion_editorial == "completa"

def test_entrada_valida_con_intencion_parcial():
    entrada = EntradaContenido(
        id_entrada="in_002",
        tipo_entrada=TipoEntrada.AUDIO,
        texto_base="Texto base para derivar intencion.",
        intencion_editorial=IntencionEditorial(
            estado_intencion_editorial=EstadoIntencionEditorial.PARCIAL,
            audiencia_objetivo="desarrolladores"
        ),
        perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
        estado_privacidad=EstadoPrivacidad(sanitizado=True),
        restricciones={"no_inventar": True}
    )
    assert entrada.intencion_editorial.estado_intencion_editorial == "parcial"

def test_entrada_falla_sin_intencion_ni_insumo():
    with pytest.raises(ValidationError):
        EntradaContenido(
            id_entrada="in_003",
            tipo_entrada=TipoEntrada.AUDIO,
            texto_base="",
            intencion_editorial=IntencionEditorial(
                estado_intencion_editorial=EstadoIntencionEditorial.PARCIAL,
                audiencia_objetivo="desarrolladores"
            ),
            perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
            estado_privacidad=EstadoPrivacidad(sanitizado=True),
            restricciones={"no_inventar": True}
        )

    with pytest.raises(ValidationError):
        EntradaContenido(
            id_entrada="in_004",
            tipo_entrada=TipoEntrada.AUDIO,
            texto_base="",
            intencion_editorial=IntencionEditorial(
                estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA
            ),
            perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
            estado_privacidad=EstadoPrivacidad(sanitizado=True),
            restricciones={"no_inventar": True}
        )

def test_entrada_rechaza_tipo_entrada_invalido():
    with pytest.raises(ValidationError):
        EntradaContenido(
            id_entrada="in_005",
            tipo_entrada="video",
            texto_base="Texto base",
            intencion_editorial=IntencionEditorial(
                estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
                idea_central="Idea"
            ),
            perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
            estado_privacidad=EstadoPrivacidad(sanitizado=True),
            restricciones={}
        )

def test_entrada_rechaza_privacidad_no_sanitizada():
    with pytest.raises(ValidationError):
        EntradaContenido(
            id_entrada="in_006",
            tipo_entrada=TipoEntrada.AUDIO,
            texto_base="Texto base",
            intencion_editorial=IntencionEditorial(
                estado_intencion_editorial=EstadoIntencionEditorial.COMPLETA,
                idea_central="Idea"
            ),
            perfil_narrativo=PerfilNarrativoReferencia(id_perfil="perfil_001"),
            estado_privacidad=EstadoPrivacidad(sanitizado=False),
            restricciones={}
        )

def test_diagnostico_editorial_valido():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.WARN,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
        motivo="Consistente",
        ajustes_recomendados="Revisar CTA"
    )
    assert diag.estado_revision == "PASS"

def test_diagnostico_editorial_rechaza_estado_invalido():
    with pytest.raises(ValidationError):
        DiagnosticoEditorial(
            claridad_idea="EXCELENTE",
            audiencia=EstadoRevision.PASS,
            hook=EstadoRevision.PASS,
            voz_cliente=EstadoRevision.PASS,
            autenticidad=EstadoRevision.PASS,
            cta=EstadoRevision.PASS,
            compliance=EstadoRevision.PASS,
            riesgo_generico=NivelRiesgoGenerico.BAJO,
            estado_revision=EstadoRevision.PASS
        )

def test_salida_localdraft_valida():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Este es mi post de LinkedIn."),
        diagnostico_editorial=diag,
        aprobacion_humana=AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex",
            fecha_aprobacion="2026-07-04T01:38:00Z"
        ),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL,
        fecha_objetivo_sugerida="2026-07-07T09:00:00Z"
    )
    assert salida.post.texto == "Este es mi post de LinkedIn."
    assert salida.aprobacion_humana.estado == "aprobado"

def test_salida_rechaza_modo_publicacion_invalido():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS
    )
    with pytest.raises(ValidationError):
        SalidaLocalDraft(
            post=PostCandidato(texto="Post"),
            diagnostico_editorial=diag,
            aprobacion_humana=AprobacionHumana(
                estado=EstadoAprobacion.APROBADO,
                aprobado_por="Alex",
                fecha_aprobacion="2026-07-04T01:38:00Z"
            ),
            modo_publicacion="publicacion_real",
            adaptador_activo=AdaptadorActivo.LOCALDRAFT,
            estado=EstadoSalidaLocal.BORRADOR_LOCAL
        )

def test_salida_rechaza_adaptador_no_local():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS
    )
    with pytest.raises(ValidationError):
        SalidaLocalDraft(
            post=PostCandidato(texto="Post"),
            diagnostico_editorial=diag,
            aprobacion_humana=AprobacionHumana(
                estado=EstadoAprobacion.APROBADO,
                aprobado_por="Alex",
                fecha_aprobacion="2026-07-04T01:38:00Z"
            ),
            modo_publicacion=ModoPublicacion.DRY_RUN,
            adaptador_activo="metricool",
            estado=EstadoSalidaLocal.BORRADOR_LOCAL
        )

def test_aprobacion_aprobada_requiere_responsable_y_fecha():
    aprob_pendiente = AprobacionHumana(estado=EstadoAprobacion.PENDIENTE)
    assert aprob_pendiente.estado == "pendiente"

    with pytest.raises(ValidationError):
        AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            fecha_aprobacion="2026-07-04T01:38:00Z"
        )

    with pytest.raises(ValidationError):
        AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex"
        )

def test_manifest_evidencia_valido():
    evidencia = ManifestEvidencia(
        id_evidencia="ev_001",
        id_entrada="in_001",
        archivos_generados=["output/kit_001/post.md"],
        estado=EstadoEvidencia.GUARDADO_LOCAL,
        timestamp="2026-07-04T01:38:00Z"
    )
    assert evidencia.id_evidencia == "ev_001"

def test_manifest_rechaza_archivos_generados_vacio():
    with pytest.raises(ValidationError):
        ManifestEvidencia(
            id_evidencia="ev_002",
            id_entrada="in_001",
            archivos_generados=[],
            estado=EstadoEvidencia.GUARDADO_LOCAL,
            timestamp="2026-07-04T01:38:00Z"
        )

def test_manifest_rechaza_estado_invalido():
    with pytest.raises(ValidationError):
        ManifestEvidencia(
            id_evidencia="ev_003",
            id_entrada="in_001",
            archivos_generados=["output/kit_001/post.md"],
            estado="publicado_externo",
            timestamp="2026-07-04T01:38:00Z"
        )
