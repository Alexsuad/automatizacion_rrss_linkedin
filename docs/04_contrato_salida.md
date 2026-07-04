# 04 — Contrato de salida del proceso V1

## 1. Propósito del documento

Este documento define la estructura y el contrato del objeto de salida final generado por el sistema tras completar el flujo completo del publicador automático. 

Sirve como la estructura de datos que se guardará localmente como evidencia del flujo y del resultado de la publicación/programación, priorizando en V1 el modo de simulación local (`LocalDraftPublisher`) offline y dejando adaptadores externos (como Metricool) como implementaciones posibles posteriores.

---

## 2. Estructura conceptual del Contrato de Salida (Kit de Salida V1)

Al finalizar el proceso, el sistema guarda un archivo JSON de salida en `output/localdraft_<id_entrada>/salida_v1.json` con la siguiente estructura conceptual. Este archivo representa de forma fidedigna el modelo serializado de `SalidaLocalDraft`:

```json
{
  "post": {
    "texto": "Contenido final del post de LinkedIn generado y aprobado..."
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
    "estado_revision": "PASS",
    "motivo": "El contenido cumple con la coherencia...",
    "ajustes_recomendados": null,
    "bloqueos_criticos": []
  },
  "aprobacion_humana": {
    "estado": "aprobado",
    "aprobado_por": "Alex Revisor",
    "fecha_aprobacion": "2026-07-04T11:00:00Z",
    "comentarios": "Aprobado sin cambios adicionales",
    "tipo_aprobacion": "simple",
    "revision_reforzada_requerida": false,
    "motivo_revision_reforzada": null
  },
  "modo_publicacion": "dry_run",
  "adaptador_activo": "localdraft",
  "estado": "borrador_local",
  "fecha_objetivo_sugerida": "2026-07-07T09:00:00Z"
}
```

> [!NOTE]
> En modo `localdraft` / `dry_run`, cualquier fecha objetivo (como `fecha_objetivo_sugerida`) es meramente orientativa y no representa programación real en plataformas externas.

---

## 3. Matriz de Publicabilidad Editorial y Gates

La persistencia de la salida y el almacenamiento de evidencias están controlados por un gate determinista estricto que evalúa el diagnóstico editorial y la aprobación humana:

*   **PASS + Aprobado (Simple):** Si `estado_revision == PASS` y la aprobación humana tiene `estado == aprobado` y `tipo_aprobacion == simple`, se permite guardar en disco localmente.
*   **WARN + Aprobado (Reforzado):** Si `estado_revision == WARN`, el sistema bloquea cualquier intento de guardado a menos que la aprobación humana tenga `estado == aprobado` y su `tipo_aprobacion == reforzada`. Esto asegura que el revisor humano ha levantado conscientemente el warning editorial.
*   **FAIL / Bloqueos Críticos:** Si `estado_revision == FAIL` o el diagnóstico contiene cualquier `bloqueo_critico`, el flujo se detiene de inmediato. Está estrictamente prohibido guardar como borrador local listo.
*   **Aprobación Pendiente:** Si el estado de aprobación no es `aprobado`, no se permite la persistencia final de salida como borrador publicable.

---

## 4. Evidencia local y Seguridad

*   **Evidencia Local Obligatoria:** Todos los borradores exitosos se almacenan en la carpeta local `output/localdraft_<id_entrada>/` conteniendo:
    *   `post.md`: Texto plano del post generado.
    *   `diagnostico.json`: Datos del diagnóstico editorial.
    *   `salida_v1.json`: Serialización completa del lote `SalidaLocalDraft`.
    *   `manifest.json`: Manifiesto con la firma y lista de archivos generados.
*   **Sanitización Absoluta:** No se debe escribir en disco ningún archivo (incluyendo los campos de texto libre como `motivo`, `comentarios` o `ajustes_recomendados`) que contenga datos PII, secretos, credenciales o rutas locales absolutas.
*   **Pruebas Offline:** El sistema opera en modo `dry_run` con `localdraft` (LocalDraftPublisher), evitando cualquier llamada real a las APIs externas y garantizando un flujo 100% offline y seguro.
