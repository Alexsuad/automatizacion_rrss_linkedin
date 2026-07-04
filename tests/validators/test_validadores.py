import pytest
from linkedin_content_system.contracts import (
    SalidaLocalDraft, PostCandidato, DiagnosticoEditorial, AprobacionHumana, EstadoAprobacion,
    EstadoRevision, NivelRiesgoGenerico, ModoPublicacion, AdaptadorActivo, EstadoSalidaLocal, TipoAprobacion
)
from linkedin_content_system.validators import (
    detectar_email, detectar_telefono_basico, detectar_secreto_basico,
    validar_texto_sin_pii_basica, validar_texto_sin_secretos_basicos,
    detectar_ruta_local, validar_sin_rutas_locales,
    validar_texto_no_vacio, validar_lista_no_vacia,
    validar_aprobacion_para_publicacion, validar_modo_dry_run_local,
    validar_salida_localdraft_segura
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
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="teléfono"):
        validar_salida_localdraft_segura(salida_bad_pii)

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
        aprobacion_humana=aprob,
        modo_publicacion=ModoPublicacion.DRY_RUN,
        adaptador_activo=AdaptadorActivo.LOCALDRAFT,
        estado=EstadoSalidaLocal.BORRADOR_LOCAL
    )
    with pytest.raises(ValueError, match="rutas locales"):
        validar_salida_localdraft_segura(salida)

