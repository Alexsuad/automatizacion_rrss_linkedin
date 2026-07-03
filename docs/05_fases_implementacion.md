# 05 — Fases de implementación

Este documento detalla las etapas de desarrollo y el plan de entregas del proyecto de automatización, estructurado en fases incrementales para asegurar la calidad técnica y evitar la sobrediseño inicial.

---

## Fase 1 (V1) — Publicador automático desde audio para LinkedIn

**Objetivo:** Desarrollar el pipeline mínimo viable para programar publicaciones en LinkedIn a partir de grabaciones de voz, priorizando la privacidad y la portabilidad de los adaptadores.

> [!IMPORTANT]
> **Regla de Prioridad Local:** La primera implementación controlada debe validar el flujo local end-to-end con `LocalDraftPublisher`, `dry_run`, aprobación humana y evidencia local antes de cualquier integración real externa.

### Flujo Operativo:
`audio → transcripción local → post LinkedIn → revisión automática (LLM/Pydantic) + sanitización PII → aprobación humana (Gate) → preparación local o programación futura mediante adaptador → evidencia local`

### Subfases de la V1 (Orden de Implementación):

*   **Fase 1A — LocalDraftPublisher:**
    *   Implementación de la ingesta de audio, transcripción mediante adaptador local candidato, redacción mediante adaptador de modelo candidato y auditoría local de PII.
    *   Aplicación del contrato de calidad del post LinkedIn antes de la aprobación humana para validación y diagnóstico editorial de la salida.
    *   Implementación del `LocalDraftPublisher`, que actúa como mock/modo local de simulación y genera archivos JSON de evidencia del kit en el directorio local de salida de forma 100% offline.
    *   Este adaptador es la pieza base para las pruebas y desarrollo desconectado.
*   **Fase 1B — Adaptador Externo Dry-Run:**
    *   Desarrollo del adaptador de programación externa candidato (como Metricool) configurado en modo `dry_run` para asegurar que el contrato y las credenciales se procesan correctamente sin realizar publicaciones reales.
*   **Fase 1C — Publicación Real:**
    *   Activación del canal real de publicación y programación externa futura mediante adaptador reemplazable (como Metricool) solo después de validar el flujo local y contar con la aprobación humana explícita para cada post individual.

### Entregables Clave de la V1:
1.  **Módulo de Entrada e Ingesta:** Ingesta de audios locales y configuración de perfil narrativo del autor.
2.  **Módulo de Transcripción:** Adaptador local de transcripción (donde Faster-Whisper local es un candidato evaluable).
3.  **Filtro de Privacidad:** Sanitización previa a la salida de datos para evitar fugas de PII o credenciales hacia APIs de LLM externas.
4.  **Módulo de Redacción y Revisión:** Generación de post (donde Google ADK es candidato) y validación estructurada.
5.  **Gate de Aprobación Humana:** CLI o interactivo local sencillo para aprobar, editar o rechazar el post de LinkedIn antes de enviarlo.
6.  **Harness de Trazabilidad:** Almacenamiento local en disco de la traza de ejecución de cada kit en `trace/` (excluyendo PII).

---

## Fase 1.5 (V1.5) — Robustez y Pruebas
**Objetivo:** Extender la cobertura de pruebas, validación automática de prompts y optimizar el rendimiento de Faster-Whisper local.

*   Integración de suite completa de pruebas unitarias usando `LocalDraftPublisher`.
*   Monitoreo de costes y tokens consumidos.
*   Sanitización avanzada de expresiones regulares para proteger datos personales.

---

## Fase 2 (V2) — Expansión Omnicanal y Formatos Visuales
**Objetivo:** Ampliar el sistema a otros canales y tipos de formato una vez consolidado el núcleo funcional estable de LinkedIn.

*   **Nuevas Redes Sociales:** Integración de X/Twitter (hilos), Instagram, Facebook y Threads.
*   **Formatos Enriquecidos:** Generación automática de carruseles PDF y de imágenes tipo quote usando herramientas locales o APIs de diseño.
*   **Analítica de Rendimiento:** Integración de analíticas para medir la repercusión de los posts publicados.
*   **Interfaz de Usuario (UI):** Desarrollo de un panel web para la aprobación humana simplificada.
*   **Multiusuario:** Soporte para múltiples perfiles y marcas desde una sola instancia.
