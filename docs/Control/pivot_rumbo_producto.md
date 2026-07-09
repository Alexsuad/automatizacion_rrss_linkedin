# Pivot de rumbo del producto

Fecha: 2026-07-08
Base revisada: estado real del repositorio en `e5bd839`

## 1. Verdad central

El problema no es que el repositorio esté "mal programado".

El problema es que el repositorio actual está optimizado para:

- gobernanza,
- validación,
- trazabilidad,
- simulación offline,
- protección del flujo,

y no para entregar cuanto antes el producto útil que se esperaba:

```text
entrada real -> generación útil -> revisión útil -> aprobación simple -> borrador/publicación
```

La consecuencia es directa:

- sí existe trabajo reutilizable;
- sí existe avance técnico real;
- pero el valor de producto entregado hoy no coincide con la expectativa que motivó el proyecto.

En términos prácticos: se construyó más arnés que vehículo.

## 2. Qué producto sí se necesita

El producto que hace falta recuperar no es "más gobernanza".

Es un flujo operativo que permita:

1. Recibir una idea en texto y, después, también audio.
2. Convertir esa idea en un post de LinkedIn usable.
3. Revisarlo con controles mínimos reales, no con sobrecarga documental.
4. Pedir aprobación humana simple.
5. Guardarlo como borrador listo o prepararlo para publicación.

Versión mínima útil:

```text
texto manual
-> generación de post
-> validación básica
-> aprobación humana
-> LocalDraft listo para uso
```

Versión siguiente:

```text
audio
-> transcripción
-> generación de post
-> validación básica
-> aprobación humana
-> borrador/publicación preparada
```

## 3. Qué parte del repo sí sirve

Estas piezas sí aportan a un pivot pragmático y conviene conservarlas:

### 3.1 Contratos base reutilizables

- `src/linkedin_content_system/contracts/`
- `src/linkedin_content_system/contracts/salida.py`
- `src/linkedin_content_system/contracts/editorial.py`
- `src/linkedin_content_system/contracts/trazabilidad.py`

Sirven porque ya modelan parte de la entrada, la salida, la aprobación y el diagnóstico.

### 3.2 Validaciones útiles de verdad

- `src/linkedin_content_system/validators/privacidad.py`
- `src/linkedin_content_system/validators/publicacion.py`
- `src/linkedin_content_system/validators/trazabilidad.py`
- `src/linkedin_content_system/validators/estructural.py`

No resuelven el producto, pero sí evitan publicar cosas inseguras o incoherentes.

### 3.3 Mock y flujo local aprovechables

- `src/linkedin_content_system/ai/ports.py`
- `src/linkedin_content_system/ai/mock_adapter.py`
- `src/linkedin_content_system/use_cases/generar_post_mock.py`
- `src/linkedin_content_system/use_cases/generar_borrador_local.py`
- `src/linkedin_content_system/publishers/localdraft.py`

Esta base permite avanzar rápido hacia una versión útil sin tirar todo.

### 3.4 Suite de tests como red de seguridad

La suite actual pasó en este estado con:

```text
315 passed in 0.94s
```

Eso no valida producto, pero sí da una base segura para reorientar sin romper todo a ciegas.

## 4. Qué parte fue desvío para la necesidad actual

No significa que esté "mal" técnicamente.

Significa que, para la necesidad actual, consumió tiempo sin acercar suficiente valor.

### 4.1 Sobredesarrollo de gobernanza

Se invirtió demasiado en:

- fases,
- mapas,
- gates futuros,
- skills de control,
- anticontaminación expandida,
- contratos alrededor del proceso,

cuando todavía faltaba el flujo útil principal.

### 4.2 Pipeline de contexto más maduro que el producto

Las fases de contexto y control quedaron más desarrolladas que:

- entrada real,
- generación útil,
- interacción de aprobación,
- salida operativa,
- preparación real de publicación.

Eso es una inversión desbalanceada respecto al objetivo del usuario.

### 4.3 Simulación más cerrada que el caso real

Hoy el sistema protege muy bien el modo offline simulado, pero todavía no resuelve bien:

- cómo entra el contenido real,
- cómo se redacta con valor,
- cómo se aprueba de forma usable,
- cómo se prepara una salida que sirva en operación diaria.

## 5. Qué congelar ya

Para recuperar foco, conviene congelar temporalmente todo lo que no acerque al flujo útil mínimo:

- nuevas skills de gobernanza;
- nuevas subfases documentales;
- expansión de `ContextoTrabajo` salvo bug real;
- nuevas evidencias o manifests no imprescindibles;
- omnicanal;
- visuales;
- analítica;
- UI completa;
- integraciones reales externas si antes no existe flujo útil local.

La regla operativa debe ser:

```text
Si no acerca al primer flujo útil para producir un post usable, se congela.
```

## 6. Qué cortar conceptualmente

Hay que abandonar estas inercias:

### 6.1 "Primero cerrar toda la arquitectura"

No.

Primero hay que conseguir una versión que sirva.

### 6.2 "Más contratos siempre mejor"

No.

Los contratos solo deben existir cuando reducen un riesgo real o simplifican una integración inmediata.

### 6.3 "El éxito actual del repo demuestra que vamos bien"

No necesariamente.

Tests verdes, contratos limpios y documentación abundante no compensan un desvío de producto.

## 7. Nuevo plan mínimo de recuperación

Este plan está ordenado por valor, no por perfección arquitectónica.

### Etapa 1 — Recuperar el caso de uso mínimo

Objetivo:

```text
texto manual -> post usable -> aprobación -> LocalDraft
```

Debe incluir:

- entrada manual simple;
- generación de post con adaptador mock o proveedor real controlado;
- validación editorial y de seguridad mínima;
- aprobación humana simple;
- salida local clara y usable.

No debe incluir todavía:

- audio real;
- Metricool real;
- visuales;
- omnicanal;
- UI grande.

### Etapa 2 — Hacer útil la aprobación humana

Objetivo:

- dejar de tratar la aprobación solo como dato;
- convertirla en una interacción operativa real.

Puede resolverse primero con:

- CLI sencilla, o
- interacción por agente/chat,

pero debe existir como paso usable de verdad.

### Etapa 3 — Incorporar entrada de audio

Objetivo:

```text
audio -> transcripción -> mismo flujo ya útil
```

La transcripción no debe entrar antes de que el flujo textual ya esté funcionando y aportando valor.

### Etapa 4 — Preparar publicación, no necesariamente publicar

Objetivo:

- payload claro;
- borrador listo;
- estructura para dry run;
- evidencia útil, no burocrática.

Si la publicación real entra antes de que exista un flujo local útil, se repite el mismo error de priorización.

## 8. Orden de prioridades corregido

Orden recomendado:

1. Flujo textual útil.
2. Aprobación humana usable.
3. Salida local lista.
4. Audio/transcripción.
5. Dry run de publicación.
6. Publicación real controlada.

Orden no recomendado:

1. Más gobernanza.
2. Más documentación estructural.
3. Más contexto.
4. Más fases abstractas.
5. Omnicanal temprano.

## 9. Decisión de producto que hay que tomar

La decisión pendiente no es técnica.

Es esta:

```text
¿El proyecto se corrige para entregar cuanto antes un sistema útil de LinkedIn V1,
o se redefine formalmente como plataforma portable de contenido?
```

Mientras esa decisión no se haga explícita, el equipo puede seguir construyendo bien cosas que no sirven.

## 10. Recomendación ejecutiva

La recomendación pragmática es:

1. No tirar el repo.
2. No seguir expandiendo gobernanza.
3. Reusar contratos, validadores, mock y LocalDraft.
4. Reorientar todo el esfuerzo al primer flujo útil real.
5. Medir avance por utilidad operativa, no por cantidad de fases cerradas.

## 11. Criterio de éxito nuevo

El nuevo criterio de éxito no debe ser:

- "cerramos otra fase",
- "añadimos otra skill",
- "el documento quedó más completo".

Debe ser:

```text
una persona puede meter una idea real
y obtener un post de LinkedIn que realmente le sirva.
```

Si eso no pasa, el proyecto sigue desalineado aunque esté prolijo por dentro.
