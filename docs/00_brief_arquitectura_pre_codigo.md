# 00 — Brief de arquitectura pre-código

## 1. Qué problema resuelve

El ciclo tradicional de creación de contenido profesional tiene alta fricción operativa por la fragmentación de herramientas y la pérdida de identidad narrativa cuando se delegan tareas a inteligencias artificiales genéricas.

El sistema busca resolver:

- **Fricción por cambio de contexto:** salto manual entre la grabación de ideas en audio, la transcripción, redacción, revisión de tono, optimización y calendarización.
- **Contenido genérico:** outputs inflados, redundantes o alejados del tono real del autor.
- **Agente monolítico:** una sola IA intentando conceptualizar, redactar, auditar y preparar publicación al mismo tiempo.
- **Falta de control por etapas:** ausencia de entradas, salidas, criterios de calidad y trazabilidad por fase.

## 2. Para quién sirve

El sistema está diseñado para creadores de contenido, ingenieros de IA y profesionales que necesitan automatizar la publicación de sus ideas expresadas en notas de voz directamente en LinkedIn, manteniendo control sobre el tono y asegurando la portabilidad y modularidad de la arquitectura.

## 3. Producto esperado (V1)

La V1 es un **Publicador automático desde audio para LinkedIn**.

El sistema procesa una nota de voz, genera un post formateado para LinkedIn, lo valida estructuralmente, solicita aprobación humana y, una vez aprobado, lo programa automáticamente para su publicación.

### V1 SÍ incluye:
- **Entrada por audio:** Captura de notas de voz como materia prima principal.
- **Transcripción:** Conversión automática de audio a texto (Faster-Whisper local o API externa).
- **Generación de post LinkedIn:** Creación de contenido con formato idóneo para la plataforma.
- **Revisión automática:** Evaluación de calidad, tono, consistencia y restricciones (Pydantic/LLM).
- **Aprobación humana:** Un gate interactivo o de confirmación humana local antes de cualquier publicación real.
- **Programación automática:** Publicación/calendarización automatizada de la pieza aprobada.
- **Evidencia local:** Registro persistente en local (`trace/` y `output/`) con el resultado del flujo y de la publicación.

### V1 NO incluye (V2):
- Otras redes sociales: Instagram, X/Twitter, Facebook, Threads.
- Formatos enriquecidos: Carruseles, imágenes o video.
- Analítica avanzada o dashboards de rendimiento.
- Interfaz de usuario (UI) completa (se gestiona localmente/CLI).
- Sistema multiusuario.

## 4. Principios base

- **Portabilidad y modularidad:** El núcleo del sistema debe ser agnóstico del publicador externo y del LLM.
- **No publicar sin aprobación humana:** La programación requiere confirmación explícita para evitar errores operativos o de tono.
- **Puertos y adaptadores:** Las integraciones externas (como Metricool o servicios de LLM) son adaptadores intercambiables.
- **Seguridad y Privacidad (PII):** Los audios y transcripciones pueden contener datos de carácter personal (PII). Antes de enviar texto a modelos externos o publicadores se debe sanitizar o aplicar un gate mínimo de privacidad. No se deben registrar secretos, tokens o PII en logs ni evidencias.
- **El repositorio es la fuente de verdad:** Ningún chat, IDE, Metricool o ADK define el comportamiento del sistema. Todo cambio se rige por lo escrito en el repositorio.

## 5. Decisiones de diseño clave para V1

- **Metricool como Adaptador:** Es el primer adaptador real candidato para la programación automática, pero es totalmente reemplazable y no pertenece al núcleo del sistema.
- **LocalDraftPublisher:** previsto como modo local planificado y definido como primera validación local de seguridad. Es la pieza central para pruebas sin conexión (offline) y para validar el flujo completo sin tocar proveedores externos ni generar costes o riesgos operativos.
- **Google ADK:** Utilizado como motor de orquestación inicial para coordinar los flujos agénticos, pero no es una dependencia eterna ni obligatoria a largo plazo.

## 6. Criterio para pasar a implementación

No se debe escribir código hasta tener definidos:
- Contrato de entrada y contrato de salida (V1).
- Contrato de perfil narrativo mínimo.
- Contrato de calidad del post LinkedIn V1.
- Estructura mínima de evidencias locales en `output/` y `trace/`.
- Reglas de gobernanza mínimas en `AGENTS.md`.