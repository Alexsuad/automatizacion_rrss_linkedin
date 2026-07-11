# Plan 007: Validacion real del producto textual

> **Executor instructions**: Ejecutar este plan solo sobre la linea base publicada en `main` y tomando como referencia tecnica el commit `3a991b3`. No implementar nada fuera de alcance, no publicar contenido real y no usar credenciales fuera del entorno local del ejecutor.

## Estado de partida

- **Rama base**: `main`
- **Linea base tecnica**: commit `3a991b3` (`Añadir benchmark editorial y preparación de smoke real`)
- **Commit de ejecucion**: se definira al cerrar documentalmente este plan y sera el commit identificable desde el que se ejecute la etapa
- **Suite base**: `401` tests pasando
- **Plan 006**: `IMPLEMENTED_PENDING_REAL_SMOKE`
- **Misiones 1-3**: cerradas y ya congeladas en Git
- **Flujo vigente**: generacion textual con ciclo editorial local; el smoke real debe usar la sesion editorial pendiente y no el flujo antiguo con aprobacion anticipada

## Estados del plan

- `TODO`: plan registrado y todavia no ejecutado
- `IN PROGRESS`: ejecucion documental o tecnica en curso sin smoke concluido
- `DONE`: smoke real satisfactorio, benchmark y ciclos de feedback completados con evidencia suficiente
- `BLOCKED`: la etapa no puede continuar sin tocar alcance prohibido, sin autorizacion o sin credencial local valida

## Objetivo

Demostrar con evidencia real y controlada que el sistema puede producir una pieza textual fiel, revisable y aprobable con un proveedor real, sin publicar nada y sin romper el modo seguro offline.

## Alcance

- una sola ruta real detras de `ModelAdapter`
- un proveedor y un modelo elegidos explicitamente
- una credencial solo local y nunca versionada
- smoke real controlado con una sola llamada
- benchmark real con cinco piezas sinteticas
- dos ciclos `v1 -> feedback -> v2`
- evaluacion separada entre validacion estructural, revision editorial y decision humana

## Fuera de alcance

- publicacion real o `dry_run` externo
- Metricool, MCP, audio, imagenes, visuales y analitica
- cambios en `publishers/`; esta etapa puede consumir su comportamiento existente, pero no debe depender de modificarlos
- nuevas dependencias o nuevos proveedores fuera de la ruta ya aprobada
- uso de datos reales de clientes o credenciales versionadas
- cambios en `docs/Instrucciones/`

## Separacion entre implementacion y ejecucion real

- la implementacion necesaria para habilitar cada fase debe cerrarse y validarse antes de cualquier lote real
- ninguna llamada real debe usarse para descubrir fallos basicos que podian detectarse con tests o revision local
- antes de cada lote real debe existir:
  - tests relevantes en verde
  - commit local o remoto identificable con el codigo exacto evaluado
  - revision humana del alcance, presupuesto y riesgo

## Fase 4.0 - Autorizacion y linea operativa

- elegir explicitamente proveedor y modelo antes de cualquier llamada
- confirmar autorizacion explicita para usar red y credencial local
- la URL del proveedor se inyecta por entorno y no se hardcodea; para Ollama
  desde WSL se usa `OLLAMA_API_BASE`
- fijar un presupuesto inicial maximo de `8` llamadas:
  - `1` smoke
  - `5` benchmark
  - `2` feedback
- cualquier evaluador-modelo queda fuera de ese presupuesto y requiere autorizacion aparte
- registrar antes de ejecutar: commit usado, proveedor, modelo, presupuesto aprobado y responsable de la revision humana

## Fase 4.1 - Smoke real controlado

- ejecutar una sola llamada real
- usar el ciclo editorial nuevo descrito en `benchmarks/editorial/runbook_smoke_real.md`
- generar una sesion editorial `pendiente`
- no crear `LocalDraft`
- no publicar
- no aprobar por adelantado
- criterio exacto de `PASS` del smoke:
  - una sola llamada al proveedor
  - respuesta no vacia
  - sesion editorial pendiente creada en la ruta esperada
  - sin `LocalDraft`
  - sin publicacion
  - sin secretos en stdout, stderr o evidencia
  - finalizacion dentro del timeout configurado
- si pasa:
  - registrar evidencia
  - cerrar Plan 006 como `DONE`
  - mantener Plan 007 abierto
- si falla:
  - conservar Plan 006 abierto
  - registrar evidencia del bloqueo sin repetir llamadas innecesarias

## Fase 4.2 - Perfil narrativo runtime completo

- completar el perfil narrativo runtime antes de evaluar voz seriamente
- registrar en evidencia si el perfil fue encontrado o si hubo fallback
- no presentar un fallback como si fuera voz real del cliente
- incluir como minimo:
  - tono base
  - tono prohibido
  - expresiones propias
  - palabras o frases a evitar
  - ejemplos `si suena`
  - ejemplos `no suena`
  - limites de inferencia

## Fase 4.3 - Contrato de evaluacion editorial

- separar explicitamente:
  - validacion estructural automatica
  - revision editorial por modelo
  - decision humana final
- el modelo nunca puede autoaprobar una pieza
- la salida de revision editorial debe poder quedar en `WARN` aunque la validacion estructural sea `PASS`

## Fase 4.4 - Benchmark real de cinco piezas

- ejecutar benchmark real con cinco piezas sinteticas
- el runner debe aceptar `ModelAdapter` inyectable
- `controlled` sigue siendo el default
- el proveedor real solo se usa mediante autorizacion explicita
- antes de ejecutar el benchmark real debe existir:
  - tests relevantes en verde
  - commit identificable del codigo evaluado
  - revision humana del lote real y del presupuesto restante
- aplicar criterios operables y no ambiguos para:
  - fidelidad
  - voz
  - naturalidad
  - publicabilidad
  - ajustes menores
  - invencion critica
- definiciones operables:
  - `invencion critica`: afirmacion falsa o no respaldada por la entrada, el perfil o el feedback, con riesgo editorial o reputacional claro
  - `ajustes menores`: cambios de estilo, orden, longitud o pulido que no exigen reescribir la tesis ni la estructura central
  - `reescritura completa`: la pieza no puede aprovecharse sin rehacer tesis, estructura y cierre desde cero
  - `cercana a publicable`: requiere solo ajustes menores despues de revision humana, no presenta riesgos estructurales ni invenciones criticas y cumple como minimo:
    - fidelidad `>= 4/5`
    - voz `>= 3/5`
    - naturalidad `>= 3/5`
    - publicabilidad `>= 4/5`
- gate inicial recomendado:
  - `4 de 5` piezas aprovechables sin reescritura completa
  - `0` invenciones criticas
  - `0` fugas de datos

## Fase 4.5 - Dos ciclos de mejora guiada

- seleccionar dos piezas del benchmark
- ejecutar dos regeneraciones de feedback, una por cada una de dos piezas seleccionadas
- cada llamada de feedback corresponde a `v1 -> feedback -> v2` sobre una pieza
- comparar si la nueva version mejora al menos una dimension editorial
- no aceptar mejoras que degraden fidelidad o seguridad

## Fase 4.6 - Decision de expansion

Tomar una decision basada en evidencia:

- mejorar calidad textual si la mayoria requiere reescritura importante
- avanzar a audio solo si el flujo textual ya aporta valor estable
- avanzar a `dry_run` externo solo si calidad, estados y aprobacion humana ya son consistentes

## Gates tecnicos

- suite completa en verde antes y despues de cambios necesarios
- `compileall` en verde
- sin secretos versionados
- sin rutas locales absolutas nuevas
- sin cambios en `publishers/`
- una sola llamada en el smoke y maximo `8` llamadas en toda la etapa salvo autorizacion adicional

## Gates de producto

- smoke real funcional sin publicacion
- benchmark con evidencia humana y tecnica trazable
- voz evaluada sobre perfil narrativo suficiente, no sobre fallback opaco
- feedback con mejora observable en dos casos
- decision final sustentada por evidencia, no por intuicion

## Evidencias requeridas

- commit o rango de commits evaluados
- proveedor y modelo usados
- numero total de llamadas realizadas
- consumo o coste cuando el proveedor lo exponga
- hashes de fixtures y hashes de salida
- estado del smoke
- resultados del benchmark
- revision humana identificable
- clasificacion de hallazgos: tecnico, editorial y de seguridad

## Riesgos

- confundir smoke tecnico con calidad de producto
- medir voz con un perfil runtime todavia insuficiente
- consumir presupuesto en repeticiones no justificadas
- dejar abierto un fallback que parezca voz real del cliente
- mezclar revision editorial automatica con aprobacion humana

## Criterio de cierre

La etapa se considera cerrada solo si existe evidencia de que:

- la integracion real funciona end-to-end con una llamada controlada
- Plan 006 queda `DONE` o bloqueado con evidencia suficiente
- el benchmark real produce evidencia reproducible
- hay comparacion `v1/v2` en dos casos
- se decide con evidencia si conviene mejorar texto, pasar a audio o abrir `dry_run` externo

## Verificacion esperada al cerrar

- coherencia con `plans/006-integracion-ia-real-controlada.md`
- coherencia con `plans/README.md`
- `git diff --check`
- `git status --short`
