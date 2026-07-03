# Ejemplos de creación de skill desde contrato

### Ejemplo 1 (Contrato completo y aprobable)
```text
NOMBRE_SKILL: clasificar-pregunta-proyecto
RUTA_PROPUESTA: .agents/skills/clasificar-pregunta-proyecto/SKILL.md
CONTRATO_RECIBIDO: completo
PRECONDICIONES_CUMPLIDAS: SI
SKILL_MD_PROPUESTO: propuesto
RIESGOS_DE_DISEÑO: bajos
EVIDENCIA_REQUERIDA: contrato y dictámenes previos
DECISION_HUMANA_REQUERIDA: NO
DICTAMEN: CREAR_SKILL_MD
```

### Ejemplo 2 (Contrato incompleto)
```text
NOMBRE_SKILL: skill sin límites claros
RUTA_PROPUESTA: .agents/skills/skill-sin-limites/SKILL.md
CONTRATO_RECIBIDO: incompleto
PRECONDICIONES_CUMPLIDAS: NO
SKILL_MD_PROPUESTO: no procede
RIESGOS_DE_DISEÑO: alto solape y ambigüedad
EVIDENCIA_REQUERIDA: contrato completo
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: NO_CREAR_SKILL_CONTRATO_INCOMPLETO
```

### Ejemplo 3 (Contrato que requiere ajuste)
```text
NOMBRE_SKILL: skill ambigua
RUTA_PROPUESTA: .agents/skills/skill-ambigua/SKILL.md
CONTRATO_RECIBIDO: parcial
PRECONDICIONES_CUMPLIDAS: NO
SKILL_MD_PROPUESTO: borrador
RIESGOS_DE_DISEÑO: duplicidad y exceso de alcance
EVIDENCIA_REQUERIDA: límites y criterios de cierre
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: REQUIERE_AJUSTE_CONTRATO
```
