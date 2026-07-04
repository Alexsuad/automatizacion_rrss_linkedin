# 09 — Plan de implementación completo — Sistema automatizado de contenido LinkedIn

## 1. Punto de partida actual

El proyecto ya no está en planeación inicial. Ya existe una base funcional offline validada al cierre del último microciclo con 61 tests deterministas aprobados:

```text
audio/texto/transcripción
→ contratos
→ validadores
→ flujo local simulado
→ diagnóstico editorial
→ aprobación humana
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

El problema actual que resuelve este documento es la definición del mapa completo de implementación paso a paso desde el estado actual offline hasta el sistema usable final.

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

### Fase I — Transcripción local
* **Objetivo:** Aceptar archivos de audio locales y convertirlos en texto limpio.
* **Implementación:** Adaptador de transcripción offline (Faster-Whisper local como candidato).
* **Control:** Sanitización de PII post-transcripción, control de idioma, metadatos y trazabilidad audio → texto.

### Fase J — Trazabilidad audio/texto → post
* **Objetivo:** Comprobar sistemáticamente que el post final representa con fidelidad la idea original del autor.
* **Control:** Detección de ideas inventadas, autoridad fingida, anécdotas inexistentes o afirmaciones sin fuente en el audio de origen.
* **Resultado esperado:** Trazabilidad `PASS` / `WARN` / `FAIL` adjunta al diagnóstico.

### Fase K — Proveedor IA real configurable
* **Objetivo:** Integrar APIs externas (OpenAI, Gemini, DeepSeek) de manera modular.
* **Reglas:** API keys configurables mediante variables de entorno (fuera del repositorio), control de timeouts y manejo de errores de red con fallbacks de contingencia.
* **Resultado esperado:** Adaptador de proveedor IA real acoplable al puerto de IA sin modificar el core del sistema.

### Fase L — Configuración segura
* **Objetivo:** Asegurar la portabilidad del entorno y evitar la fuga de credenciales.
* **Resultado esperado:** Archivos `.env.example` robustos, exclusión estricta en `.gitignore`, validadores de configuración en el arranque del sistema y tests que comprueben la ausencia de secretos en evidencias y logs.

### Fase M — Generación real de post LinkedIn
* **Objetivo:** Conectar el proveedor IA real al pipeline para generar posts candidato basados en la idea e intención real del autor.

### Fase N — Revisión y regeneración
* **Objetivo:** Permitir al usuario solicitar ajustes específicos al post candidato (ajustar hook, suavizar tono, acortar CTA) y mantener un historial de versiones del borrador.

### Fase O — Borrador LinkedIn completo
* **Objetivo:** Consolidar el paquete de salida final del post textual listo para publicarse.
* **Estados:** `borrador_local`, `requiere_revision`, `rechazado_editorial`, `publicable`, `no_publicable`.

### Fase P — Timing y programación sugerida
* **Objetivo:** Recomendar la mejor ventana horaria y fecha para la publicación basándose en preferencias B2B y directrices del autor.

### Fase Q — Adapter Metricool dry_run
* **Objetivo:** Preparar el payload de programación de Metricool y guardarlo localmente para auditoría física.
* **Regla:** Bloqueo físico estricto si no hay aprobación humana previa, si el diagnóstico es `FAIL`, o ante sospecha de PII/secretos.

### Fase R — Publicación/programación real controlada
* **Objetivo:** Habilitar el envío real del post programado a la API de Metricool.
* **Requisitos:** Gate manual explícito superado, dry_run previo correcto, credenciales válidas y almacenamiento de la evidencia del ID de publicación externa en el manifest de trazabilidad.

### Fase S — Recurso visual offline
* **Objetivo:** Asociar metadatos visuales, prompts de generación de imagen o marcadores de posición sin invocar herramientas externas.

### Fase T — Generación visual con proveedor externo
* **Objetivo:** Conectar adaptadores de generación de imágenes (Canva, Higgsfield, etc.) controlando derechos de uso, estilo de marca e incorporando gate de revisión visual humana.

### Fase U — Carruseles
* **Objetivo:** Estructurar slides (portada, desarrollo, cierre, CTA) para formatos interactivos en LinkedIn.

---

## 5. Plan de pruebas

*   **Pruebas unitarias:** Contratos, validadores, diagnóstico editorial, estados de aprobación, sanitizadores de PII/secretos y ausencia de rutas absolutas.
*   **Pruebas de integración offline:** Tubería completa desde la entrada simulada, pasando por el `MockModelAdapter` y el diagnóstico, hasta la persistencia física en el `LocalDraftPublisher`.
*   **Pruebas end-to-end:** Ingesta de audio fixture, transcripción simulada, generación de post, exigencia de aprobación reforzada ante advertencias y bloqueo garantizado ante fallos.
*   **Pruebas de seguridad:** Detección y filtrado de PII, prevención de exposición de credenciales/tokens en logs y evidencias, y auditoría de rutas absolutas locales en los artefactos generados.
*   **Pruebas de adaptadores de red (Fases K y R):** Pruebas de integración con mocks de API de LLM y Metricool que evalúen fallos de red, timeouts, respuestas vacías y payloads corruptos sin realizar llamadas reales ni consumir tokens.

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
1. Consolidar y auditar plan de implementación completo en docs/ (CERRADO CON ESTE DOCUMENTO).
2. Confirmar saneamiento del flujo offline existente: tests desde raíz, bloqueo de FAIL, WARN con aprobación reforzada, evidencia limpia y estado_publicabilidad.
3. Fase B: Módulo de IA (src/linkedin_content_system/ai/ports.py y mock_adapter.py) + tests unitarios.
4. Fase C: Integración de generación de post con MockModelAdapter.
5. Fase D: Ingesta de idea central (modelos de datos Pydantic y flujo).
6. Fase E: Estructuración de intención editorial.
7. Fase F: Diagnóstico editorial completo (reglas y matriz de estados).
8. Fase G: Sistema de aprobación simple/reforzada y bloqueos.
9. Fase H: Flujo end-to-end offline completo y pruebas de integración.
10. Fase I: Integración de transcripción local (adaptador Whisper).
11. Fase J: Trazabilidad semántica e inferencia.
12. Fase K: Adaptadores para proveedores IA reales (OpenAI/Gemini/DeepSeek).
13. Fase L: Configuración segura de credenciales y entornos (.env).
14. Fase M: Pruebas de generación y control en vivo con IA real.
15. Fase N: Lógica de regeneración y revisión de post.
16. Fase O: Salida de borrador LinkedIn final.
17. Fase P: Algoritmo de sugerencia de timing.
18. Fase Q: Adaptador Metricool en modo dry_run.
19. Fase R: Publicación real controlada (API y Gate humano final).
20. Fase S, T, U: Recursos visuales y carruseles (V2 posterior).
```
