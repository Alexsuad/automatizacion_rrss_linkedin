# 06 — Contrato de Calidad del Post LinkedIn V1

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
*   **FAIL crítico (No levantable por aprobación simple):** Bloqueos graves que impiden la publicación automática. Si existe un FAIL crítico abierto, el post debe ser modificado o regenerado obligatoriamente; la aprobación humana no puede levantar estos estados por sí sola.

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

Esta microfase solo refuerza el contrato editorial. No implementa todavía el gate operativo completo de publicabilidad. La conversión final entre diagnóstico + aprobación humana y `estado_publicabilidad` corresponde a una fase posterior.

---

## 7. Criterios de Veredicto
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

