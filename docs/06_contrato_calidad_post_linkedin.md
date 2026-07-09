# 06 — Contrato de Calidad del Post LinkedIn V1

> [!NOTE]
> Este documento sigue siendo útil como contrato de calidad para el primer canal operativo.
> No debe interpretarse como contrato universal de todos los canales futuros del sistema portable.

## 1. Objetivo
Este contrato define los criterios operativos mínimos para aceptar, corregir o rechazar un post generado para LinkedIn en V1. Su función es evitar contenido genérico, artificial, sin trazabilidad o riesgoso.

---

## 2. Principio de Aceptación
Un post es aceptable si cumple:
*   Tiene idea central clara y audiencia definida.
*   Respeta el perfil narrativo del cliente.
*   Es legible en móvil (párrafos de máximo 2-3 líneas, sin bloques densos, escaneable).
*   Evita frases genéricas de IA y CTAs artificiales.
*   No inventa datos, hechos, experiencia ni autoridad.
*   No genera riesgo reputacional ni viola compliance.
*   Todo post requiere aprobación humana explícita antes de programarse o publicarse.

---

## 3. Intención Editorial Mínima (Metadata)
Todo post debe declarar esta metadata interna de sistema (invisible al público y útil para control):
```yaml
audiencia_objetivo:
objetivo_del_post:
pilar_contenido:
tipo_de_post:          # Clasificación conceptual (ej: aprendizaje, opinión, caso, error, reflexión, educativo, venta suave)
dolor_o_tension:
idea_central:
cta_intencionado:
nivel_de_promocion:    # nulo | bajo | medio | alto
```

---

## 4. Checklist Mínimo de Calidad
*   ¿La idea central se entiende rápido?
*   ¿El tono coincide con el perfil narrativo del cliente sin inventar vivencias?
*   ¿El hook y el CTA son naturales y evitan fórmulas genéricas de IA (ej. "En un mundo donde...", "Comenta SÍ")?
*   ¿Tiene recomendación horaria razonable?

---

## 5. Bloqueos Levantables y No Levantables (FAIL Crítico)
*   **WARN editorial (Levantables):** Criterios de estilo mejorables (ej: hook débil, CTA genérico, pilar poco claro). Se pueden subsanar mediante aprobación humana reforzada.
*   **FAIL crítico (No levantable por aprobación simple):** Bloqueos graves que impiden que la pieza avance a una salida operativa o preparación de publicación. Si existe un FAIL crítico abierto, el post debe ser modificado o regenerado obligatoriamente; la aprobación humana no puede levantar estos estados por sí sola.

Son considerados **FAIL crítico no levantable**:
*   PII expuesta (datos personales sensibles).
*   Secretos o credenciales expuestos en los logs o el kit.
*   Claims de datos/cifras sin fuente o promesas exageradas.
*   Riesgo reputacional alto para el cliente.
*   Incumplimiento de compliance de canal (ej. automatizaciones de interacciones).
*   Falta de trazabilidad directa con el input original (el post inventa experiencia personal o autoridad no presente en la entrada).
*   Intento de publicación o programación en vivo omitiendo la aprobación humana.

---

## 6. Diagnóstico Editorial Mínimo
Cada post debe incluir obligatoriamente este diagnóstico estructurado de calidad:
```yaml
diagnostico_editorial:
  claridad_idea: PASS | WARN | FAIL
  audiencia: PASS | WARN | FAIL
  hook: PASS | WARN | FAIL
  voz_cliente: PASS | WARN | FAIL
  autenticidad: PASS | WARN | FAIL
  cta: PASS | WARN | FAIL
  compliance: PASS | WARN | FAIL
  riesgo_generico: bajo | medio | alto
  estado_revision: PASS | WARN | FAIL  # Será FAIL obligatorio si hay algún bloqueo crítico
  motivo: "Explicación breve del veredicto"
  ajustes_recomendados: "Detalles correctivos sugeridos"
  bloqueos_criticos:
    - tipo: PII | SECRETO | CLAIM_SIN_FUENTE | RIESGO_REPUTACIONAL | COMPLIANCE | TRAZABILIDAD | SIN_APROBACION
      descripcion: "Detalle del bloqueo crítico detectado"
```

`bloqueos_criticos` agrupa bloqueos editoriales graves que impiden considerar el contenido publicable. Si la lista no está vacía, `estado_revision` debe quedar en `FAIL`.

El contrato editorial define criterios y bloqueos, y la resolución operativa de publicabilidad ya existe en `validators/publicacion.py`. Allí, los bloqueos críticos, `FAIL` editorial, riesgo alto, `compliance` `FAIL`, `autenticidad` `FAIL` y `diagnostico_trazabilidad` `FAIL` terminan en `rechazado_editorial`. En V1 esto no implica publicación real ni programación externa.

---

## 7. Trazabilidad Fuerte (Etapa S)
La Etapa S incorpora un criterio adicional de trazabilidad fuerte entre entrada original, idea central, contexto permitido y `PostLinkedIn` o salida candidata equivalente existente en el pipeline.

Su objetivo es validar de forma determinista y offline que el contenido no avance cuando introduce información sensible o de riesgo no soportada por la evidencia disponible.

El alcance de esta etapa es deliberadamente acotado:
*   No busca detectar todas las afirmaciones del texto.
*   Solo valida afirmaciones explícitas sensibles o de riesgo:
    *   cifras;
    *   logros;
    *   autoridad;
    *   experiencia personal;
    *   promesas;
    *   claims técnicos o comerciales;
    *   referencias a cliente o contexto.

Estados propuestos del diagnóstico de trazabilidad:
*   **PASS:** No hay hallazgos y el post se mantiene dentro del soporte explícito permitido.
*   **WARN:** Solo existen hallazgos de tipo `inferencia_debil`.
*   **FAIL:** Existe al menos un hallazgo crítico no soportado.

Tipos de hallazgos propuestos:
*   `hecho_no_soportado`
*   `autoridad_fingida`
*   `anecdota_inventada`
*   `cifra_no_soportada`
*   `promesa_excesiva`
*   `claim_sin_fuente`
*   `inferencia_debil`
*   `contradiccion_con_contexto`

Reglas propuestas de bloqueo:
*   `FAIL` si aparece cualquiera de estos hallazgos: `hecho_no_soportado`, `autoridad_fingida`, `anecdota_inventada`, `cifra_no_soportada`, `promesa_excesiva`, `claim_sin_fuente` o `contradiccion_con_contexto`.
*   `WARN` si el único hallazgo presente es `inferencia_debil`.
*   `PASS` si no se detectan hallazgos y el contenido permanece trazable a la entrada, la idea central y el contexto permitido.

`SIN_APROBACION` no es un hallazgo de trazabilidad. Pertenece al gate humano y a la resolución de publicabilidad, no al análisis de soporte contenido → evidencia.

La integración efectiva ocurre después de la generación del post candidato, antes de la aprobación humana, antes de resolver `estado_publicabilidad` y antes de persistir `LocalDraft`. Esta etapa ya cuenta con contratos Python, validador determinista, integración de flujo y persistencia controlada en `LocalDraftPublisher`.

---

## 8. Criterios de Veredicto
*   **PASS:** Cumple el alcance, tiene idea clara, respeta la voz del autor y está libre de riesgos de compliance o PII.
*   **WARN:** Cumple parcialmente pero tiene riesgos editoriales menores. Requiere revisión y aprobación humana reforzada.
*   **FAIL:** Contiene algún bloqueo crítico o no cumple la idea central básica. Debe corregirse obligatoriamente en el origen.
*   **BLOQUEADO:** Detiene el flujo técnico ante la falta de metadatos mínimos, presencia de bloqueos críticos o falta de gate humano.


## Señales rápidas de rechazo editorial

Marcar `WARN` si:
- el hook es débil pero corregible;
- el CTA es genérico pero no manipulador;
- el pilar de contenido no está claro;
- el post es publicable, pero suena poco específico.

Marcar `FAIL` si:
- el post inventa experiencia personal;
- usa cifras o resultados sin fuente;
- empuja engagement artificial;
- contradice el perfil narrativo;
- contiene PII, secretos o datos sensibles;
- no se puede explicar qué idea del audio originó el post.
