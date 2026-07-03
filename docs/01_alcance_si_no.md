# 01 — Alcance SÍ/NO

## 1. Propósito del documento

Este documento define el alcance inicial (V1) del proyecto.

Su función es evitar que el sistema crezca sin control, adopte tecnologías antes de tiempo o confunda el objetivo principal. El alcance de la V1 se enfoca en automatizar la publicación para un único canal clave (LinkedIn) a partir de una nota de voz, garantizando la seguridad en el manejo de datos y la modularidad de la arquitectura.

---

## 2. SÍ entra en la primera versión (V1)

| Elemento | Detalle e Implicación |
| :--- | :--- |
| **Entrada por audio** | Entrada principal a través de notas de voz/archivos de audio. |
| **Transcripción local/remota** | Conversión de audio a texto (priorizando Faster-Whisper local como adaptador). |
| **Generación de post LinkedIn** | Creación y formateo de la pieza de contenido optimizada para LinkedIn. |
| **Revisión automática** | Evaluación de calidad, estructura y tono usando Pydantic y LLM de forma estructurada. |
| **Aprobación humana (Gate)** | Mecanismo de control local donde el usuario aprueba o rechaza el borrador antes de programar. |
| **Programación automática** | Calendarización o publicación automatizada del post aprobado. |
| **Evidencia local estructurada** | Persistencia en `trace/` y `output/` del flujo completo y el estado del publicador. |
| **Metricool como primer adaptador** | Primer adaptador real para programación automática (reemplazable y no acoplado al núcleo). |
| **LocalDraftPublisher** | Modo de publicación local y fallback offline, vital para testing sin coste ni riesgo operativo. |
| **Sanitización de PII** | Control previo a la publicación/procesamiento para evitar el envío de datos personales sensibles a servicios externos. |
| **Google ADK como orquestador** | Motor de orquestación inicial para los flujos (no una dependencia obligatoria a largo plazo). |

---

## 3. NO entra en la primera versión (V1)

| Elemento | Motivo / Destino (V2) |
| :--- | :--- |
| **Publicación sin confirmación humana** | Va en contra del control de calidad y consistencia narrativa requerido. |
| **Otras redes sociales** | Instagram, X/Twitter, Facebook, Threads quedan excluidos para acotar el esfuerzo inicial. |
| **Formatos gráficos** | Carruseles, imágenes, quote-cards, video y Canva/Figma API quedan fuera. |
| **Formatos de texto alternativos** | Hilos de X, artículos largos, newsletters u optimización omnicanal. |
| **Analítica de rendimiento** | No se requiere hasta tener un volumen de publicaciones reales. |
| **Panel Web / Interfaz Gráfica** | La V1 se gestionará mediante interfaces de comandos (CLI) o scripts locales. |
| **Sistema multiusuario** | Se asume un único usuario/autor en el flujo inicial. |
| **Dependencia exclusiva de proveedor** | Ningún componente externo de publicación o IA debe ser el núcleo del sistema. |
| **Engagement artificial e interacciones** | Queda fuera de la V1 la automatización de likes, comentarios, conexiones, mensajes masivos, scraping y cualquier técnica de engagement artificial. |

---

## 4. Reglas de control de alcance y seguridad

1. **Principio de Verdad:** El repositorio es la fuente de verdad. No el chat, no el IDE, no Metricool ni ADK.
2. **Puertos y Adaptadores:** Toda integración externa (transcripción, LLM, publicador) se implementará mediante contratos (interfaces) que permitan el intercambio fácil de componentes.
3. **Privacidad y PII:** Los audios y transcripciones pueden contener datos sensibles o información personal identificable (PII). Debe existir una etapa de sanitización o un gate de privacidad local antes de enviar datos a LLMs remotos o adaptadores de publicación.
4. **Protección de Secretos:** No se permite registrar credenciales, tokens, contraseñas o PII en logs ni evidencias locales (`trace/`).
5. **Aislamiento en Tests:** `LocalDraftPublisher` actuará como la base de pruebas local para simular la publicación sin necesidad de conexión ni consumo de APIs de producción.
