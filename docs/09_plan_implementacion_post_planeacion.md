# 09 — Plan de transición del repositorio al producto deseado

## 1. Punto de partida real

El repositorio actual no está vacío ni fallido.

Tiene una base útil ya construida:

* contratos en `src/linkedin_content_system/contracts/`;
* validadores de seguridad y publicabilidad;
* `ModelAdapter` y `MockModelAdapter`;
* generación mock de post;
* `LocalDraftPublisher`;
* pipeline offline determinista con contexto;
* una suite de tests amplia y estable.

También tiene un desbalance claro:

* está más maduro en gobernanza, trazabilidad y control offline;
* está menos maduro en flujo de producto útil, entrada flexible, aprobación operativa y salida real reutilizable.

## 2. Qué se conserva

Estas piezas deben tratarse como activos reutilizables:

* contratos base;
* validadores de privacidad, estructura, publicabilidad y trazabilidad;
* `LocalDraftPublisher`;
* adaptador mock;
* evidencia local existente;
* tests como red de seguridad.

## 3. Qué se congela

Hasta consolidar el nuevo flujo útil, deben congelarse:

* expansión del pipeline de contexto si no desbloquea producto;
* nuevas skills de gobernanza;
* nuevas capas documentales no esenciales;
* omnicanal real simultáneo;
* visuales como requisito obligatorio;
* analítica avanzada;
* multiusuario;
* integraciones reales externas adelantadas.

## 4. Qué se reorienta

El esfuerzo debe moverse hacia:

1. flujo textual útil;
2. aprobación humana usable;
3. salida local lista;
4. ampliación de fuentes;
5. preparación de publicación;
6. publicación real controlada.

## 5. Etapas operativas de transición

### Etapa A — Reordenar la verdad documental

Objetivo:

* dejar clara la nueva visión del producto;
* corregir alcance, fases y reglas operativas;
* separar visión de fotografía técnica.

### Etapa B — Consolidar el flujo textual útil

Objetivo:

```text
texto manual -> post usable -> revisión -> aprobación -> LocalDraft
```

Qué implica:

* reutilizar componentes existentes;
* cerrar lagunas operativas;
* medir éxito por utilidad, no por fases históricas.

### Etapa C — Añadir entrada flexible

Objetivo:

* sumar audio, transcripciones y otras fuentes sin rediseñar el núcleo.

### Etapa D — Preparar publicación

Objetivo:

* consolidar una frontera portable de publicación;
* generar payloads y `dry_run` desacoplados;
* simular una salida externa verificable sin publicar realmente;
* dejar preparada la evolución futura hacia un publisher genérico y después Metricool en modo `dry_run`.

### Etapa E — Publicación real y crecimiento

Objetivo:

* habilitar publicación real solo cuando el sistema ya sea útil, seguro y mantenible;
* permitir la secuencia futura `publisher genérico -> external dry_run -> Metricool dry_run -> IA real -> audio/transcripción -> otros canales -> visuales/analítica`.

## 6. Qué no debe repetirse

No debe repetirse este patrón:

```text
documentar mucho
-> cerrar fases internas
-> reforzar control
-> seguir sin resolver el flujo útil principal
```

## 7. Nuevo criterio de éxito

El repositorio avanza bien si una persona puede:

1. entregar una idea real;
2. recibir una pieza útil;
3. revisarla con confianza;
4. aprobarla;
5. guardarla o prepararla para salida.

Si eso no mejora, el sistema puede estar ordenado pero no alineado.
