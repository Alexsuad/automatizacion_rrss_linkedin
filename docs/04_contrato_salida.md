# 04 — Contrato de salida del proceso V1

## 1. Propósito del documento

Este documento define la estructura y el contrato del objeto de salida final generado por el sistema tras completar el flujo completo del publicador automático. 

Sirve como la estructura de datos que se guardará localmente como evidencia del flujo y del resultado de la publicación/programación, priorizando en V1 el modo de simulación local (`LocalDraftPublisher`) offline y dejando adaptadores externos (como Metricool) como implementaciones posibles posteriores.

---

## 2. Estructura conceptual del Contrato de Salida (Kit de Salida V1)

Al finalizar el proceso, el sistema guarda un archivo JSON de salida en `output/kit_<id>/salida_v1.json` con la siguiente estructura conceptual (donde se prefiere el adaptador local como ejemplo base):

```json
{
  "id_proceso": "proc_lnk_001",
  "id_entrada": "in_lnk_001",
  "perfil_narrativo": "perfil_profesional_linkedin",
  "fecha_procesamiento": "2026-07-03T11:15:00Z",
  "transcripcion": {
    "sanitizada": "Transcripción con datos personales (PII) anonimizados o removidos...",
    "ruta_transcripcion_bruta_privada": null
  },
  "post_generado": {
    "version_inicial": "Contenido del post de LinkedIn generado por el LLM...",
    "version_aprobada": "Contenido del post de LinkedIn final, tras revisión y edición humana (si aplica)..."
  },
  "revision_automatica": {
    "pasa_filtro_calidad": true,
    "cumple_reglas_perfil": true,
    "pii_detectada": false,
    "comentarios_auditoria": []
  },
  "diagnostico_editorial": {
    "claridad_idea": "PASS",
    "audiencia": "PASS",
    "hook": "PASS",
    "voz_cliente": "PASS",
    "autenticidad": "PASS",
    "cta": "PASS",
    "compliance": "PASS",
    "riesgo_generico": "bajo",
    "estado_revision": "PASS"
  },
  "aprobacion_humana": {
    "estado": "aprobado",
    "fecha_aprobacion": "2026-07-03T11:18:22Z",
    "comentarios_usuario": "Aprobado sin cambios adicionales"
  },
  "recomendacion_timing": {
    "zona_horaria": "Europe/Madrid",
    "ventana_horaria_recomendada": "Martes de 08:30 a 10:00",
    "justificacion_timing": "Recomendación conservadora para audiencia B2B en horario laboral local; ajustable según histórico del cliente.",
    "excepcion_timing": "Se permite publicar fuera de ventana si coincide con un evento en vivo relevante o noticia de última hora."
  },
  "publicacion": {
    "adaptador_activo": "localdraft",
    "modo_publicacion": "dry_run",
    "estado": "borrador_local",
    "fecha_objetivo_sugerida": "2026-07-07T09:00:00Z",
    "id_publicacion_externa": null,
    "detalles_resultado": "Borrador local guardado en disco con éxito para revisión offline.",
    "evidencia_local_path": "output/kit_001/evidencia_publicacion.json"
  }
}
```

> [!NOTE]
> En modo `localdraft` / `dry_run`, cualquier fecha objetivo (como `fecha_objetivo_sugerida`) es meramente orientativa y no representa programación real en plataformas externas.

---

## 3. Campos del contrato de salida

*   `id_proceso`: Identificador del proceso de automatización.
*   `transcripcion.sanitizada`: (Obligatoria si el flujo la necesita) Texto base una vez procesado por el filtro de PII.
*   `transcripcion.ruta_transcripcion_bruta_privada`: (Opcional) Ruta a la transcripción en bruto. Puede ser `null` o no persistirse si la política de privacidad activa decide no almacenarla en disco.
*   `post_generado.version_aprobada`: El texto real que fue aprobado y programado.
*   `diagnostico_editorial`: Objeto que contiene las evaluaciones de calidad editorial (`claridad_idea`, `audiencia`, `hook`, `voz_cliente`, `autenticidad`, `cta`, `compliance`, `riesgo_generico`, `estado_revision`).
*   `aprobacion_humana.estado`: Estado del gate (`aprobado`, `rechazado`, `pendiente`).
*   `recomendacion_timing`: Objeto que detalla la recomendación horaria para la publicación en LinkedIn (`zona_horaria`, `ventana_horaria_recomendada`, `justificacion_timing`, `excepcion_timing`).
*   `publicacion.adaptador_activo`: Identifica si se usó `localdraft` (adaptador principal V1) o adaptadores externos posteriores (ej: `metricool`).
*   `publicacion.estado`: Estado de la publicación (`programado`, `borrador_local`, `dry_run`, `error`).
*   `publicacion.id_publicacion_externa`: ID en el proveedor externo, o `null` si se publica localmente.

---

## 4. Evidencia local y Seguridad de logs

*   **Evidencia Local Obligatoria:** Todos los kits de salida se almacenan en carpetas locales numeradas (`output/kit_<id>/`).
*   **Limpieza de Datos:** Las evidencias del adaptador no deben guardar bajo ninguna circunstancia credenciales de API, tokens de autenticación ni PII sin sanitizar.
*   **Pruebas Offline:** Por defecto, el sistema prioriza el modo `dry_run` con `localdraft` (LocalDraftPublisher), evitando cualquier llamada real a las APIs externas y permitiendo probar el flujo completo de forma offline sin coste ni riesgo operativo. La publicación real queda relegada a adaptadores posteriores una vez validada la estabilidad local.
