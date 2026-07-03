# Ejemplos de decisión de tipo de pieza del sistema agéntico

### Ejemplo 1
Necesidad: validar que un archivo tenga frontmatter, nombre correcto y secciones obligatorias.
Resultado:
```text
TIPO_RECOMENDADO: SCRIPT
PIEZA_PROPUESTA: script de validación estructural
RAZON: La comprobación es determinista y repetible.
ALTERNATIVAS_DESCARTADAS: SKILL, GATE, WORKFLOW
RIESGO_SI_SE_CREA_MAL: Se delega una verificación exacta a criterio subjetivo.
EVIDENCIA_REQUERIDA: reglas de formato y rutas esperadas.
DECISION_HUMANA_REQUERIDA: NO
DICTAMEN: CREAR_SCRIPT
```

### Ejemplo 2
Necesidad: clasificar si una duda debe resolverse con documentación interna, consulta a responsable, investigación externa o decisión humana.
Resultado:
```text
TIPO_RECOMENDADO: SKILL
PIEZA_PROPUESTA: skill de clasificación de fuentes y decisiones
RAZON: Hace falta criterio semántico y decisión guiada.
ALTERNATIVAS_DESCARTADAS: SCRIPT, GATE, REGLA
RIESGO_SI_SE_CREA_MAL: La clasificación se vuelve rígida o incompleta.
EVIDENCIA_REQUERIDA: ejemplos de dudas, fuentes disponibles y responsables de decisión.
DECISION_HUMANA_REQUERIDA: NO
DICTAMEN: CREAR_SKILL
```

### Ejemplo 3
Necesidad: aprobar la apertura de una fase posterior.
Resultado:
```text
TIPO_RECOMENDADO: GATE
PIEZA_PROPUESTA: gate documental
RAZON: La necesidad es de aprobación o bloqueo, no de ejecución.
ALTERNATIVAS_DESCARTADAS: SKILL, SCRIPT
RIESGO_SI_SE_CREA_MAL: Se confunde control de avance con herramienta operativa.
EVIDENCIA_REQUERIDA: criterios de aprobación y bloqueos vigentes.
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: CREAR_GATE
```

### Ejemplo 4
Necesidad: bloquear Fase 3 si no hay evidencia.
Resultado:
```text
TIPO_RECOMENDADO: GATE + SCRIPT
PIEZA_PROPUESTA: gate de bloqueo con auditoría determinista previa
RAZON: La decisión de bloqueo es de gobernanza y la verificación de evidencia es exacta.
ALTERNATIVAS_DESCARTADAS: SKILL, REGLA
RIESGO_SI_SE_CREA_MAL: Se mezcla control de fase con análisis subjetivo y se deja pasar una entrega insuficiente.
EVIDENCIA_REQUERIDA: criterio de bloqueo, evidencia mínima y archivos válidos.
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: CREAR_GATE_Y_SCRIPT
```

### Ejemplo 5
Necesidad: revisar coherencia entre varios bloques dependientes de un proyecto.
Resultado:
```text
TIPO_RECOMENDADO: SKILL + GATE
PIEZA_PROPUESTA: skill de coherencia transversal más gate de validación de fase
RAZON: La revisión necesita criterio experto y la decisión de avance requiere control de fase.
ALTERNATIVAS_DESCARTADAS: SCRIPT, REGLA
RIESGO_SI_SE_CREA_MAL: Se valida una incoherencia como si fuera suficiente con formato.
EVIDENCIA_REQUERIDA: bloques relacionados, dependencias entre artefactos y criterio de aprobación.
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: CREAR_SKILL_Y_GATE
```

### Ejemplo 6
Necesidad: consultar una fuente externa o repositorio de conocimiento para resolver un hueco concreto.
Resultado:
```text
TIPO_RECOMENDADO: SKILL
PIEZA_PROPUESTA: skill de preparación de consulta controlada
RAZON: La necesidad principal es criterio experto sobre qué buscar y cómo usarlo.
ALTERNATIVAS_DESCARTADAS: SCRIPT, GATE, WORKFLOW
RIESGO_SI_SE_CREA_MAL: Se crea una integración innecesaria o se sobredimensiona el sistema.
EVIDENCIA_REQUERIDA: hueco concreto, fuente probable, canal de consulta y límite de uso.
DECISION_HUMANA_REQUERIDA: NO
DICTAMEN: CREAR_SKILL
```

### Ejemplo 7
Necesidad: regla "no tocar salidas finales protegidas antes del gate correspondiente".
Resultado:
```text
TIPO_RECOMENDADO: REGLA / GATE
PIEZA_PROPUESTA: regla transversal o gate de autorización
RAZON: La restricción aplica a todo el sistema y también puede apoyarse en la aprobación de gate.
ALTERNATIVAS_DESCARTADAS: SKILL, SCRIPT
RIESGO_SI_SE_CREA_MAL: Se convierte una restricción global en una instrucción local fácil de saltar.
EVIDENCIA_REQUERIDA: ámbito de aplicación y referencia al gate, fase o autorización vigente.
DECISION_HUMANA_REQUERIDA: SI
DICTAMEN: CREAR_REGLA_Y_GATE
```

### Ejemplo 8
Necesidad: crear un subagente para cada skill.
Resultado:
```text
TIPO_RECOMENDADO: NO_CREAR
PIEZA_PROPUESTA: ninguna
RAZON: Crear un subagente por skill sobredimensiona el sistema y duplica responsabilidades.
ALTERNATIVAS_DESCARTADAS: SUBAGENTE, WORKFLOW
RIESGO_SI_SE_CREA_MAL: El sistema se vuelve más complejo, más caro de mantener y menos trazable.
EVIDENCIA_REQUERIDA: ninguna; la decisión correcta es no crear.
DECISION_HUMANA_REQUERIDA: NO
DICTAMEN: NO_CREAR
```
