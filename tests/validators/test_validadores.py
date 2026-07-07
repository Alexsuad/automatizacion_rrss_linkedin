import pytest
from linkedin_content_system.contracts import (
    SalidaLocalDraft, PostCandidato, DiagnosticoEditorial, AprobacionHumana, EstadoAprobacion,
    EstadoRevision, NivelRiesgoGenerico, ModoPublicacion, AdaptadorActivo, EstadoSalidaLocal, TipoAprobacion,
    BloqueoCritico, TipoBloqueoCritico
)
from linkedin_content_system.contracts.salida import EstadoPublicabilidad
from linkedin_content_system.contracts.trazabilidad import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
    HallazgoTrazabilidad,
    TipoHallazgoTrazabilidad,
)
from linkedin_content_system.validators import (
    detectar_email, detectar_telefono_basico, detectar_secreto_basico,
    validar_texto_sin_pii_basica, validar_texto_sin_secretos_basicos,
    detectar_ruta_local, validar_sin_rutas_locales,
    validar_texto_no_vacio, validar_lista_no_vacia,
    validar_aprobacion_para_publicacion, validar_modo_dry_run_local,
    resolver_estado_publicabilidad, validar_salida_localdraft_segura
)

def test_validar_no_pii_detecta_correo_y_telefono():
    assert detectar_email("Mi correo es alex@test.com") is True
    with pytest.raises(ValueError, match="correo electrónico"):
        validar_texto_sin_pii_basica("Mi correo es alex@test.com")

    assert detectar_telefono_basico("Llamame al 123-456-789") is True
    with pytest.raises(ValueError, match="teléfono"):
        validar_texto_sin_pii_basica("Llamame al 123-456-789")

def test_validar_no_secretos_detecta_tokens():
    assert detectar_secreto_basico("Clave sk-proj12345678901234567890") is True
    with pytest.raises(ValueError, match="secretos o credenciales"):
        validar_texto_sin_secretos_basicos("Clave sk-proj12345678901234567890")

    assert detectar_secreto_basico("Bearer abc123xyz") is True
    assert detectar_secreto_basico("password=admin123") is True
    assert detectar_secreto_basico("api_key=mykeysecret") is True

def test_validar_no_rutas_absolutas_detecta_caminos_locales():
    assert detectar_ruta_local("Enlace: file:///path/to/file") is True
    with pytest.raises(ValueError, match="rutas locales"):
        validar_sin_rutas_locales("Enlace: file:///path/to/file")

    assert detectar_ruta_local("Directorio: /home/user/code") is True
    assert detectar_ruta_local("Directorio: C:/Users/name") is True
    assert detectar_ruta_local("Directorio: /mnt/data/source") is True
    assert detectar_ruta_local("Directorio: \\wsl$\\Ubuntu") is True

def test_texto_limpio_aceptado():
    texto = "Este es un texto seguro sin credenciales ni rutas absolutas."
    validar_texto_sin_pii_basica(texto)
    validar_texto_sin_secretos_basicos(texto)
    validar_sin_rutas_locales(texto)
    validar_texto_no_vacio(texto)

def test_texto_vacio_rechazado():
    with pytest.raises(ValueError, match="no puede estar vacío"):
        validar_texto_no_vacio("")
    with pytest.raises(ValueError, match="no puede estar vacío"):
        validar_texto_no_vacio("   ")

def test_lista_vacia_rechazada():
    with pytest.raises(ValueError, match="no puede estar vacía"):
        validar_lista_no_vacia([])
    validar_lista_no_vacia([1, 2])

def test_publicacion_rechazada_si_aprobacion_pendiente():
    aprob = AprobacionHumana(estado=EstadoAprobacion.PENDIENTE)
    with pytest.raises(ValueError, match="Publicación denegada"):
        validar_aprobacion_para_publicacion(aprob)

def test_publicacion_aceptada_si_aprobacion_aprobada_con_fecha_y_responsable():
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )
    validar_aprobacion_para_publicacion(aprob)


def _trazabilidad_pass():
    return DiagnosticoTrazabilidad(estado=EstadoTrazabilidad.PASS)

@pytest.mark.parametrize(
    "estado_revision,tipo_aprobacion,estado_aprobacion,expected",
    [
        (EstadoRevision.PASS, TipoAprobacion.SIMPLE, EstadoAprobacion.APROBADO, "publicable"),
        (EstadoRevision.WARN, TipoAprobacion.REFORZADA, EstadoAprobacion.APROBADO, "publicable"),
        (EstadoRevision.WARN, TipoAprobacion.SIMPLE, EstadoAprobacion.APROBADO, "requiere_revision"),
        (EstadoRevision.FAIL, TipoAprobacion.REFORZADA, EstadoAprobacion.APROBADO, "rechazado_editorial"),
        (EstadoRevision.PASS, TipoAprobacion.SIMPLE, EstadoAprobacion.PENDIENTE, "no_publicable"),
        (EstadoRevision.PASS, TipoAprobacion.SIMPLE, EstadoAprobacion.RECHAZADO, "no_publicable"),
    ],
)
def test_resolver_estado_publicabilidad(
    estado_revision,
    tipo_aprobacion,
    estado_aprobacion,
    expected,
):
    diag_kwargs = dict(
        claridad_idea=estado_revision,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=estado_revision,
    )
    if estado_revision == EstadoRevision.FAIL:
        diag_kwargs["bloqueos_criticos"] = [
            BloqueoCritico(tipo=TipoBloqueoCritico.PII, descripcion="Email detectado")
        ]

    diag = DiagnosticoEditorial(**diag_kwargs)
    aprob = AprobacionHumana(
        estado=estado_aprobacion,
        aprobado_por="Alex" if estado_aprobacion == EstadoAprobacion.APROBADO else None,
        fecha_aprobacion="2026-07-04T01:53:00Z" if estado_aprobacion == EstadoAprobacion.APROBADO else None,
        tipo_aprobacion=tipo_aprobacion,
        motivo_revision_reforzada=(
            "Revisión reforzada validada"
            if tipo_aprobacion == TipoAprobacion.REFORZADA and estado_aprobacion == EstadoAprobacion.APROBADO
            else None
        ),
    )

    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=_trazabilidad_pass(),
    ).value == expected

def test_resolver_estado_publicabilidad_sin_trazabilidad_no_es_publicable():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )

    assert resolver_estado_publicabilidad(diag, aprob, diagnostico_trazabilidad=None) == EstadoPublicabilidad.NO_PUBLICABLE

def test_resolver_estado_publicabilidad_fail_editorial_sin_trazabilidad_sigue_siendo_rechazado():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.FAIL,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.FAIL,
        bloqueos_criticos=[
            BloqueoCritico(tipo=TipoBloqueoCritico.PII, descripcion="Email detectado")
        ],
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )

    assert resolver_estado_publicabilidad(diag, aprob, diagnostico_trazabilidad=None) == EstadoPublicabilidad.RECHAZADO_EDITORIAL

def test_resolver_estado_publicabilidad_trazabilidad_warn_con_aprobacion_simple_es_requiere_revision():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z",
        tipo_aprobacion=TipoAprobacion.SIMPLE,
    )
    diagnostico_trazabilidad = DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.WARN,
        hallazgos=[
            HallazgoTrazabilidad(
                tipo=TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
                fragmento_post="Quizá",
                descripcion="Inferencia débil",
                bloqueante=False,
            )
        ],
        resumen="Solo una inferencia débil.",
    )

    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
    ) == EstadoPublicabilidad.REQUIERE_REVISION

def test_resolver_estado_publicabilidad_trazabilidad_warn_con_aprobacion_reforzada_es_publicable():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z",
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        revision_reforzada_requerida=True,
        motivo_revision_reforzada="Se aceptó la inferencia débil.",
    )
    diagnostico_trazabilidad = DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.WARN,
        hallazgos=[
            HallazgoTrazabilidad(
                tipo=TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
                fragmento_post="Quizá",
                descripcion="Inferencia débil",
                bloqueante=False,
            )
        ],
        resumen="Solo una inferencia débil.",
    )

    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
    ) == EstadoPublicabilidad.PUBLICABLE

def test_resolver_estado_publicabilidad_editorial_warn_y_trazabilidad_warn_con_aprobacion_reforzada_es_publicable():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.WARN,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.WARN,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z",
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        revision_reforzada_requerida=True,
        motivo_revision_reforzada="Se aceptaron los warnings.",
    )
    diagnostico_trazabilidad = DiagnosticoTrazabilidad(
        estado=EstadoTrazabilidad.WARN,
        hallazgos=[
            HallazgoTrazabilidad(
                tipo=TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
                fragmento_post="Quizá",
                descripcion="Inferencia débil",
                bloqueante=False,
            )
        ],
        resumen="Solo una inferencia débil.",
    )

    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=diagnostico_trazabilidad,
    ) == EstadoPublicabilidad.PUBLICABLE


def test_resolver_estado_publicabilidad_rechaza_riesgo_alto():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.ALTO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )
    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=_trazabilidad_pass(),
    ) == EstadoPublicabilidad.RECHAZADO_EDITORIAL

def test_resolver_estado_publicabilidad_rechaza_compliance_fail():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.FAIL,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )
    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=_trazabilidad_pass(),
    ) == EstadoPublicabilidad.RECHAZADO_EDITORIAL

def test_resolver_estado_publicabilidad_rechaza_autenticidad_fail():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.FAIL,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )
    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=_trazabilidad_pass(),
    ) == EstadoPublicabilidad.RECHAZADO_EDITORIAL

@pytest.mark.parametrize("estado_aprobacion", [EstadoAprobacion.PENDIENTE, EstadoAprobacion.RECHAZADO])
def test_resolver_estado_publicabilidad_fail_con_aprobacion_no_aprobada_sigue_siendo_rechazado(
    estado_aprobacion,
):
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.FAIL,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.FAIL,
    )
    aprob = AprobacionHumana(estado=estado_aprobacion)

    assert resolver_estado_publicabilidad(
        diag,
        aprob,
        diagnostico_trazabilidad=_trazabilidad_pass(),
    ) == EstadoPublicabilidad.RECHAZADO_EDITORIAL

def test_salida_rechazada_si_no_es_dry_run_localdraft_borrador_local():
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
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T01:53:00Z"
    )
    salida_ok = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    validar_modo_dry_run_local(salida_ok)
    validar_salida_localdraft_segura(salida_ok)

    salida_bad_pii = SalidaLocalDraft(
        post=PostCandidato(texto="Llamame al 123-456-789"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="teléfono"):
        validar_salida_localdraft_segura(salida_bad_pii)

def test_validar_salida_marca_no_publicable_si_aprobacion_pendiente():
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
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=AprobacionHumana(estado=EstadoAprobacion.PENDIENTE),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="Publicación denegada"):
        validar_salida_localdraft_segura(salida)
    assert salida.estado_publicabilidad == EstadoPublicabilidad.NO_PUBLICABLE

def test_validar_salida_marca_rechazado_editorial_si_riesgo_alto():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.ALTO,
        estado_revision=EstadoRevision.PASS
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=AprobacionHumana(
            estado=EstadoAprobacion.APROBADO,
            aprobado_por="Alex",
            fecha_aprobacion="2026-07-04T01:53:00Z"
        ),
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="nivel de riesgo genérico es alto"):
        validar_salida_localdraft_segura(salida)
    assert salida.estado_publicabilidad == EstadoPublicabilidad.RECHAZADO_EDITORIAL

def test_validar_editorial_fail_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.FAIL,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.FAIL
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="estado_revision es FAIL"):
        validar_salida_localdraft_segura(salida)

def test_validar_bloqueos_criticos_bloquea():
    from linkedin_content_system.contracts import BloqueoCritico, TipoBloqueoCritico
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.FAIL,
        bloqueos_criticos=[
            BloqueoCritico(tipo=TipoBloqueoCritico.PII, descripcion="Email en post")
        ]
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="bloqueos críticos"):
        validar_salida_localdraft_segura(salida)

def test_validar_riesgo_alto_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.ALTO,
        estado_revision=EstadoRevision.PASS
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="riesgo genérico es alto"):
        validar_salida_localdraft_segura(salida)

def test_validar_compliance_fail_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.FAIL,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="compliance es FAIL"):
        validar_salida_localdraft_segura(salida)

def test_validar_autenticidad_fail_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.FAIL,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="autenticidad es FAIL"):
        validar_salida_localdraft_segura(salida)

def test_validar_warn_sin_aprobacion_reforzada_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.WARN
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z",
        tipo_aprobacion=TipoAprobacion.SIMPLE
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="no se cuenta con una aprobación reforzada"):
        validar_salida_localdraft_segura(salida)

def test_validar_warn_con_aprobacion_reforzada_permite():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.WARN
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z",
        tipo_aprobacion=TipoAprobacion.REFORZADA,
        revision_reforzada_requerida=True,
        motivo_revision_reforzada="Warning de estilo aceptado."
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    # Permite sin excepciones
    validar_salida_localdraft_segura(salida)

def test_sanitiza_motivo_diagnostico_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
        motivo="Contiene PII: correo@test.com"
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="correo electrónico"):
        validar_salida_localdraft_segura(salida)

def test_sanitiza_ajustes_recomendados_bloquea():
    diag = DiagnosticoEditorial(
        claridad_idea=EstadoRevision.PASS,
        audiencia=EstadoRevision.PASS,
        hook=EstadoRevision.PASS,
        voz_cliente=EstadoRevision.PASS,
        autenticidad=EstadoRevision.PASS,
        cta=EstadoRevision.PASS,
        compliance=EstadoRevision.PASS,
        riesgo_generico=NivelRiesgoGenerico.BAJO,
        estado_revision=EstadoRevision.PASS,
        ajustes_recomendados="Remover token sk-projabcdefghijklmnopqrstuvwx"
    )
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="secretos o credenciales"):
        validar_salida_localdraft_segura(salida)

def test_sanitiza_comentarios_aprobacion_bloquea():
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
    aprob = AprobacionHumana(
        estado=EstadoAprobacion.APROBADO,
        aprobado_por="Alex",
        fecha_aprobacion="2026-07-04T12:00:00Z",
        comentarios="Ver archivo en file:///home/user/passwords.txt"
    )
    salida = SalidaLocalDraft(
        post=PostCandidato(texto="Post limpio"),
        diagnostico_editorial=diag,
        diagnostico_trazabilidad=_trazabilidad_pass(),
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="rutas locales"):
        validar_salida_localdraft_segura(salida)
