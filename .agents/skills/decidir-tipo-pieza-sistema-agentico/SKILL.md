---
name: decidir-tipo-pieza-sistema-agentico
description: Usar antes de crear una nueva pieza del sistema agéntico para decidir si la necesidad corresponde a skill, script, skill+script, gate, regla, workflow, subagente, MCP, ajuste documental o si no debe crearse nada.
---

# Decidir tipo de pieza del sistema agéntico

## Propósito
Decidir la pieza mínima y correcta para resolver una necesidad nueva sin sobredimensionar el sistema.

## Cuándo usarla
Usar antes de:
*   Crear una nueva pieza del sistema agéntico o proponer cambios de arquitectura.
*   Decidir si una demanda ya queda cubierta por una pieza existente.

## Cuándo NO usarla
No usarla para:
*   Implementar la pieza, redactar contenido final, o abrir/saltarse gates.
*   Sustituir una auditoría de cierre o validación técnica ya definida.

## Entradas
*   Necesidad detectada y objetivo operativo.
*   Fase vigente, alcance y restricciones activas.
*   Piezas existentes, determinismo requerido e integración de herramientas.

## Salidas
*   `TIPO_RECOMENDADO`
*   `PIEZA_PROPUESTA`
*   `RAZON`
*   `ALTERNATIVAS_DESCARTADAS`
*   `RIESGO_SI_SE_CREA_MAL`
*   `EVIDENCIA_REQUERIDA`
*   `DECISION_HUMANA_REQUERIDA`
*   `DICTAMEN`

## Criterios de Decisión
*   **SKILL:** Requiere juicio experto, interpretación semántica, redacción o análisis del dominio.
*   **SCRIPT:** Comprobación determinista exacta (formatos, existencia de archivos, conteos, YAML/JSON).
*   **SKILL + SCRIPT:** Combina criterio semántico de evaluación y validación de sintaxis exacta.
*   **GATE:** Control de avance de fase o transición crítica (aprobación o bloqueo).
*   **REGLA:** Restricción transversal permanente aplicable a todo el sistema.
*   **WORKFLOW:** Secuencia repetible estable de múltiples etapas.
*   **SUBAGENTE:** Autonomía propia persistente con capacidad de veto y contexto propio.
*   **MCP:** Consulta o acción recurrente sobre herramienta externa viva.
*   **AJUSTE_DOCUMENTAL:** Registro de decisiones aclaratorias en documentos existentes.
*   **NO_CREAR:** Duplica funciones, no aporta control, sobredimensiona el sistema o es de fase futura.

## Matriz de Decisión Compacta
| Señal dominante | Tipo probable | Regla práctica |
| --- | --- | --- |
| Juicio experto, lectura ambigua, análisis | `SKILL` | Priorizar si depende de interpretación semántica |
| Verificación exacta, formato, conteos, JSON | `SCRIPT` | Priorizar si debe ser reproducible y exacto |
| Parte semántica + parte exacta | `SKILL + SCRIPT` | Separar lógica experta y verificación |
| Aprobación/bloqueo de fase o control | `GATE` | Punto de control, no ejecutor operativo |
| Restricción transversal permanente | `REGLA` | Restricción global del sistema |
| Duplicado, exceso o fase futura | `NO_CREAR` | Frenar la creación |

## Pasos Obligatorios
1.  Identificar la necesidad real y separar lo experto de lo exacto.
2.  Comparar con piezas existentes para evitar duplicidades.
3.  Determinar la pieza mínima suficiente y registrar alternativas descartadas.
4.  Explicar riesgos de diseño erróneo y emitir dictamen.

## Formato de Respuesta
```text
TIPO_RECOMENDADO:
PIEZA_PROPUESTA:
RAZON:
ALTERNATIVAS_DESCARTADAS:
RIESGO_SI_SE_CREA_MAL:
EVIDENCIA_REQUERIDA:
DECISION_HUMANA_REQUERIDA: SI/NO
DICTAMEN:
```

## Valores Permitidos para DICTAMEN
`CREAR_SKILL` | `CREAR_SCRIPT` | `CREAR_SKILL_Y_SCRIPT` | `CREAR_GATE` | `CREAR_REGLA` | `CREAR_WORKFLOW` | `CREAR_SUBAGENTE` | `CREAR_MCP` | `HACER_AJUSTE_DOCUMENTAL` | `NO_CREAR` | `REQUIERE_DECISION_HUMANA` | `CREAR_GATE_Y_SCRIPT` | `CREAR_SKILL_Y_GATE` | `CREAR_REGLA_Y_GATE` | `CREAR_WORKFLOW_Y_GATE`

## Ejemplos de Referencia
Consulte el archivo de referencias [ejemplos.md](references/ejemplos.md) para revisar casos específicos resueltos con esta matriz.

## Criterio de Cierre
La skill queda cerrada cuando el dictamen emitido define sin ambigüedad la pieza mínima adecuada.

## Evidencia Mínima
Necesidad analizada, piezas existentes comparadas, tipo recomendado, alternativas descartadas y riesgo evaluado.

## Prohibiciones
*   No redactar contenido final del proyecto ni abrir/aprobar/saltar gates.
*   No decidir por sí sola asuntos de negocio, marketing, seguridad ni arquitectura crítica.
*   No crear subagentes para envolver una simple skill, ni convertir hipótesis en hechos.
