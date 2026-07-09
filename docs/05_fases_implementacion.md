# 05 — Fases de implementación

Este documento define el roadmap de implementación por valor del producto actual.

La regla principal es:

```text
primero flujo útil
después ampliación de fuentes
después preparación/publicación
después visuales y expansión
```

## Fase 1 — Flujo útil textual

**Objetivo:** Conseguir que una persona entregue una idea en texto y reciba un borrador de LinkedIn realmente usable.

### Flujo objetivo

```text
texto manual
-> normalización mínima
-> extracción de idea e intención
-> generación de pieza
-> validación
-> aprobación humana
-> LocalDraft listo
```

### Debe incluir

* reutilización de contratos y validadores actuales;
* uso de `LocalDraftPublisher` o salida equivalente;
* control de PII, rutas, secretos y publicabilidad;
* aprobación humana operativa.

### No debe incluir todavía

* audio real;
* publicación real;
* visuales;
* omnicanal real;
* UI completa.

## Fase 2 — Aprobación humana usable

**Objetivo:** Convertir la aprobación humana en una operación real y no solo en un estado de datos.

Puede resolverse inicialmente con:

* CLI simple;
* interfaz de agente/chat;
* flujo local interactivo.

**Resultado esperado:** un revisor puede aprobar, rechazar o pedir ajustes sin romper el flujo.

## Fase 3 — Ampliación de entradas

**Objetivo:** Añadir nuevas fuentes sobre el flujo útil ya validado.

Orden recomendado:

1. audio con transcripción;
2. transcripciones de video;
3. documentos o borradores previos;
4. otras materias primas normalizables.

**Regla:** ninguna nueva fuente debe entrar si el flujo textual base todavía no aporta valor claro.

## Fase 4 — Preparación de publicación

**Objetivo:** Llegar a un `dry_run` realista de salida externa sin perder el control local.

Debe incluir:

* payload de salida claro;
* adaptador desacoplado;
* evidencia útil;
* credenciales fuera del repositorio;
* bloqueo automático ante FAIL editorial o falta de aprobación.

**Resultado esperado:** el sistema puede preparar publicación sin ejecutar todavía una publicación real descontrolada.

## Fase 5 — Publicación real controlada

**Objetivo:** Permitir programación o publicación real solo cuando el flujo local, la revisión y el `dry_run` ya estén consolidados.

Condiciones mínimas:

* aprobación humana explícita;
* adaptador desacoplado;
* validaciones activas;
* trazabilidad suficiente;
* política de secretos clara.

## Fase 6 — Visuales, feedback y expansión

**Objetivo:** Extender el sistema una vez el núcleo textual ya sirve de verdad.

Puede incluir:

* carruseles o piezas visuales;
* analítica básica;
* aprendizaje sobre formatos ganadores;
* nuevos canales;
* mejora de interfaz.

## Regla transversal

Toda fase debe responder a esta pregunta:

```text
¿esto acerca el sistema a una operación útil real o solo añade estructura?
```

Si la respuesta es “solo añade estructura”, no tiene prioridad.
