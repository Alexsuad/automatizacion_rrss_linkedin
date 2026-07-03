# 07 — Gates Futuros del Sistema V1

## 1. Propósito
Este documento define y cataloga los **gates candidatos futuros** del sistema de automatización de publicaciones para LinkedIn V1. Estos gates actuarán como puntos de control para validar la consistencia, calidad, privacidad y portabilidad del flujo antes de avanzar entre fases de ejecución.

## 2. Regla Operativa Base
> [!IMPORTANT]
> Los gates aquí descritos son **candidatos futuros**. No son ejecutables en la fase de planeación pre-código actual y no deben programarse hasta recibir la orden de inicio de implementación técnica.

---

## 3. Matriz de Gates Candidatos

| Gate Futuro | Tipo Futuro | Propósito | Documento de Justificación | Momento del Flujo | PASS | WARN | FAIL | BLOQUEADO |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gate_validar_entrada` | `híbrido` | Validar que la entrada tenga audio/transcripción, metadatos mínimos e intención editorial obligatoria. | [02_contrato_entrada_contenido.md](02_contrato_entrada_contenido.md) | Antes de generar el post. | Tiene entrada física, metadatos y canal `linkedin`. | Advertencias menores de privacidad no críticas. | Entrada o transcripción vacía o no sanitizada. | BLOQUEADO si no existe bloque `intencion_editorial`, si falta `estado_intencion_editorial`, o si no hay insumo suficiente autorizado para normalizar una intención parcial/tentativa. |
| `gate_validar_perfil_narrativo` | `híbrido` | Validar que existe perfil narrativo estructurado suficiente para respetar la voz y tono del cliente. | [03_contrato_perfil_narrativo.md](03_contrato_perfil_narrativo.md) | Antes de redactar o adaptar el tono. | Perfil completo y con campos obligatorios poblados. | Perfil requiere revisión menor pero tiene datos usables. | Faltan campos esenciales de voz de marca o CTA. | Perfil inexistente o marcado como incompleto. |
| `gate_no_pii` | `híbrido` | Evitar exposición de datos personales, credenciales o información sensible. | [02_contrato_entrada_contenido.md](02_contrato_entrada_contenido.md), [04_contrato_salida.md](04_contrato_salida.md), [AGENTS.md](../AGENTS.md) | Antes de guardar evidencia, enviar a adaptador o publicar. | Confirmación de sanitización completa sin PII detectada. | Advertencias de privacidad leves en transcripción privada. | Detección de posibles datos personales en campos públicos. | PII crítica sin sanitizar (credenciales, teléfonos, correos). |
| `gate_calidad_editorial` | `LLM + humano` | Validar que el post cumple intención editorial, calidad, voz, hook, CTA y reputación. | [06_contrato_calidad_post_linkedin.md](06_contrato_calidad_post_linkedin.md) | Después de generar el post y antes de aprobación humana. | Diagnóstico completo en `PASS` y riesgo reputacional bajo. | Advertencias menores de hook/CTA mejorables. | Uno o más campos del diagnóstico en `FAIL`. | Riesgo reputacional alto o post no defendible. |
| `gate_aprobacion_humana` | `humano` | Bloquear la publicación/programación si no existe aprobación humana explícita. | [04_contrato_salida.md](04_contrato_salida.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Antes de cualquier publicación o programación. | Confirmación explícita firmada de aprobación del post. | N/A (Gate binario). | Post rechazado por el usuario con comentarios. | Falta de registro de aprobación o estado en `pendiente`. |
| `gate_publicacion_local` | `script` | Validar que la primera prueba se realiza con LocalDraftPublisher offline y no con adaptador real. | [01_alcance_si_no.md](01_alcance_si_no.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Primera ejecución end-to-end local. | Adaptador activo configurado como `localdraft` en `dry_run`. | N/A. | Configuración local incorrecta. | Intento de conexión o publicación en vivo vía API real. |
| `gate_no_secretos` | `script` | Bloquear credenciales, claves API o secretos en la salida, evidencia o repositorio. | [AGENTS.md](../AGENTS.md), [ADR-000_Decisiones_Tecnicas_Base.md](architecture/ADR-000_Decisiones_Tecnicas_Base.md) | Antes de cerrar tareas, guardar evidencia o integrar adaptadores. | Ausencia total de secretos en trazas y evidencias. | N/A. | Claves API de prueba en trazas públicas. | Claves reales, contraseñas o tokens expuestos. |
| `gate_no_rutas_absolutas` | `script` | Bloquear rutas locales absolutas o referencias al entorno local del desarrollador. | [AGENTS.md](../AGENTS.md) | Antes de cerrar cualquier tarea técnica o documental. | Rutas relativas y portables comprobadas. | N/A. | N/A. | Presencia de rutas absolutas (`file:///`, `/home/`, etc.) en evidencias. |
| `gate_manifest_evidencia` | `script` | Validar que cada ejecución relevante genera su manifest de salida con los datos del flujo. | [04_contrato_salida.md](04_contrato_salida.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Al cierre de ejecución local o publicación programada. | Manifest (`salida_v1.json`) guardado con campos poblados. | Evidencia secundaria o logs parciales. | Estructura del manifest inválida o incompleta. | Ausencia del manifest o falta de registro del adaptador. |

---

## 4. Reglas de Implementación Futura
*   **Fase Actual:** Ninguno de los gates anteriores se implementa en esta fase. Queda prohibida la creación de archivos en `.agents/gates/` o la escritura de código para validadores.
*   **Diseño:** Los gates no se convertirán automáticamente en scripts. La decisión de si un gate se implementa como script Python determinista, como llamada estructurada a LLM (flexible), aprobación humana interactiva, o una combinación, se tomará utilizando la skill `decidir-tipo-pieza-sistema-agentico`.
*   **Límites:** Ningún gate tiene autorización para publicar, programar o modificar contenido por sí solo; su única responsabilidad es emitir un veredicto de validación (`PASS`, `WARN`, `FAIL`, `BLOQUEADO`).
*   **Prueba Inicial:** La primera validación real y offline del sistema se ejecutará obligatoriamente con `LocalDraftPublisher`.
