# Plan de saneamiento documental

Fecha: 2026-07-08
Motivo: alinear la documentación del repositorio con el producto que realmente se quiere construir.

## 1. Problema actual

La documentación del repositorio ya no cumple una única función clara.

Ahora mismo mezcla:

- visión inicial del producto;
- restricciones temporales de implementación;
- decisiones técnicas candidatas;
- gobernanza del trabajo del agente;
- estado real del repositorio;
- dirección futura deseada por el usuario.

La consecuencia es que hoy no existe una única fuente de verdad estable.

Eso genera cuatro riesgos:

1. Se toman decisiones sobre documentos que ya no representan el producto deseado.
2. Se confunde lo que es alcance actual con lo que fue una restricción temporal.
3. Se protege el rumbo antiguo aunque el producto ya haya cambiado.
4. Se dificulta distinguir entre documentación vigente, táctica e histórica.

## 2. Objetivo del saneamiento

Dejar la documentación en un estado donde sea fácil responder estas preguntas:

1. Qué producto queremos construir realmente.
2. Qué parte del repositorio actual sí sirve para ese producto.
3. Qué restricciones siguen vigentes y cuáles fueron temporales.
4. Qué documentos son fuente de verdad.
5. Qué documentos son históricos y no deben gobernar nuevas decisiones.

## 3. Criterio rector

El saneamiento no debe empezar por detalles formales.

Debe empezar por la jerarquía de verdad:

```text
visión de producto
-> alcance
-> roadmap/fases
-> decisiones técnicas
-> reglas operativas del agente
-> anexos, gates, skills futuras, mapas
```

Si se actualiza en otro orden, volverán a aparecer contradicciones.

## 4. Clasificación propuesta por archivo

### 4.1 Reescribir primero

Estos documentos tienen demasiado peso sobre la interpretación global del proyecto y hoy no están alineados con el nuevo objetivo:

#### `docs/00_brief_arquitectura_pre_codigo.md`

Problema:

- define el producto como publicador automático desde audio para LinkedIn;
- no refleja el objetivo portable y agnóstico;
- trata audio y LinkedIn como identidad del sistema.

Acción:

- reescritura completa.

Nuevo rol:

- visión de producto vigente.

#### `docs/01_alcance_si_no.md`

Problema:

- fija un alcance muy centrado en LinkedIn como producto;
- deja fuera demasiado pronto capacidades que ahora parecen parte de la visión real;
- mezcla límites de V1 con identidad estructural del sistema.

Acción:

- reescritura completa.

Nuevo rol:

- alcance del nuevo MVP portable.

#### `docs/05_fases_implementacion.md`

Problema:

- responde a un roadmap del producto antiguo;
- ordena la implementación alrededor de audio + LinkedIn;
- no coincide con el plan de recuperación basado en utilidad inmediata.

Acción:

- reescritura completa.

Nuevo rol:

- roadmap de implementación realista por valor.

#### `docs/09_plan_implementacion_post_planeacion.md`

Problema:

- hoy es el documento más cercano al estado real del repo;
- pero sigue anclado al marco LinkedIn V1 y al cierre de fases anteriores;
- no alcanza todavía la nueva visión portable.

Acción:

- reescritura fuerte o reemplazo controlado.

Nuevo rol:

- plan de transición entre el repo actual y el nuevo producto.

#### `AGENTS.md`

Problema:

- hoy congela reglas pensadas para un momento anterior del proyecto;
- mezcla control operativo del agente con alcance de producto;
- impone límites que ya pueden bloquear el nuevo rumbo.

Acción:

- reescritura controlada.

Nuevo rol:

- marco operativo actualizado para trabajar sobre el nuevo producto sin perder seguridad.

### 4.2 Mantener, pero revisar después

Estos documentos pueden seguir existiendo, pero deben revisarse cuando la nueva visión ya esté fijada:

#### `docs/02_contrato_entrada_contenido.md`

Motivo:

- seguramente necesitará ampliarse para soportar más tipos de fuente;
- no conviene tocarlo antes de definir bien la nueva entrada del sistema.

Acción:

- revisión posterior.

#### `docs/03_contrato_perfil_narrativo.md`

Motivo:

- probablemente sigue siendo útil;
- puede necesitar ajustes para un sistema multicanal o multimodal.

Acción:

- revisión posterior.

#### `docs/04_contrato_salida.md`

Motivo:

- puede mantenerse parcialmente;
- habrá que revisar si la salida ya no es solo LocalDraft LinkedIn.

Acción:

- revisión posterior.

#### `docs/06_contrato_calidad_post_linkedin.md`

Motivo:

- sigue siendo útil si LinkedIn continúa como primer canal operativo;
- deja de ser documento universal si el sistema pasa a ser portable.

Acción:

- mantener por ahora;
- renombrar o especializar después si hace falta.

### 4.3 Convertir en anexo histórico o derivado

Estos documentos no deberían seguir gobernando el rumbo principal:

#### `docs/07_gates_futuros_v1.md`

Motivo:

- es documentación de planeación secundaria;
- depende del rumbo principal y no debe definirlo.

Acción:

- mantener como anexo;
- revisar solo después de reescribir visión y alcance.

#### `docs/08_skills_producto_linkedin_futuras.md`

Motivo:

- está directamente acoplado a una visión futura orientada a LinkedIn;
- puede quedar obsoleto si el producto pasa a ser portable y modular.

Acción:

- pasar a estado histórico o reetiquetar como referencia anterior.

#### `docs/10_mapa_tecnico_contexto_pipeline_offline.md`

Motivo:

- describe bien el estado del sistema construido;
- es útil como fotografía técnica;
- no debe confundirse con visión de producto.

Acción:

- mantener como mapa técnico del estado actual;
- marcar explícitamente que no define el destino del producto.

#### `docs/Control/Chat Deep Progrlama Linkedin2.md`

Motivo:

- sirve como insumo de discusión;
- no debe considerarse documento rector.

Acción:

- mantener fuera de la cadena principal de verdad.

### 4.4 Revaluar como decisión técnica, no como verdad de producto

#### `docs/architecture/ADR-000_Decisiones_Tecnicas_Base.md`

Motivo:

- contiene decisiones útiles;
- pero hoy mezcla decisiones técnicas con una definición de producto antigua;
- puede tener partes aceptadas que siguen sirviendo y otras que deben pasar a reevaluación.

Acción:

- no reescribir primero;
- revisar después de redefinir visión y alcance;
- probablemente emitir un nuevo ADR en vez de forzar este a representar dos etapas históricas.

## 5. Nuevo orden recomendado de documentación

Orden propuesto para el saneamiento:

1. Documento nuevo de visión del producto portable y agnóstico.
2. Reescritura de `docs/00_brief_arquitectura_pre_codigo.md`.
3. Reescritura de `docs/01_alcance_si_no.md`.
4. Reescritura de `docs/05_fases_implementacion.md`.
5. Reescritura o reemplazo de `docs/09_plan_implementacion_post_planeacion.md`.
6. Actualización de `AGENTS.md`.
7. Revisión de contratos `02`, `03`, `04`, `06`.
8. Revisión del ADR base y creación de nuevo ADR si corresponde.
9. Revisión de anexos `07`, `08`, `10`.

## 6. Estrategia de ejecución

### Etapa A — Fijar la nueva verdad principal

Tarea 0 de transición:

- actualizar `AGENTS.md` para que la documentación núcleo vigente prevalezca sobre documentos técnicos o históricos en conflicto;
- mantener intactas las reglas de seguridad, PII, secretos y acciones reales de riesgo;
- evitar que reglas antiguas de producto saboteen el nuevo rumbo.

Entregables:

- un documento de visión del producto;
- una definición clara del nuevo MVP;
- una declaración explícita de que el sistema es portable y agnóstico.

Resultado esperado:

- ya no habrá que inferir el producto desde conversaciones o documentos de control.

### Etapa B — Reordenar la documentación núcleo

Entregables:

- `docs/00` alineado;
- `docs/01` alineado;
- `docs/05` alineado;
- `docs/09` alineado.

Resultado esperado:

- cualquier lector nuevo entenderá qué se quiere construir, qué entra, qué no entra y en qué orden se implementa.

### Etapa C — Reajustar gobernanza y decisiones técnicas

Entregables:

- `AGENTS.md` actualizado;
- ADR revisado;
- contratos revisados si la nueva visión lo exige.

Resultado esperado:

- la gobernanza deja de bloquear el producto correcto y pasa a protegerlo.

### Etapa D — Limpiar anexos y residuos

Entregables:

- documentos históricos marcados como tales;
- anexos secundarios alineados;
- archivos de control no confundibles con fuente de verdad.
- validación explícita entre visión vigente y fotografía técnica.

Resultado esperado:

- baja fricción documental y menos ambigüedad para futuras decisiones.

## 7. Propuesta concreta de estados

### Estado `vigente`

Deberían quedar aquí:

- visión del producto;
- alcance;
- roadmap;
- plan de transición;
- reglas operativas del agente;
- ADRs activos.

### Estado `derivado`

Deberían quedar aquí:

- contratos;
- gates;
- skills futuras;
- mapas técnicos.

### Estado `histórico`

Deberían quedar aquí:

- documentos que describen un rumbo anterior;
- chats de control;
- planes descartados;
- anexos que ya no gobiernan decisiones.

## 8. Riesgos a evitar durante el saneamiento

1. Reescribir todo sin fijar antes la nueva visión.
2. Cambiar el wording sin cambiar realmente la jerarquía de verdad.
3. Mantener documentos antiguos como si siguieran vigentes.
4. Actualizar el ADR antes del alcance.
5. Intentar sanear documentación y arquitectura en el mismo movimiento.
6. Dejar que `AGENTS.md` siga bloqueando un rumbo que la documentación núcleo ya corrigió.
7. Permitir que `docs/10` o un mapa técnico se lean como si fueran la visión de producto.

## 9. Verificación mínima de consistencia

Antes de cerrar el saneamiento documental, debe ejecutarse este checklist manual:

1. `docs/00` y `docs/01` no se contradicen entre sí.
2. `docs/05` implementa el alcance descrito en `docs/01`.
3. `docs/09` describe el puente entre el estado real del repo y la visión nueva.
4. `AGENTS.md` remite a la documentación núcleo vigente y no al rumbo antiguo.
5. `docs/10` queda marcado explícitamente como fotografía técnica.
6. Contratos, ADRs y anexos derivados incluyen nota de transición si todavía no fueron reescritos.

## 10. Recomendación práctica inmediata

El siguiente paso más útil no es editar cinco archivos a la vez.

El siguiente paso útil es este:

1. Crear o consolidar un documento corto de visión del producto portable.
2. Usarlo como base para reescribir `docs/00`.
3. Después reescribir `docs/01` y `docs/05`.
4. Con eso ya sí actualizar `docs/09` y `AGENTS.md`.

## 11. Resultado esperado del saneamiento

Cuando este saneamiento esté bien hecho, el repositorio debería poder leerse así:

```text
qué producto es
-> qué alcance tiene
-> cómo se implementa
-> qué decisiones técnicas lo sostienen
-> qué reglas operativas lo protegen
```

Si no logramos esa lectura simple, la documentación seguirá siendo parte del problema en vez de parte de la solución.
