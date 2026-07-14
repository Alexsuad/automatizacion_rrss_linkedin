# Plan 008: Recuperar el producto completo por incrementos verificables

> **Executor instructions**: Este plan es la hoja de ruta vigente después de
> los planes 001-007. No conviertas sus incrementos en microplanes de ajuste
> textual ni implementes varias capacidades a la vez. Antes de iniciar cada
> incremento, fija un commit de línea base, revisa el alcance completo de ese
> incremento y ejecuta sus gates de verificación. Si una capacidad requiere
> datos reales, credenciales, coste o publicación, detente y solicita
> autorización explícita.
>
> **Drift check (run first)**: `git status --short` y `git diff --stat
> bb581db..HEAD -- src tests plans benchmarks README.md docs`
> La auditoría que originó este plan incluye cambios aún no confirmados del
> runner de benchmark y de sus tests. No comiences un incremento funcional con
> esos cambios sin una línea base auditable que los incluya o los descarte.

## Estado

- **Prioridad**: P1
- **Esfuerzo**: L, repartido en incrementos cerrados
- **Riesgo**: MED
- **Depende de**: evidencia de planes 006 y 007
- **Categoría**: direction
- **Planned at**: commit `bb581db`, 2026-07-12
- **Estado actual**: INCREMENTO_2_IMPLEMENTED_PENDING_REAL_TRANSCRIPTION_SMOKE

## Producto objetivo y límites

El producto es un Portable Content Publisher, no un generador de posts de
LinkedIn. Su recorrido objetivo es:

```text
entrada multifuente -> normalización y hechos autorizados -> selección de idea
-> adaptación por canal y Brand Voice -> candidata textual/visual -> auditoría
-> corrección limitada -> aprobación humana -> salida/programación -> analítica
-> aprendizaje aprobado
```

LinkedIn textual es el primer vertical desarrollado. Su infraestructura es
útil, pero el benchmark real no alcanzó aceptación editorial; no debe
presentarse como producto final ni como bloqueo permanente del roadmap.

Límites transversales: no PII, secretos ni datos reales en fixtures o evidencia
versionada; ninguna publicación o programación real sin aprobación humana y
autorización explícita; el core no depende de un proveedor, IDE o framework
agéntico; las afirmaciones de voz, calidad y mejora solo se emiten con evidencia
humana o con un método de revisión expresamente validado.

## Línea base auditada

- Los commits `08d5b9b`, `c3dc15a` y `bb581db` demuestran una ruta real de
  LiteLLM/Ollama detrás de `ModelAdapter`, con errores saneados y sin acoplar
  el core al proveedor.
- `output/real_smoke_editorial_quality_20260711T231104Z/` y
  `output/benchmark_real_20260712T095432Z/benchmark_resumen.json` conservan
  evidencia de smoke y benchmark real. El benchmark registra cinco piezas y
  dos ciclos de feedback, todos técnicos y estructurales `PASS`, editoriales
  `WARN` y humanos `PENDIENTE`.
- La suite local pasó con `427 passed`; `python -m compileall -q src tests` y
  `git diff --check` también pasaron durante la auditoría.
- No existe un documento maestro independiente de lecciones aprendidas. Las
  lecciones operativas se conservan en Plan 007, la rúbrica y la evidencia del
  benchmark.

## Matriz de capacidades

| Capacidad | Origen del requisito | Estado real | Evidencia | Brecha y dependencia | Prioridad |
|---|---|---|---|---|---|
| Texto manual | `docs/00`: primer corte; `docs/02` | IMPLEMENTADO_Y_PROBADO | `EntradaContenido`, CLI `--texto`, ciclo editorial y pruebas CLI | Debe pasar al núcleo multifuente sin perder el flujo vigente | P1 |
| Documento textual y borrador existente | `docs/02:24-25,118-121` | IMPLEMENTADO_PARCIAL | Enum `DOCUMENTO_BASE` y `BORRADOR_EXISTENTE` en `contracts/entrada.py` | No hay lector, normalizador ni ruta ejecutable; depende del núcleo de normalización | P1 |
| Audio, transcripción y audio de vídeo | `docs/02:106-116`; `docs/05:57-68` | IMPLEMENTADO_PARCIAL | Enum y contratos; no hay puerto, adaptador ni pruebas de transcripción | Requiere normalización común y un adaptador de transcripción local o autorizado | P1 |
| Entrada de imagen o documento visual | Norte multifuente de este plan; no forma parte de la transcripción contratada en `docs/02` | AUSENTE | No hay contrato, lector, descripción ni pruebas para imagen aportada, captura, escaneo, fotografía o combinación texto-imagen | Debe definirse como entrada visual propia, sin atribuirla al futuro adaptador de transcripción | P2 |
| Normalización, hechos e ideas | `docs/00`, `docs/02`, auditoría de producto | IMPLEMENTADO_PARCIAL | `extraer_idea_central`, intención y trazabilidad determinista | La extracción es heurística y no existe registro estructurado de hechos/experiencias autorizadas | P1 |
| Brand Voice y límites del cliente | `docs/03` | IMPLEMENTADO_PARCIAL | Resolver JSON, tono, palabras, frases y CTA en `flujo_textual_runtime.py` | Faltan ejemplos sí/no, temas, experiencias autorizadas, nivel técnico y estado de completitud aplicado | P1 |
| LinkedIn textual | `docs/00:61-71`, `docs/06` | IMPLEMENTADO_PARCIAL | `LinkedInTextChannelStrategy`, sesiones, feedback, LocalDraft; benchmark real | Infraestructura correcta, gate editorial 4/5 no alcanzado; no es aceptado como producto final | P1 |
| X/Threads, newsletter, Instagram y derivados YouTube | Norte del producto; portabilidad de canal | PLANIFICADO | Protocolo `TextChannelStrategy` acepta inyección | Solo hay estrategia LinkedIn; faltan contratos de formato y casos de uso | P3 |
| Producción visual y Brand Design | Norte del producto; `docs/05:94-101` | AUSENTE | Sin decisión visual, contrato de Brand Design, recurso, prompt visual ni pruebas | Debe cubrir imagen, fotografía, infografía, carrusel, vídeo o prompt visual sin confundirse con la entrada de imagen | P2 |
| Auditoría interna y autocorrección | `docs/06`; Plan 007 | IMPLEMENTADO_PARCIAL | PII, secretos, rutas, trazabilidad, rechazo de metatexto/invención/cierre; ciclo de feedback | No hay revisor editorial independiente ni métrica fiable de voz/naturalidad; corrección sin límite de salida formal | P1 |
| Experiencia de cliente/operador | `docs/01`, auditoría en `docs/Instrucciones/01_auditoria-01` | IMPLEMENTADO_PARCIAL | CLI muestra sesión, versiones, estados y errores saneados | No separa vista cliente de información administrativa y no ofrece candidata completa multiformato | P2 |
| LocalDraft | `docs/04`; Plan 001 | IMPLEMENTADO_Y_PROBADO | `LocalDraftPublisher`, ciclo de aprobación y pruebas de persistencia | Es salida local segura, no prueba de distribución externa | P1 |
| External dry-run operativo | `docs/04`; Plan 003 | IMPLEMENTADO_PARCIAL | `ExternalDryRunPublisher` y `tests/publishers/test_dryrun_publisher.py` crean payload local simulado | La CLI y el ciclo editorial solo componen `LocalDraftPublisher`; falta recorrido end-to-end de candidata aprobada a payload por canal | P1 |
| Programación/publicación real controlada | `docs/04`, `docs/05:72-91` | PLANIFICADO | Puerto de publicación, gates de aprobación y dry-run unitario | No hay scheduler, adaptador externo, operación observable ni reversión; depende de 4A y autorización operacional | P2 |
| Analítica offline y aprendizaje controlado | Norte del producto; `docs/05:94-101` | AUSENTE | No hay contrato de métricas, fixtures, asociación ni reglas de aprendizaje | Puede validarse con datos sintéticos, pero no prueba recuperación externa | P3 |
| Analítica real de proveedor | Norte del producto | AUSENTE | No hay lector de métricas, ID/URL externo ni evidencia de recuperación | Depende de una publicación identificada, acceso autorizado y tiempo de maduración | P3 |
| Portabilidad y configuración | `AGENTS.md`, ADR-000 | IMPLEMENTADO_PARCIAL | `ModelAdapter`, LiteLLM opcional, publisher port, JSON local, estrategias inyectables | Un canal concreto, salida y almacenamiento siguen dominando la composición | P1 |

Estados usados: `IMPLEMENTADO_Y_PROBADO`, `IMPLEMENTADO_PARCIAL`,
`SOLO_DOCUMENTADO`, `PLANIFICADO`, `AUSENTE`, `BLOQUEADO` y `DEUDA_HEREDADA`.
Una enumeración de contrato sin ruta ejecutable se clasifica como parcial, no
como capacidad entregada.

## Contradicciones resueltas y deuda heredada

1. **Plan 006** queda `DONE`. Su objetivo era validar la integración real
   detrás de `ModelAdapter`; Plan 007 aportó una evidencia más actual mediante
   LiteLLM/Ollama, sin publicación y con el ciclo editorial nuevo. El comando
   legacy de Plan 006, que aprobaba antes de generar, queda histórico y no se
   ejecutará para satisfacer literalmente un flujo ya reemplazado.
2. **Plan 007** conserva `IMPLEMENTED_PRODUCT_GATE_NOT_MET`. Sus restricciones
   impedían expandir dentro de ese experimento, pero no son una prohibición
   permanente de audio o dry-run. El roadmap siguiente decide por dependencias
   y evidencia, no por ese cierre aislado.
3. **Índice de planes**: los rechazos de audio y publicación en fases iniciales
   se conservan como decisiones históricas. Plan 008 es la fuente operativa
   para capacidades posteriores.
4. **Contrato vs. runtime**: `TipoEntrada` enumera audio, transcripción y
   documento, mientras `generar_candidato_textual()` acepta solo
   `TEXTO_MANUAL`. Es una deuda de producto explícita, no evidencia de soporte
   multifuente.
5. **Portabilidad nominal**: existen puertos de modelo, estrategia textual y
   publisher, pero solo LinkedIn está implementado y la salida modelada es
   `SalidaLocalDraft`. No hacer un renombrado masivo ni una arquitectura nueva
   antes de que un segundo caso de uso pruebe qué abstracción falta.

## Activos que se conservan

- Contratos Pydantic de entrada, salida, ciclo editorial y trazabilidad.
- Validadores deterministas de PII, secretos, rutas, aprobación y soporte de
  afirmaciones.
- `ModelAdapter` con modos controlled, mock y LiteLLM configurable.
- Sesiones editoriales versionadas con persistencia atómica y feedback.
- `LocalDraftPublisher`, `ExternalDryRunPublisher` y `PublicationPublisherPort`.
- Fixture sintético, perfiles de benchmark, rúbrica humana y evidencia saneada.
- CLI como superficie operativa inicial, no como interfaz final de cliente.

## Deuda que se difiere

- Renombrar `linkedin_content_system` hasta que un segundo canal o fuente
  demuestre el coste real del nombre actual.
- Base de datos, UI SaaS, multiusuario y runtime multiagente.
- Evaluador-modelo automático de calidad: no se añadirá hasta definir evidencia
  y límites que eviten falsos PASS.
- Publicación real y analítica: no se adelantan al incremento que deje una
  candidata aceptable y un dry-run por canal.

## Secuencia de implementación por incrementos completos

### Incremento 1 — Candidata editorial multifuente textual

**Resultado observable**: una persona entrega texto manual, documento textual
o borrador existente y recibe una candidata LinkedIn completa, trazable y
revisable con Brand Voice suficientemente declarada; puede aprobar, pedir un
ajuste o rechazar sin exponer detalles técnicos.

**Alcance cerrado**: normalizador común para las tres entradas textuales,
registro de hechos/experiencias autorizadas, perfil narrativo ampliado fuera del
core, estrategia LinkedIn conservada y revisión separada en estructural,
editorial automática limitada y decisión humana. No incluye audio, visuales,
publicación real ni un segundo canal.

**Aceptación suficiente**: tres fixtures sintéticos (manual, documento y
borrador) recorren el ciclo completo hasta LocalDraft o external dry-run local
solo después de aprobación; cada candidata conserva fuente, hechos y perfil;
el revisor no recibe un `PASS` editorial no demostrable; el flujo conserva una
vista de cliente sin logs ni errores internos.

**Límite**: máximo dos regeneraciones por candidata y una corrección de
implementación del incremento tras el lote de aceptación. Defectos de voz que
no sean seguridad, fidelidad o bloqueo de flujo se registran para evaluación
humana y no abren iteraciones ilimitadas.

**Habilita**: audio/transcripción y dry-run compuesto sobre una entrada común.

**Primera implementación**: commit `97d4e7e`. La auditoría posterior detectó
que faltaban evidencia fragmentada, auditoría estructurada y autocorrección
interna; fueron corregidas en el cierre funcional del Incremento 1.

**Resultado de ejecución (2026-07-13)**: `PASS` offline. Las entradas
`TEXTO_MANUAL`, `DOCUMENTO_BASE` y `BORRADOR_EXISTENTE` pasan por la misma
normalización, conservan hash, referencia relativa, hechos y experiencias
autorizadas en la sesión. El perfil runtime admite límites y ejemplos externos;
el generador y el revisor conservador están separados. El ciclo limita a dos
regeneraciones y pasa a `REQUIERE_ATENCION` cuando se agotan. La CLI ofrece
vista cliente y administrativa; la aprobación reforzada puede preparar
`LocalDraft` o `ExternalDryRunPublisher`, que declara no publicar. Smoke
offline: documento sintético -> sesión pendiente -> aprobación humana ->
external dry-run, sin red ni `LocalDraft`. El auditor separado persiste
hallazgos y feedback estructurado; el ciclo selecciona explícitamente la mejor
versión o exige atención tras dos regeneraciones. La corrección de cierre quedó
congelada en `f9ea71f` y el Incremento 1 queda `DONE`.

### Incremento 2 — Audio local a candidata revisable

**Resultado observable**: un audio sintético autorizado se transcribe,
sanitiza, normaliza y llega al mismo ciclo editorial, conservando el vínculo
audio -> transcripción -> hechos -> candidata.

**Alcance cerrado**: puerto de transcripción, un adaptador local o autorizado,
control de tamaño/formato, sanitización previa al proveedor de generación y
evidencia con hashes. No incluye vídeo completo, publicación ni visuales.

**Aceptación suficiente**: dos audios sintéticos reproducibles generan sesiones
pendientes sin PII, secretos ni transcripción bruta expuesta; un audio inseguro
no invoca transcripción ni generación; tests y un smoke local autorizado pasan.

**Límite**: una implementación de transcriptor y un intento de corrección por
fallo de integración. La calidad de transcripción se revisa en muestra humana,
no mediante reglas de estilo.

**Habilita**: fuentes de vídeo a través de audio extraído y una selección de
piezas basada en hechos normalizados.

**Resultado de ejecución (2026-07-13)**: `PASS TÉCNICO`. El Incremento 2 añade
contrato ejecutable de audio local, validación previa de archivo, puerto de
transcripción desacoplado y dos adaptadores: `fake_fixture` para smoke
determinista y `whisper_cpp` como ruta real local opcional sin red. La
transcripción se sanitiza antes de entrar al generador, conserva hash,
segmentos y procedencia, y se normaliza en el mismo núcleo editorial del
Incremento 1. La CLI admite `--audio`, `--transcriber`, `--idioma` y metadatos
autorizados; el smoke determinista `output/smoke_incremento_2_20260713T123958Z`
recorre audio -> transcripción fake -> auditoría -> selección -> aprobación
simulada -> `ExternalDryRunPublisher`, con `publicado=false`. La suite quedó en
`465 passed`. El smoke real local no pudo ejecutarse en este entorno porque
faltan `whisper-cli` y `LINKEDIN_CONTENT_TRANSCRIPTION_MODEL_PATH`; por eso el
estado operativo queda `IMPLEMENTED_PENDING_REAL_TRANSCRIPTION_SMOKE`.

### Incremento 3 — Entrada visual, decisión visual y Brand Design

**Resultado observable**: una imagen aportada, captura, documento escaneado o
fotografía puede normalizarse como contexto cuando el caso lo requiera; cada
candidata determina por separado si necesita recurso visual y, cuando
corresponda, genera un brief/prompt o un recurso con Brand Design y evidencia
de concordancia texto-visual.

**Alcance cerrado**: contrato de entrada visual, combinación texto-imagen,
contrato de decisión visual, perfil de diseño externo al core, un tipo de
recurso inicial y revisión de concordancia. No incluye una biblioteca de
carruseles, edición de vídeo ni publicación.

**Aceptación suficiente**: una entrada visual sintética y una combinación
texto-imagen conservan su procedencia; tres candidatas producen decisión
`sin_visual` o un recurso/brief trazable; la revisión bloquea una pieza visual
que contradiga texto, voz o restricciones de marca; aprobación humana sigue
siendo obligatoria.

**Límite**: un formato visual inicial y dos iteraciones de generación por
recurso. Los formatos restantes se difieren sin crear adaptadores vacíos.

**Habilita**: candidatas completas por canal y payloads de salida con recursos.

### Incremento 4 — Distribución: dry-run y smoke real controlado

#### 4A — Dry-run operativo obligatorio

**Resultado observable**: una candidata aprobada produce un payload externo
válido por canal, ejecuta un dry-run verificable y conserva evidencia
persistida que confirma la ausencia de publicación real.

**Alcance cerrado**: composición explícita de `ExternalDryRunPublisher`,
adaptación por canal, payload, idempotencia y evidencia. No incluye
automatización de engagement ni publicación real.

**Aceptación suficiente**: una candidata aprobada llega a dry-run; una
pendiente, rechazada o con FAIL no genera payload; no se filtran secretos; cada
operación queda asociada a versión, aprobación y manifest; la evidencia declara
payload, canal, modo dry-run y ausencia de publicación real.

**Estado después de 4A**: `IMPLEMENTED_PENDING_REAL_PUBLISH_SMOKE` hasta que
4B tenga autorización, credencial, cuenta/destino seguro y evidencia real. 4A
no permite declarar terminada la capacidad de distribución.

#### 4B — Smoke real de programación/publicación controlada

**Resultado observable**: una única operación real autorizada programa o
publica una candidata aprobada en un destino seguro y deja ID, URL o referencia
externa, evidencia de operación y resultado saneado.

**Alcance cerrado**: un proveedor/adaptador real, una cuenta o destino seguro,
aprobación humana explícita, manejo de error y una cancelación, borrado o
reversión cuando el proveedor lo permita. No incluye reintentos automáticos,
fallback entre proveedores, engagement ni lote de publicaciones.

**Aceptación suficiente**: la operación es observable, queda asociada a versión
y aprobación, conserva la referencia externa y no expone secretos; si falla,
el error queda saneado y no se repite sin autorización. Debe demostrarse la
capacidad de cancelación, borrado o reversión cuando el proveedor soporte una.

**Límite y bloqueo**: máximo una operación de smoke. Si falta autorización,
credencial, destino seguro o el proveedor no permite una operación reversible,
mantener `IMPLEMENTED_PENDING_REAL_PUBLISH_SMOKE` y no sustituirlo por un PASS
de dry-run.

**Habilita**: asociación verificable de resultados externos a una pieza
aprobada y el smoke de métricas reales.

### Incremento 5 — Analítica: contrato offline y recuperación real

#### 5A — Contrato y procesamiento offline de métricas

**Resultado observable**: fixtures de métricas validan esquema, asociación
métrica -> pieza, cálculos, almacenamiento, reglas de aprendizaje y prevención
de contaminación entre perfiles o clientes.

**Alcance cerrado**: contrato de métrica, almacenamiento local, asociación con
pieza/canal/perfil y propuesta explícita. No modifica Brand Voice ni Brand
Design automáticamente ni consulta proveedores.

**Aceptación suficiente**: fixtures producen una recomendación trazable; una
métrica de otro perfil no contamina el actual; ningún aprendizaje se aplica sin
aprobación humana; pruebas cubren ausencia, datos incompletos y duplicados.

**Estado después de 5A**: implementación offline parcial. No puede declararse
analítica completa sin 5B; si depende de publicación real o de tiempo de
maduración, se registra como pendiente y no como `DONE`.

#### 5B — Smoke real de recuperación de métricas

**Resultado observable**: una publicación identificada por ID o URL se consulta
desde proveedor o fuente autorizada; las métricas reales quedan asociadas a la
pieza correcta, persistidas y acompañadas de evidencia reproducible.

**Alcance cerrado**: una fuente real, una pieza publicada identificable, lectura
autorizada, manejo de ausencia, retraso y error del proveedor. No incluye
optimización automática ni aprendizaje aplicado sin aprobación humana.

**Aceptación suficiente**: la evidencia registra referencia externa, momento de
lectura, conjunto de métricas, asociación a versión y resultado saneado. La
ausencia o retraso de métricas no se interpreta como rendimiento negativo ni
como error no controlado.

**Límite y bloqueo**: máximo una fuente y un ciclo de recuperación por smoke.
Si no existe publicación real autorizada, no maduraron las métricas o falta
acceso, conservar el estado pendiente de analítica real; 5A no lo sustituye.

**Habilita**: decisiones de formato, voz y diseño basadas en aprendizaje humano
aprobado.

### Incremento 6 — Segundo canal reutilizando el core

**Resultado observable**: una misma entrada normalizada produce candidatas
distintas y trazables para LinkedIn y un segundo canal elegido por evidencia de
usuario, sin duplicar generación, validación ni aprobación.

**Alcance cerrado**: una estrategia concreta de segundo canal, contrato de
formato, dry-run local y pruebas de aislamiento. No incluye lanzar todos los
canales ni renombrar masivamente el paquete.

**Aceptación suficiente**: fixtures compartidos producen dos piezas con reglas
de canal diferenciadas; una estrategia no puede publicar ni contaminar la otra;
las aprobaciones y evidencias conservan canal y versión.

**Límite**: un canal nuevo y un formato principal. La elección se documenta al
iniciar el incremento, no se presupone Instagram, newsletter o Threads.

**Habilita**: evaluar un renombrado del paquete y la siguiente expansión de
canales con evidencia real.

## Contrato de ejecución y límite de iteraciones

Cada incremento anterior es una misión funcional completa y debe registrar:

- resultado observable y alcance cerrado antes de tocar código;
- pruebas unitarias, de integración del flujo afectado y una evidencia
  end-to-end sintética o autorizada según el alcance;
- un máximo de dos iteraciones de corrección sobre el mismo defecto de
  implementación; si persiste, declarar bloqueo con la evidencia;
- calidad suficiente definida por su criterio de aceptación, no perfección de
  estilo, hook, CTA o tono;
- defectos diferibles que no rompan seguridad, fidelidad, trazabilidad,
  aprobación o el resultado observable;
- condición de bloqueo cuando falte contrato, autorización, entorno seguro,
  dependencia necesaria o evidencia para una afirmación de `PASS`;
- la capacidad habilitada por el incremento antes de empezar el siguiente.

Para calidad editorial, quedan prohibidos los planes aislados de hook, CTA,
tono o estilo. Plan 007 no se reabre y no se ejecutan nuevos benchmarks
textuales salvo regresión o bug bloqueante. La auditoría editorial solo se
mejora dentro del incremento funcional que consume esa candidata.

## Próxima misión ejecutable

Ejecutar el **Incremento 2: Audio local a candidata revisable** solo sobre un
commit que incluya este cierre. No reabrir el Incremento 1 ni el Plan 007 salvo
una regresión demostrada de seguridad, trazabilidad o aprobación.

## Gates transversales antes de cada incremento

- Commit identificable y `git status --short` revisado; no mezclar cambios
  ajenos ni `docs/Instrucciones/`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest -q`,
  `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` y
  `git diff --check` en verde.
- Fixtures sintéticos, sin secretos, PII ni rutas absolutas; búsqueda de
  contaminación revisada para los archivos tocados.
- Revisión humana de alcance, presupuesto y riesgos antes de red, credenciales,
  publicación o datos reales.
- Un incremento no se considera aceptado por una respuesta no vacía, un PASS
  técnico o una modificación textual: debe cumplir su resultado observable y
  su criterio de aceptación.

## Gates de cierre

### Gate A — MVP usable

El MVP se considera usable solo cuando se demuestre de extremo a extremo:

- entrada textual y documental funcional;
- audio real con transcripción integrada;
- extracción de hechos y experiencias autorizadas;
- candidata textual terminada y decisión o propuesta visual mínima;
- auditoría interna y autocorrección limitada;
- aprobación humana; salida local o dry-run operativo;
- experiencia separada para cliente y administración, sin exponer logs ni
  errores internos;
- evidencia reproducible del flujo completo.

Este gate no implica programación/publicación real, analítica real ni cierre
del producto completo.

### Gate B — Producto V1 comprometido

El Producto V1 se considera comprometido solo después de Gate A y cuando exista
evidencia de:

- programación o publicación real controlada con operación observable;
- analítica real mínima recuperada desde una publicación identificada;
- aprendizaje aprobado y trazable;
- al menos un segundo canal reutilizando el mismo core;
- producción visual funcional o integración real con un proveedor visual;
- portabilidad demostrada entre proveedores, canales y publishers.

Ni componentes offline, ni dry-run aislado, ni métricas sintéticas permiten
marcar Gate B como `DONE`.

## Riesgos y condiciones de parada

- Detener un incremento si obliga a mezclar datos reales de clientes con
  fixtures, prompts o evidencia versionada.
- Detenerlo si una nueva fuente necesita saltarse sanitización, trazabilidad o
  aprobación humana.
- No crear un evaluador-modelo, una UI completa, base de datos o framework
  multiagente como sustituto de una capacidad observable.
- Si la arquitectura existente impide un incremento, producir una decisión
  técnica acotada antes de refactorizar el core; no crear capas especulativas.
