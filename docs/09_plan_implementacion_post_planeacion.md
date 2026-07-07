# 09 — Plan de implementación completo — Sistema automatizado de contenido LinkedIn

## 1. Punto de partida actual

El proyecto ya no está en planeación inicial. Ya existe un núcleo V1 offline textual/controlado cerrado, validado con 275 tests deterministas aprobados y con la cadena operativa resuelta antes de persistir LocalDraft:

```text
audio/texto/controlado
→ contratos
→ validadores
→ flujo local simulado
→ diagnóstico editorial
→ aprobación humana
→ resolución de publicabilidad
→ LocalDraftPublisher
→ evidencia local
```

El estado del repositorio cuenta con gobernanza documental robusta:
* `docs/00_brief_arquitectura_pre_codigo.md`
* `docs/01_alcance_si_no.md`
* `docs/02_contrato_entrada_contenido.md`
* `docs/03_contrato_perfil_narrativo.md`
* `docs/04_contrato_salida.md`
* `docs/05_fases_implementacion.md`
* `docs/06_contrato_calidad_post_linkedin.md`
* `docs/07_gates_futuros_v1.md`
* `docs/08_skills_producto_linkedin_futuras.md`
* `docs/architecture/ADR-000_Decisiones_Tecnicas_Base.md`
* `AGENTS.md`

El problema que resuelve este documento ya no es "qué imaginar", sino dejar un mapa vigente y confiable de dónde estamos, qué quedó cerrado y cuál es la siguiente decisión real.

Antes de trabajar con contexto real de cliente o fuentes externas, aplicar las reglas ya cerradas de Fase J.

## 1.1 Estado actual del proyecto

- [x] Núcleo V1 offline textual/controlado cerrado.
- [x] Pipeline offline con contexto cerrado.
- [x] Sistema de publicabilidad editorial cerrado.
- [x] Persistencia LocalDraft protegida: solo `publicable` puede persistir como borrador local listo.
- [x] Tests actuales esperados: 275 passed.
- [x] No hay publicación real.
- [x] No hay Metricool real.
- [x] No hay IA real conectada.
- [x] No hay transcripción local real conectada.
- [x] No hay automatización omnicanal.
- [x] Fase B — Puerto IA portable / MockAdapter offline.
- [x] Fase C — Generación mock de post.
- [x] Fase D — Extracción determinista de idea central.
- [x] Fase E — Intención editorial determinista.
- [x] Fase F — Diagnóstico editorial base.
- [x] Fase G — Aprobación humana.
- [x] Fase H — Evidencia de generación / salida local.
- [x] Fase I — Exports públicos de F/G/H.
- [x] Fase J — Contexto de trabajo aislado / anticontaminación.
- [x] Fase K — Compatibilidad de contexto.
- [x] Fase L — Cambio/reset de contexto.
- [x] Fase M — Exports públicos de contexto.
- [x] Fase N — Evidencia de contexto usado.
- [x] Fase O — Exports de evidencia de contexto.
- [x] Fase P — Pipeline offline con contexto.
- [x] Fase Q — Exports públicos del pipeline.
- [x] Fase R — Mapa técnico de contexto/pipeline offline.
- [x] Saneamiento Marketing/RRSS/Producto — criterios editoriales.
- [x] Saneamiento Marketing/RRSS/Producto — contrato de publicabilidad.
- [x] Saneamiento Marketing/RRSS/Producto — bloqueos críticos editoriales.
- [x] Saneamiento Marketing/RRSS/Producto — validación operativa antes de persistir LocalDraft.
- [x] Saneamiento Marketing/RRSS/Producto — documentación alineada y export público.
- [~] Próxima decisión — Etapa S: trazabilidad fuerte entrada → idea → post (pendiente de autorización).
- [ ] Proveedor IA real configurable en modo dry_run.
- [ ] Transcripción local real.
- [ ] Adaptador externo tipo Metricool dry_run.
- [ ] Publicación/programación real.
- [ ] Métricas/analítica posterior.
- [ ] UI o interfaz operativa.
- [ ] Skills editoriales reales de producto, solo cuando haya contrato individual aprobado.

> [!WARNING]
> Advertencia de trazabilidad: algunas letras de fases antiguas en versiones previas del plan no corresponden al mapa real ejecutado. Este documento queda actualizado como fuente vigente de verdad. Las fases I y L del mapa real ya están cerradas; no deben confundirse con propuestas antiguas de “transcripción local real” o “proveedor IA real”.

---

## 2. Objetivo final del proyecto

El sistema debe permitir que un usuario entregue una idea hablada o escrita y reciba un post listo para LinkedIn, revisado, aprobado y preparado para publicación.

Flujo objetivo:
```text
Usuario entrega audio / nota / texto
→ el sistema transcribe o normaliza
→ extrae idea central
→ identifica intención editorial
→ genera post LinkedIn
→ revisa calidad, voz, PII, compliance y trazabilidad
→ humano aprueba / rechaza / pide cambios
→ prepara borrador local
→ opcionalmente prepara recurso visual (V2)
→ programa o publica mediante adaptador
→ guarda evidencia
→ registra aprendizaje básico posterior
```

---

## 3. Versiones del proyecto

### MVP offline
Objetivo: demostrar que el sistema completo puede funcionar sin red, sin API keys y sin publicación real.
* **Incluye:** entrada textual simulada, contratos, validadores, generación mock, diagnóstico editorial, aprobación humana, borrador local, evidencia local y tests.
* **No incluye:** LLM real, Whisper real, Metricool real, publicación real, imágenes externas, runtime de ADK obligatorio.

### V1 funcional LinkedIn
Objetivo: que el usuario pueda generar y revisar posts reales de LinkedIn con ayuda de IA, manteniendo aprobación humana.
* **Incluye:** entrada por texto o transcripción, proveedor IA configurable, generación de post LinkedIn, diagnóstico editorial, aprobación simple/reforzada, borrador local, evidencia y opción de preparar publicación.
* **Puede incluir:** transcripción local, dry_run de Metricool, configuración segura de proveedor IA.
* **No debe incluir todavía:** publicación automática sin control, engagement automático, scraping, likes, comentarios o mensajes automáticos.

### V1.5 publicación controlada
Objetivo: permitir programación o publicación real solo bajo condiciones seguras.
* **Incluye:** Metricool o adaptador equivalente, dry_run validado, payload de publicación, credenciales fuera del repositorio, aprobación humana explícita, bloqueo por FAIL editorial o PII/secretos, y evidencia de publicación/programación.

### V2 visual (Fase posterior)
Objetivo: añadir recursos visuales al post.
* **Incluye:** imagen de acompañamiento, quotes visuales, creativo simple, posible carrusel, revisión humana visual y evidencia del recurso generado.
* **Nota:** No debe contaminar el MVP textual. Las imágenes son importantes, pero no deben bloquear que el sistema textual funcione bien primero.

### Post-MVP
Objetivo: convertir el sistema en algo más amplio y reusable.
* **Incluye:** omnicanal (Instagram, X/Twitter, newsletter), carruseles avanzados, interfaz de usuario (UI), multiusuario, multi-cliente, analítica, aprendizaje automático. Queda fuera de la V1 inicial.

---

## 4. Fases de implementación detalladas

### Fase A — Consolidación del estado actual
* **Objetivo:** Asegurar que lo ya construido está limpio y no se reabre innecesariamente.
* **Criterios de Cierre:** Tests pasan, git limpio, no hay rutas locales absolutas en el código del repositorio, no hay secretos expuestos ni PII en evidencias locales.

### Fase B — Puerto IA portable (Módulo de IA)
* **Objetivo:** Crear la frontera interna para usar IA sin acoplar el núcleo a ningún proveedor.
* **Ubicación:** Las interfaces y adaptadores de IA residirán en un módulo exclusivo e independiente, nunca dentro de `publishers/`.
  * Puerto (interfaz abstracta): `src/linkedin_content_system/ai/ports.py`
  * Adaptador Mock offline: `src/linkedin_content_system/ai/mock_adapter.py`
* **Resultado esperado:** Interfaz interna de generación IA desacoplada, MockAdapter offline y tests deterministas sin llamadas a red ni SDKs externos.

### Fase C — Generación de post con mock
* **Objetivo:** Conectar la entrada validada con la generación simulada de post.
* **Flujo:** `EntradaContenido → intención editorial → idea central → MockModelAdapter → PostLinkedIn → diagnóstico editorial`
* **Resultado esperado:** Post simulado, estructura validada, diagnóstico inicial y tests de integración offline.

### Fase D — Extracción de idea central
* **Objetivo:** Evitar el "teléfono roto" extrayendo los conceptos clave de la entrada antes de redactar.
* **Estructura de datos:** `idea_central`, `resumen_operativo`, `puntos_de_soporte`, `límites_de_inferencia`.
* **Resultado esperado:** Modelos de datos estables y casos de uso de extracción validados con mocks.

### Fase E — Intención editorial
* **Objetivo:** Garantizar que cada post tenga una dirección estratégica de negocio y tono.
* **Estructura de datos:** `audiencia_objetivo`, `objetivo_del_post`, `pilar_contenido`, `tipo_de_post`, `dolor_o_tension`, `cta_intencionado`, `nivel_de_promocion`.
* **Resultado esperado:** Inclusión de la intención editorial en la tubería semántica.

### Fase F — Diagnóstico editorial completo
* **Objetivo:** Evaluar si el post cumple los estándares de calidad y no tiene riesgos.
* **Validaciones:** Claridad de idea, hook, voz del cliente, autenticidad, CTA, compliance, riesgo genérico, PII, claims sin fuente, trazabilidad, riesgo reputacional.
* **Estados:** `PASS` (avanza con aprobación simple), `WARN` (requiere aprobación reforzada), `FAIL` (no puede avanzar como borrador publicable).

### Fase G — Aprobación humana simple/reforzada
* **Objetivo:** Conectar el diagnóstico editorial con la aprobación interactiva de forma segura.
* **Matriz de Control:**
  * Diagnóstico `PASS` + Aprobación Simple → `Aprobado` (avanza)
  * Diagnóstico `WARN` + Aprobación Reforzada → `Aprobado` (avanza con advertencias)
  * Diagnóstico `WARN` + Aprobación Simple → `Bloqueado`
  * Diagnóstico `FAIL` + Cualquier Aprobación → `Bloqueado`

### Fase H — Flujo end-to-end offline completo
* **Objetivo:** Unir todo el pipeline semántico sin IA real ni red.
* **Resultado esperado:** Tests end-to-end simulados que generen `post.md`, `diagnostico.json`, `manifest.json` y el estado final de publicabilidad.

### Fase I — Exports públicos de F/G/H
* **Objetivo real cerrado:** Exports públicos de F/G/H.
* **Resultado:** Exportar de forma pública los contratos y evidencias de Fase F, Fase G y Fase H.
* **Estado del mapa real:** cerrado como hito de trazabilidad; no debe reinterpretarse como transcripción local.

### Fase J — Contexto de trabajo aislado / anticontaminación V0
* **Objetivo:** Crear una frontera explícita para separar cliente, página/canal, tema, tono, campaña y contexto activo antes de usar datos reales o fuentes externas.
* **Regla:** Ningún dato real de cliente debe entrar en tests, fixtures, docs generales, evidencias versionadas ni core reutilizable.
* **Debe cubrir:** contexto activo; contexto prohibido; reset/cambio de contexto; prevención de mezcla cliente A / cliente B; prevención de mezcla página personal / página empresa; prevención de mezcla campaña / tema / tono; evidencia de qué contexto fue usado.
* **No objetivos:** no conectar Google Drive todavía; no conectar Notion todavía; no crear UI; no persistir contexto real; no generar posts con datos reales; no publicar; no mezclar contexto entre clientes.

### Fase K — Compatibilidad de contexto
* **Objetivo:** Validar que el contexto activo y el contexto prohibido se distingan sin ambigüedad.
* **Control:** Prevención de mezcla cliente A / cliente B, página personal / página empresa, campaña / tema / tono.
* **Resultado esperado:** Estados de compatibilidad claros y tests de aislamiento.

### Fase L — Cambio/reset de contexto
* **Objetivo:** Permitir reset y cambio explícito del contexto de trabajo sin mezclar clientes, campañas o tonos.
* **Resultado esperado:** Flujo determinista de cambio de contexto con evidencia del contexto usado.

### Fase M — Exports públicos de contexto
* **Objetivo:** Exponer públicamente los contratos y resultados del contexto de trabajo.
* **Resultado esperado:** Exports públicos estables y consumibles desde el paquete de contratos.

### Fase N — Evidencia de contexto usado
* **Objetivo:** Registrar qué contexto concreto fue usado en cada ejecución.
* **Resultado esperado:** Evidencia trazable, sin rutas locales absolutas ni secretos.

### Fase O — Exports de evidencia de contexto
* **Objetivo:** Publicar las evidencias de contexto usado sin contaminar el core.
* **Resultado esperado:** Exportaciones consistentes de la evidencia de contexto.

### Fase P — Pipeline offline con contexto
* **Objetivo:** Unir el contexto de trabajo aislado al pipeline offline.
* **Resultado esperado:** Ejecución offline con contexto controlado de extremo a extremo.

### Fase Q — Exports públicos del pipeline
* **Objetivo:** Exponer públicamente los contratos y evidencias del pipeline offline.
* **Resultado esperado:** Export público coherente de la tubería offline.

### Fase R — Mapa técnico de contexto/pipeline offline
* **Objetivo:** Consolidar el mapa técnico real de contexto y pipeline offline.
* **Resultado esperado:** Documento técnico de referencia para el estado ejecutado.

### Roadmap futuro funcional
* **Etapa S — Trazabilidad fuerte entrada → idea → post:** próxima decisión candidata, pendiente de autorización.
* **Transcripción local real:** pendiente futuro, sin letra cerrada en el mapa real.
* **Proveedor IA real configurable:** pendiente futuro, sin letra cerrada en el mapa real.
* **Configuración segura avanzada:** pendiente futuro, no implementada.
* **Generación real de post LinkedIn:** pendiente futuro, no implementada.
* **Revisión y regeneración:** pendiente futuro, no implementada.
* **Timing y programación sugerida:** pendiente futuro, no implementada.
* **Metricool dry_run:** pendiente futuro, no implementada.
* **Publicación/programación real:** pendiente futuro, no implementada.
* **Recursos visuales y carruseles:** pendiente futuro, no implementados.
* **UI o interfaz operativa:** pendiente futuro, no implementada.
* **Métricas/analítica posterior:** pendiente futuro, no implementada.

### Etapa S.0 — Diseño de trazabilidad fuerte entrada → idea → post
* **Estado:** diseño documental/pre-código. No iniciada como implementación.
* **Objetivo:** definir una validación determinista y auditable que compruebe que el `PostLinkedIn` o salida candidata equivalente existente no introduce hechos, autoridad, anécdotas, cifras, promesas, claims o referencias sensibles no soportadas por la entrada original, la idea central o el contexto permitido.
* **Alcance acotado:** no intenta detectar todas las afirmaciones del texto. Solo revisa afirmaciones explícitas sensibles o de riesgo: cifras, logros, autoridad, experiencia personal, promesas, claims técnicos/comerciales y referencias a cliente/contexto.
* **Estados esperados:** `PASS`, `WARN`, `FAIL`.
* **Integración futura:** después de generar el post candidato, antes de aprobación humana, antes de resolver `estado_publicabilidad` y antes de persistir `LocalDraft`.
* **Fuera de alcance en S.0:** IA real, RAG, embeddings, vector DB, Internet, Metricool, transcripción real, publicación real y UI.
* **Microfases previstas:** S.1 contratos/modelos mínimos, S.2 validador determinista, S.3 integración con diagnóstico/publicabilidad y S.4 tests end-to-end offline.

---

## 5. Plan de pruebas

*   **Pruebas unitarias:** Contratos, validadores, diagnóstico editorial, estados de aprobación, sanitizadores de PII/secretos y ausencia de rutas absolutas.
*   **Pruebas de integración offline:** Tubería completa desde la entrada simulada, pasando por el `MockModelAdapter` y el diagnóstico, hasta la persistencia física en el `LocalDraftPublisher`.
*   **Pruebas end-to-end:** Ingesta de audio fixture, transcripción simulada, generación de post, exigencia de aprobación reforzada ante advertencias y bloqueo garantizado ante fallos.
*   **Pruebas de seguridad:** Detección y filtrado de PII, prevención de exposición de credenciales/tokens en logs y evidencias, y auditoría de rutas absolutas locales en los artefactos generados.
*   **Pruebas del roadmap futuro funcional:** Pruebas de integración con mocks de API de LLM y Metricool que evalúen fallos de red, timeouts, respuestas vacías y payloads corruptos sin realizar llamadas reales ni consumir tokens.

Toda fase técnica debe cerrarse con prueba proporcional, evidencia del comando ejecutado y estado PASS/WARN/BLOQUEADO.

---

## 6. Gates obligatorios de control

1.  **Gate de entrada:** El contenido inicial cumple estrictamente el formato y tamaño esperado.
2.  **Gate de sanitización (PII/Secretos):** Ningún dato personal identificable o secreto del entorno pasa al pipeline editorial.
3.  **Gate de calidad editorial:**
    * El diagnóstico `PASS` puede avanzar con aprobación humana simple.
    * El diagnóstico `WARN` solo puede avanzar con aprobación humana reforzada.
    * El diagnóstico `FAIL` no puede avanzar como salida publicable.
4.  **Gate de aprobación humana:** Aprobación explícita (simple para `PASS`, reforzada para `WARN`) antes de la persistencia o programación.
5.  **Gate de publicabilidad:** Valida el campo `estado_publicabilidad` y confirma que solo pueda ser publicable cuando:
    * Diagnóstico editorial `PASS` + aprobación simple, o
    * Diagnóstico editorial `WARN` + aprobación reforzada.
    * Sin bloqueos críticos, sin PII, sin secretos, y con evidencia completa registrada en el manifest.

---

## 7. Protocolo de Skills de Gobernanza y Producto

1.  **Skills de Gobernanza agéntica:** Implementadas localmente en `.agents/skills/` para auditar la trazabilidad de entrada-salida, limpieza de secretos y no mezcla de capas.
2.  **Skills de Producto (Fase Futura):** Las skills relacionadas con la redacción y marketing de LinkedIn (ej. `redactar-post-linkedin`, `validar-voz-cliente`, etc.) se crearán a demanda únicamente cuando el pipeline offline esté completo.
3.  **Protocolo Central de Customizations:** Antes de proponer o crear cualquier skill, se debe ejecutar el validador contra la biblioteca central de customizations/skills definida por el entorno local del usuario para verificar que la capacidad no exista ya a nivel global o de plantilla en el laboratorio.

---

## 8. Orden recomendado de trabajo

```text
1. Estado actual consolidado y cerrado: núcleo offline textual/controlado, publicabilidad editorial y export público.
2. Próxima decisión recomendada: [~] Etapa S — Trazabilidad fuerte entrada → idea → post (pendiente de autorización).
3. Si se aprueba la siguiente etapa, escoger conscientemente una sola vía: proveedor IA real configurable en dry_run, transcripción local real o trazabilidad reforzada antes de abrir integraciones externas.
4. Mantener fuera del alcance: publicación/programación real, Metricool real, automatización omnicanal, UI y analítica hasta nueva auditoría explícita.
```
