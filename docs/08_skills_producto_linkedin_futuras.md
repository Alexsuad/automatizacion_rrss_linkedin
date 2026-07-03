# 08 — Skills de Producto LinkedIn Futuras

## 1. Propósito
Este documento define y registra el catálogo de **skills de producto futuras** planificadas para el publicador de LinkedIn V1. 

> [!IMPORTANT]
> **Regla de Planificación:** Estas skills son candidatas futuras y **no existen físicamente** en forma de archivo `SKILL.md` ni implementaciones en el entorno actual. No deben crearse hasta que se cumplan las especificaciones del contrato de entrada/salida y las validaciones del equipo de Marketing/RRSS/Product correspondientes.

---

## 2. Dictamen Marketing/RRSS/Product
```text
Dictamen: WARN

La lista preliminar servía como base, pero requería:
- añadir `extraer-idea-central-linkedin`;
- fusionar `generar-diagnostico-editorial` dentro de `revisar-calidad-editorial-linkedin`;
- renombrar las skills de publicación para evitar sugerir publicación directa (cambiar a "preparar");
- mantener hook, CTA, reputación, variantes y formato LinkedIn dentro de redacción/revisión, no como skills separadas.
```

---

## 3. Lista Final de Skills Futuras

| Skill futura | Propósito | Documento de justificación | Entradas esperadas | Salidas esperadas | Gate relacionado | Requiere Marketing/RRSS | Cuándo crear | Cuándo NO crear |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `extraer-idea-central-linkedin` | Refinar, ordenar y estructurar la intención editorial inicial o la transcripción autorizada, sin redactar todavía el post definitivo ni inventar hechos. | [02_contrato_entrada.md](02_contrato_entrada_contenido.md), [03_contrato_perfil.md](03_contrato_perfil_narrativo.md) | Transcripción limpia, idea cruda o intención editorial inicial, contexto autorizado y límites de voz. | `idea_central` en YAML (audiencia, dolor, pilar, etc.). | `gate_validar_entrada`, `gate_validar_perfil_narrativo` | Sí | Flujo audio/post repetitivo donde conviene separar interpretación editorial, normalización de intención y redacción. | Si se usa para inventar intención, hechos, audiencia o enfoque no autorizados por el input. |
| `redactar-post-linkedin` | Transformar idea editorial a borrador o reescribir ante `WARN`. | [03_contrato_perfil.md](03_contrato_perfil_narrativo.md), [06_contrato_calidad.md](06_contrato_calidad_post_linkedin.md) | Idea estructurada, perfil narrativo, diagnóstico previo. | Borrador de post de LinkedIn, variantes de hook/CTA. | `gate_calidad_editorial`, `gate_aprobacion_humana` | Sí | Exista idea estructurada y se requieran borradores legibles. | Si se pretende pasar directo de audio bruto a post. |
| `validar-voz-cliente` | Validar alineación con el perfil de estilo y voz sin inventar. | [03_contrato_perfil.md](03_contrato_perfil_narrativo.md), [06_contrato_calidad.md](06_contrato_calidad_post_linkedin.md) | Post candidato, perfil narrativo, límites de voz. | Dictamen de alineación de voz, fragmentos problemáticos. | `gate_validar_perfil_narrativo`, `gate_calidad_editorial` | Sí | Al definir perfiles narrativos reales y verificar coherencia. | Si no existe perfil narrativo documentado. |
| `verificar-trazabilidad-audio-post` | Validar que el post no introduce hechos no indicados en la voz del cliente. | [02_contrato_entrada.md](02_contrato_entrada_contenido.md), [04_contrato_salida.md](04_contrato_salida.md) | Audio/transcripción de origen, idea central, post. | Dictamen de trazabilidad, hechos adicionales. | `gate_validar_entrada`, `gate_manifest_evidencia` | Sí | Para control de riesgos de alucinación ante LLM remotos. | Si la skill general `auditar-trazabilidad-input-output` basta. |
| `revisar-calidad-editorial-linkedin` | Auditar consistencia con el contrato de calidad LinkedIn V1. | [06_contrato_calidad.md](06_contrato_calidad_post_linkedin.md) | Post candidato, perfil narrativo, restricciones. | `diagnostico_editorial` en YAML (PASS/WARN/FAIL). | `gate_calidad_editorial` | Sí | Existan posts candidatos reales y criterios claros. | Reemplazar al ojo humano o saltar gate de aprobación. |
| `preparar-borrador-local-linkedin` | Generar el kit local offline en modo dry_run. | [04_contrato_salida.md](04_contrato_salida.md), [05_fases.md](05_fases_implementacion.md) | Post aprobado, adaptador local, metadatos. | Borrador en JSON y manifest de evidencias. | `gate_aprobacion_humana`, `gate_publicacion_local` | No | Al empezar el pipeline local de simulación offline. | Sin aprobación humana previa o contrato de salida. |
| `preparar-programacion-metricool-linkedin` | Preparar payload para adaptador Metricool, en modo simulado o futuro modo real, siempre después de aprobación humana. | [01_alcance.md](01_alcance_si_no.md), [04_contrato_salida.md](04_contrato_salida.md), [05_fases.md](05_fases_implementacion.md) | Post aprobado, adaptador externo, credenciales seguras. | Payload del adaptador, ID de publicación externa. | `gate_aprobacion_humana`, `gate_no_secretos` | No | Validado el flujo local offline y se active fase de publicación. | Antes de LocalDraftPublisher, sin gate humano o secretos. |

---

### Relación entre `intencion_editorial` e `idea_central`

`intencion_editorial` puede llegar como insumo inicial desde el contrato de entrada. Puede estar completa, parcial o tentativa (declarado de forma explícita mediante el campo `estado_intencion_editorial`).

La skill futura `extraer-idea-central-linkedin` no reemplaza ese contrato ni inventa una intención nueva. Su función es refinar, ordenar y normalizar la intención autorizada para producir una idea editorial estructurada antes de redactar el post.

Si la `intencion_editorial` ya está completa, la skill debe validar consistencia, detectar riesgos de interpretación y devolver una estructura normalizada.

Si la `intencion_editorial` está marcada como `parcial` o `tentativa`, la skill puede derivar u ordenar una idea editorial desde la transcripción o idea cruda, pero sin inventar información y utilizando solo el contenido autorizado en el input.

---

### Especificación Detallada de Campos de Salida

#### `extraer-idea-central-linkedin`
```yaml
idea_central:
audiencia_objetivo:
dolor_o_tension:
angulo_editorial:
pilar_contenido:
tipo_de_post:
ideas_descartadas:
riesgos_de_interpretacion:
```

El esquema oficial de `diagnostico_editorial` vive en [06_contrato_calidad_post_linkedin.md](06_contrato_calidad_post_linkedin.md). La skill futura `revisar-calidad-editorial-linkedin` debe usar ese esquema sin duplicarlo.

---

## 4. Skills Explícitamente Fusionadas o Descartadas en V1
*   `generar-diagnostico-editorial` **no se crea como skill independiente en V1.** El diagnóstico editorial estructurado se integra como salida obligatoria dentro de la revisión efectuada por la skill `revisar-calidad-editorial-linkedin`.
*   Las siguientes habilidades conceptuales de marketing no se estructuran como skills separadas, sino que **viven dentro de la lógica de redacción o revisión editorial** para evitar redundancia técnica:
    *   `generar-variantes-linkedin`
    *   `adaptar-formato-linkedin`
    *   `validar-hook-linkedin`
    *   `validar-cta-linkedin`
    *   `validar-reputacion-linkedin`

---

## 5. Skills que NO deben crearse en V1
Quedan fuera del alcance inicial de la V1 las siguientes automatizaciones:
*   `generar-hashtags-linkedin`
*   `optimizar-viralidad-linkedin`
*   `automatizar-comentarios`
*   `responder-comentarios`
*   `generar-menciones`
*   `buscar-personas-para-etiquetar`
*   `automatizar-likes`
*   `automatizar-conexiones`
*   `automatizar-dms`
*   `extraer-tendencias-linkedin`
*   `crear-carrusel-instagram`
*   `crear-imagen-post`
*   `adaptar-post-instagram`
*   `adaptar-post-twitter`
*   `analizar-metricas-avanzadas`

---

## 6. Reglas para Crear estas Skills en el Futuro
1.  **Gobernanza:** Ejecutar la skill `crear-skill-desde-contrato` antes de redactar cualquier especificación física `SKILL.md`.
2.  **Validación de Arquitectura:** Invocar la skill `decidir-tipo-pieza-sistema-agentico` para evaluar si la funcionalidad corresponde a una skill, un script determinista Python, un gate, una regla, o un workflow.
3.  **Control Humano:** Ninguna skill de preparación o programación de publicación puede ejecutarse sin la confirmación explícita del `gate_aprobacion_humana`.
4.  **Alineación Editorial:** Toda skill de redacción, validación de voz o diagnóstico requiere revisión editorial/funcional y aprobación previa del equipo de Marketing/RRSS.
5.  **Desacoplamiento:** Ninguna skill debe invocar o acoplarse directamente a librerías de proveedores externos (Gemini SDK, OpenAI SDK, ADK orquestador, LiteLLM, Faster-Whisper, Metricool API) en el dominio.
6.  **Reutilización:** Si una necesidad del flujo puede cubrirse con una skill de gobernanza global ya provista en `.agents/skills/`, no se permite duplicar funcionalidad localmente.
7.  **Variantes:** El alcance en V1 de variantes de redacción se limita a pruebas selectivas del hook o el CTA. No se deben generar paquetes múltiples de posts completos alternativos.
