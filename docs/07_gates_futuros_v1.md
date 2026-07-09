# 07 — Gates Futuros del Sistema V1

> [!NOTE]
> Este documento es **derivado** y no define la visión principal del producto.
> Debe leerse después de `docs/00`, `docs/01`, `docs/05` y `docs/09`.

## 1. Propósito
Este documento define y cataloga los **gates** derivados del primer flujo operativo centrado en publicaciones de texto y salida local segura. Estos gates actúan como puntos de control para validar la consistencia, calidad, privacidad y portabilidad del flujo antes de avanzar entre fases de ejecución.

## 2. Regla Operativa Base
> [!IMPORTANT]
> Los gates deterministas básicos ya han sido implementados como validadores deterministas offline en la base de código (`src/linkedin_content_system/validators/`). Las llamadas a LLM y adaptadores de red continúan siendo simuladas.

---

## 3. Matriz de Gates

| Gate | Tipo | Propósito | Documento de Justificación | Momento del Flujo | PASS | WARN | FAIL | BLOQUEADO |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gate_validar_entrada` | `híbrido` | Validar que la entrada tenga audio/transcripción, metadatos mínimos e intención editorial obligatoria. | [02_contrato_entrada_contenido.md](02_contrato_entrada_contenido.md) | Antes de generar el post. | Tiene entrada física, metadatos y canal `linkedin`. | Advertencias menores de privacidad no críticas. | Entrada o transcripción vacía o no sanitizada. | BLOQUEADO si no existe bloque `intencion_editorial`, si falta `estado_intencion_editorial`, o si no hay insumo suficiente autorizado para normalizar una intención parcial/tentativa. |
| `gate_validar_perfil_narrativo` | `híbrido` | Validar que existe perfil narrativo estructurado suficiente para respetar la voz y tono del cliente. | [03_contrato_perfil_narrativo.md](03_contrato_perfil_narrativo.md) | Antes de redactar o adaptar el tono. | Perfil completo y con campos obligatorios poblados. | Perfil requiere revisión menor pero tiene datos usables. | Faltan campos esenciales de voz de marca o CTA. | Perfil inexistente o marcado como incompleto. |
| `gate_no_pii` | `híbrido` | Evitar la exposición de datos personales en el post y el kit. | [02_contrato_entrada_contenido.md](02_contrato_entrada_contenido.md), [04_contrato_salida.md](04_contrato_salida.md), [AGENTS.md](../AGENTS.md) | Antes de guardar evidencia. | Confirmación de sanitización completa sin PII detectada. | Advertencias de privacidad leves en transcripción privada. | Detección de posibles datos personales en campos públicos. | PII crítica sin sanitizar (credenciales, teléfonos, correos) detectada en post o campos de texto libre de salida. |
| `gate_calidad_editorial` | `LLM + humano` | Validar que el post cumple intención editorial, calidad, voz, hook, CTA y reputación. | [06_contrato_calidad_post_linkedin.md](06_contrato_calidad_post_linkedin.md) | Después de generar el post. | Diagnóstico completo en `PASS` y riesgo reputacional bajo. | Advertencias menores de hook/CTA mejorables. | Uno o más campos del diagnóstico en `FAIL`, compliance en `FAIL`, autenticidad en `FAIL` o presencia de bloqueos críticos. | Riesgo reputacional alto o post no defendible. |
| `gate_aprobacion_humana` | `humano` | Bloquear la publicación/programación si no existe aprobación humana explícita. | [04_contrato_salida.md](04_contrato_salida.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Antes de cualquier publicación o programación. | Confirmación explícita firmada de aprobación del post. | N/A (Gate binario). | Post rechazado por el usuario con comentarios. | Falta de registro de aprobación o estado en `pendiente`. |
| `gate_publicacion_local` | `script` | Validar que la primera prueba se realiza con LocalDraftPublisher offline y no con adaptador real. | [01_alcance_si_no.md](01_alcance_si_no.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Primera ejecución end-to-end local. | Adaptador activo configurado como `localdraft` en `dry_run`. | N/A. | Configuración local incorrecta. | Intento de conexión o publicación en vivo vía API real. |
| `gate_no_secretos` | `script` | Bloquear credenciales, claves API o secretos en la salida, evidencia o repositorio. | [AGENTS.md](../AGENTS.md), [ADR-000_Decisiones_Tecnicas_Base.md](architecture/ADR-000_Decisiones_Tecnicas_Base.md) | Antes de guardar evidencia. | Ausencia total de secretos en trazas y evidencias. | N/A. | Claves API de prueba en trazas públicas. | Claves reales, contraseñas o tokens expuestos. |
| `gate_no_rutas_absolutas` | `script` | Bloquear rutas locales absolutas o referencias al entorno local del desarrollador. | [AGENTS.md](../AGENTS.md) | Antes de cerrar cualquier tarea técnica o documental. | Rutas relativas y portables comprobadas. | N/A. | N/A. | Presencia de rutas absolutas del sistema o referencias de entorno local en evidencias. |
| `gate_manifest_evidencia` | `script` | Validar que cada ejecución relevante genera su manifest de salida con los datos del flujo. | [04_contrato_salida.md](04_contrato_salida.md), [05_fases_implementacion.md](05_fases_implementacion.md), [AGENTS.md](../AGENTS.md) | Al cierre de ejecución local o publicación programada. | Manifest (`salida_v1.json`) guardado con campos poblados. | Evidencia secundaria o logs parciales. | Estructura del manifest inválida o incompleta. | Ausencia del manifest o falta de registro del adaptador. |

---

## 4. Estado de Implementación
*   **Fase Actual:** Los gates deterministas (privacidad, estructural, manifest, no secretos y no rutas absolutas) están implementados a nivel de código en `src/linkedin_content_system/validators/`.
*   **Límites:** Ningún gate tiene autorización para publicar, programar o modificar contenido por sí solo; su única responsabilidad es emitir un veredicto de validación (`PASS`, `WARN`, `FAIL`, `BLOQUEADO`).
*   **Prueba Inicial:** La primera validación real y offline del sistema se ejecuta obligatoriamente con `LocalDraftPublisher`.
