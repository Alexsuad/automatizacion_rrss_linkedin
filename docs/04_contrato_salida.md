# 04 — Contrato de salida del proceso

> [!IMPORTANT]
> Este documento describe la salida del flujo actualmente implementado y el contrato mínimo que debe respetar cualquier salida futura.
> 
> Hoy la implementación real gira alrededor de `LocalDraftPublisher` y del primer canal operativo.
> Eso no convierte `LocalDraft` en la única salida permanente del sistema ni hace que LinkedIn sea la identidad total del producto.

## 1. Propósito del documento

Este documento define la estructura mínima de salida que el sistema debe producir una vez completa el flujo de generación, validación y aprobación.

Su objetivo es separar dos cosas:

* la **salida conceptual del sistema**, que debe seguir siendo portable dentro del Portable Content Publisher;
* la **salida hoy implementada**, que actualmente se persiste como borrador local seguro.

## 2. Principio rector

Toda salida del sistema debe representar una pieza:

* generada o adaptada desde una entrada válida;
* revisada editorialmente;
* evaluada en trazabilidad y seguridad;
* asociada a una aprobación humana;
* lista para persistirse, revisarse o prepararse para publicación.

La primera implementación concreta de ese principio es `SalidaLocalDraft`.

## 3. Salidas previstas por contrato

### 3.1 Salida implementada actualmente

| Tipo de salida | Estado actual | Descripción |
| :--- | :--- | :--- |
| `localdraft` | Implementada | Borrador local persistido en modo seguro y `dry_run`. |

### 3.2 Salidas previstas a futuro

| Tipo de salida | Estado | Descripción |
| :--- | :--- | :--- |
| `payload_publicacion` | Futura | Estructura preparada para adaptadores externos desacoplados. |
| `external_dry_run` | Futura | Simulación local de salida externa preparada sin publicar realmente. |
| `programacion_controlada` | Futura | Salida lista para programación real tras aprobación explícita. |
| `pieza_por_canal` | Futura | Variante específica por canal cuando el sistema amplíe adaptadores y salidas. |

## 4. Estructura conceptual mínima de salida

Independientemente del adaptador o del canal, una salida del sistema debe poder expresar, como mínimo, esta estructura conceptual:

```json
{
  "pieza": {
    "canal": "linkedin",
    "texto": "Contenido final aprobado y listo para persistirse o prepararse"
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
    "motivo": "El contenido cumple con la coherencia esperada",
    "ajustes_recomendados": null,
    "bloqueos_criticos": []
  },
  "diagnostico_trazabilidad": {
    "estado": "PASS",
    "hallazgos": [],
    "resumen": "No se detectaron hallazgos sensibles de trazabilidad"
  },
  "aprobacion_humana": {
    "estado": "aprobado",
    "aprobado_por": "Revisor Responsable",
    "fecha_aprobacion": "2026-07-08T12:00:00Z",
    "comentarios": "Aprobado sin cambios",
    "tipo_aprobacion": "simple",
    "revision_reforzada_requerida": false,
    "motivo_revision_reforzada": null
  },
  "modo_salida": "dry_run",
  "adaptador_activo": "localdraft",
  "estado_salida": "borrador_local",
  "estado_publicabilidad": "publicable",
  "fecha_objetivo_sugerida": "2026-07-10T09:00:00Z"
}
```

## 5. Relación con la implementación actual

Hoy la representación concreta ya implementada es `SalidaLocalDraft`, que:

* persiste un borrador local;
* opera en `dry_run`;
* usa `localdraft` como adaptador activo;
* no implica publicación real ni programación externa.

Por tanto:

* el contrato actual debe seguir siendo compatible con `SalidaLocalDraft`;
* pero no debe impedir futuras salidas desacopladas.

## 6. Matriz de publicabilidad editorial y gates

La persistencia de la salida actual queda controlada por la validación determinista de:

* diagnóstico editorial;
* diagnóstico de trazabilidad;
* aprobación humana.

Reglas operativas actuales:

* **PASS + trazabilidad PASS + aprobación simple:** `publicable`
* **PASS + trazabilidad WARN + aprobación reforzada:** `publicable`
* **WARN + trazabilidad PASS + aprobación reforzada:** `publicable`
* **WARN + trazabilidad WARN + aprobación reforzada:** `publicable`
* **WARN sin aprobación reforzada:** `requiere_revision`
* **FAIL editorial o FAIL de trazabilidad:** `rechazado_editorial`
* **Sin aprobación:** `no_publicable`
* **Sin diagnóstico de trazabilidad:** `no_publicable`

Estas reglas describen el comportamiento actual antes de persistir un borrador local listo.

## 7. Evidencia local y seguridad

La primera forma de salida persistida del sistema sigue siendo evidencia local segura.

En la implementación actual, un `localdraft` exitoso genera:

* `post.md`
* `diagnostico.json`
* `salida_v1.json`
* `manifest.json`

Reglas:

1. No se debe escribir PII, secretos, credenciales ni rutas locales absolutas en disco.
2. Ninguna salida debe considerarse publicable si no pasó por validación y aprobación.
3. La persistencia local debe servir como base de validación antes de cualquier integración real externa.

## 8. Qué no afirma este documento

Este documento no afirma que:

* `LocalDraft` sea la única salida válida del producto;
* LinkedIn sea el único canal posible del sistema;
* la salida actual ya equivalga a publicación real;
* el contrato de salida futuro esté cerrado para otros adaptadores o canales.
* la fase de `external_dry_run` implique una publicación real o una dependencia de proveedor real.

## 9. Regla de trabajo

La evolución correcta sigue siendo:

```text
primero definir salida mínima portable
después mantener compatibilidad con la salida actual
después adaptar ADR y decisiones técnicas
después tocar código
```
