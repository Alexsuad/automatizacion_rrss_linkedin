---
name: crear-skill-desde-contrato
description: Usar para redactar un SKILL.md nuevo solo cuando exista un contrato aprobado que justifique crear una skill y defina propósito, entradas, salidas, límites, evidencia y criterios de cierre.
---

# Crear skill desde contrato

## Propósito
Redactar una nueva skill únicamente cuando ya existe un contrato aprobado que justifica su creación.

## Cuándo usarla
Usarla solo después de:
*   `decidir-tipo-pieza-sistema-agentico` con dictamen favorable para crear skill.
*   Dictamen de necesidad emitido por revisión humana o regla.
*   Contrato mínimo aprobado por decisión humana.

## Cuándo NO usarla
No usarla para:
*   Decidir si una skill hace falta.
*   Casos de script, gate, regla, workflow, subagente, MCP o ajuste documental.
*   Si falta el contrato.

## Precondiciones Obligatorias
*   Dictámenes previos de necesidad y nombre de skill aprobado.
*   Propósito, entradas/salidas, límites y criterios de cierre definidos.
*   Si falta alguna, devolver `NO_CREAR_SKILL_CONTRATO_INCOMPLETO`.

## Entradas
*   Contrato aprobado y nombre de skill.
*   Propósito, entradas, salidas y límites.
*   Ejemplos de uso y restricciones del proyecto.

## Salidas
*   SKILL.md propuesto.
*   Dictamen y riesgos de diseño.
*   Evidencia requerida y decisión humana requerida.

## Estructura Obligatoria de SKILL.md
*   Frontmatter válido.
*   Propósito, cuándo usar/no usar, entradas y salidas.
*   Pasos obligatorios y criterios de calidad.
*   Formato de respuesta, ejemplos y criterio de cierre.
*   Evidencia mínima, prohibiciones y criterio operativo.

## Pasos Obligatorios
1.  Leer el contrato y verificar precondiciones.
2.  Traducir a una skill mínima acotada a una sola función.
3.  Escribir formato de respuesta cerrado y añadir ejemplos y criterio operativo.
4.  Emitir propuesta para revisión.

## Criterios de Calidad
*   Una sola función principal con límites explícitos.
*   No invade scripts, gates, reglas ni workflows.
*   No mezcla redacción con validación determinista ni crea contradicciones.

## Formato de Respuesta
```text
NOMBRE_SKILL:
RUTA_PROPUESTA:
CONTRATO_RECIBIDO:
PRECONDICIONES_CUMPLIDAS: SI/NO
SKILL_MD_PROPUESTO:
RIESGOS_DE_DISEÑO:
EVIDENCIA_REQUERIDA:
DECISION_HUMANA_REQUERIDA: SI/NO
DICTAMEN:
```

## Valores Permitidos para DICTAMEN
`CREAR_SKILL_MD` | `NO_CREAR_SKILL_CONTRATO_INCOMPLETO` | `REQUIERE_AJUSTE_CONTRATO` | `REQUIERE_DECISION_HUMANA`

## Ejemplos de Referencia
Consulte el archivo de referencias [ejemplos.md](references/ejemplos.md) para revisar contratos aprobados e incompletos.

## Criterio Operativo del Proyecto
Una skill se planifica, se conecta con la necesidad del proyecto, define pasos constantes para la IA y se audita mediante checklist.

## Criterio de Cierre
El SKILL.md propuesto cumple el contrato y puede revisarse sin ambigüedad.

## Evidencia Mínima
Contrato aprobado, dictámenes previos, SKILL.md propuesto y riesgos evaluados.

## Prohibiciones
*   No decidir de forma autónoma que una skill hace falta.
*   No crear scripts, gates, workflows ni subagentes.
*   No abrir ni autorizar gates de fases directamente, ni convertir validaciones deterministas en skills.
