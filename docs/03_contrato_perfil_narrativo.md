# 03 — Contrato de perfil narrativo

## 1. Propósito del documento

Este documento define la estructura y el contrato genérico del **perfil narrativo**, que sirve para parametrizar el tono, estilo, reglas y restricciones de escritura del autor para los posts de LinkedIn generados, asegurando que el contenido mantenga la identidad única del creador.

> [!IMPORTANT]
> **Contrato y no Perfil Concreto:** Este documento no representa el perfil de un cliente real concreto ni sus valores por defecto, sino las reglas estructurales (el contrato de datos) que cualquier perfil narrativo de cliente debe implementar.
> 
> **Regla de desacoplamiento de contexto:** El contexto específico de cada cliente (historial, detalles del autor, etc.) debe vivir fuera del core reutilizable, en una sede intercambiable como `contexto_cliente.md`, `perfil_narrativo_cliente.md` o equivalente.

---

## 2. Estructura conceptual del Perfil Narrativo

Cada perfil narrativo se almacena localmente en JSON o YAML y debe seguir la siguiente estructura conceptual (los valores son ejemplos ilustrativos y no definen valores por defecto del core):

```json
{
  "id_perfil": "ejemplo_perfil_narrativo",
  "autor": "Nombre del Creador",
  "plataforma": "linkedin",
  "estado_perfil_narrativo": "COMPLETO",
  "voz_marca": {
    "tono_base": {
      "descripcion": "Ej: Analítico pero directo, enfocado en metodología práctica.",
      "ejemplos": ["Basado en la prueba de ayer, descubrimos que..."]
    },
    "tono_prohibido": {
      "descripcion": "Evitar tono motivacional vacío y jerga corporativa inflada.",
      "ejemplos": ["¡Hola red! Hoy estoy súper emocionado de anunciar disruptivamente..."]
    },
    "nivel_opinion_personal": {
      "valor": "medio",
      "criterio": "Dar opinión respaldada por datos de proyectos propios."
    },
    "nivel_tecnicismo": {
      "valor": "alto",
      "criterio": "Usar términos del sector si aportan claridad al lector técnico."
    },
    "nivel_cercania": {
      "valor": "alto",
      "criterio": "Tratar de tú al lector de forma directa."
    },
    "nivel_promocional": {
      "valor": "bajo",
      "criterio": "Sólo mencionar el producto como solución al final de un caso útil."
    }
  },
  "temas": {
    "permitidos": ["diseño modular", "patrones de diseño", "desarrollo ágil"],
    "prohibidos": ["política", "finanzas personales", "opiniones médicas"],
    "sensibles": ["casos de estudio sin anonimizar"]
  },
  "lenguaje": {
    "palabras_frecuentes": ["modularidad", "flujo", "componente"],
    "expresiones_propias": ["la simplicidad es clave", "sin pasos manuales"],
    "palabras_a_evitar": ["disruptivo", "sinergia", "revolucionar"],
    "frases_prohibidas": [
      "En un mundo donde…",
      "No es solo X, es Y…",
      "¿Sabías que…?",
      "La clave del éxito es…",
      "Hoy quiero hablarte de…",
      "En la era digital…"
    ]
  },
  "autenticidad": {
    "experiencias_que_puede_usar": ["Proyectos propios de desarrollo en local", "Tests de rendimiento"],
    "experiencias_que_no_debe_inventar": ["Años de experiencia con clientes que no posee", "Cifras de negocio ficticias"],
    "ejemplos_si_suena": ["Ayer probé a correr el servidor local..."],
    "ejemplos_no_suena": ["Como líder visionario de una corporación global..."]
  },
  "cta": {
    "cta_preferidos": ["preguntar por desacuerdo razonado", "sugerir guardar si es una guía útil"],
    "cta_prohibidos": ["Comenta SÍ", "Comenta INFO", "Dale like si estás de acuerdo", "Sígueme para más consejos"],
    "condiciones_para_dm": ["Solo cuando se ofrezca acceso a una demo técnica privada"]
  }
}
```

---

## 3. Contrato de Voz de Marca

El perfil narrativo no debe limitarse a definir un tono general. Debe permitir que el sistema distinga entre un texto genérico y un texto que suena auténticamente al cliente.

Todo perfil narrativo debe declarar, como mínimo, los campos indicados en la clave `voz_marca` de la estructura conceptual (incluyendo `tono_base`, `tono_prohibido`, `nivel_opinion_personal`, `nivel_tecnicismo`, `nivel_cercania`, y `nivel_promocional`). Si estos campos están vacíos o son genéricos, el perfil narrativo debe considerarse incompleto.

---

## 4. Temas Permitidos y Prohibidos

El sistema no debe asumir que cualquier tema relacionado con el sector del cliente es válido. Cada perfil narrativo debe declarar la clave `temas`.

*   **Tema prohibido:** Si el post resultante trata un tema prohibido, debe marcarse como `FAIL`.
*   **Tema sensible:** Si trata un tema sensible, debe marcarse como `WARN` y requerir aprobación humana explícita antes de publicarse.

---

## 5. Lenguaje Propio del Cliente

El sistema debe conservar señales de lenguaje que hagan reconocible al cliente. Cada perfil narrativo debe incluir la clave `lenguaje` con palabras frecuentes, expresiones propias, palabras a evitar y frases prohibidas por defecto.

---

## 6. Autenticidad y Experiencia

El sistema no debe inventar vivencias, autoridad, resultados ni historias personales.
*   El sistema solo puede usar experiencias aportadas por el audio, briefing, historial aprobado o perfil narrativo.
*   Si una experiencia no está documentada, no debe presentarse como vivencia personal.
*   Si el post inventa experiencia personal, debe marcarse obligatoriamente como `FAIL`.

---

## 7. Preferencias de CTA

El perfil narrativo no debe definir un CTA genérico por defecto. El CTA debe depender de la intención editorial del post (audiencia, objetivo del post, pilar de contenido, tipo de post, nivel promocional y perfil narrativo).

Se prohíben explícitamente los CTAs diseñados para manipular engagement artificial (ej: "Comenta INFO", "Sígueme para más consejos").

---

## 8. Criterio de Completitud

Un perfil narrativo está completo solo si permite responder:
*   ¿Cómo debe sonar el cliente? ¿Cómo no debe sonar?
*   ¿Qué temas puede tratar? ¿Qué temas debe evitar?
*   ¿Qué nivel de opinión puede usar? ¿Qué nivel técnico puede manejar?
*   ¿Qué frases o tonos están prohibidos?
*   ¿Qué ejemplos sí representan su voz? ¿Qué ejemplos no representan su voz?
*   ¿Qué CTAs son coherentes con su estilo?

Si el perfil no permite responder estas preguntas, no debe usarse para la generación automática de posts.

```yaml
estado_perfil_narrativo: COMPLETO | INCOMPLETO | REQUIERE_REVISION
```
