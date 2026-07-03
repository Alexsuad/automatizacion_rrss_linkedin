---
name: verificar-no-mezcla-de-capas
description: "Usar para detectar si una tarea mezcla capas incompatibles como gobernanza, redacción, negocio, marketing, legal, scripts, gates, compilación o entrega final, y recomendar separación si corresponde."
---

# verificar-no-mezcla-de-capas

## Propósito
Detectar si una tarea mezcla capas que deben permanecer separadas.

## Cuándo usarla
Usarla al revisar tareas, reportes, skills o paquetes que puedan cruzar gobernanza, redacción, negocio, marketing, legal, scripts, gates, compilación o entrega final.

## Cuándo NO usarla
No usarla para redactar contenido final de negocio ni para ejecutar cambios fuera de revisión.

## Entradas
- Instrucción recibida.
- Alcance permitido.
- Archivos tocados.
- Acciones realizadas.
- Capas implicadas.

## Salidas
- Lista de capas separadas.
- `DICTAMEN_CAPAS`.
- `SIN_MEZCLA`
- `MEZCLA_CONTROLADA`
- `MEZCLA_CRITICA`
- `SEPARAR_TAREA`
- Lista de mezclas detectadas.
- Riesgo de contaminación o confusión.
- Recomendación de corrección o bloqueo.

## Pasos obligatorios
1. Identificar las capas implicadas.
2. Separar lo que pertenece a cada capa.
3. Detectar cruces indebidos.
4. Marcar si hay mezcla crítica.
5. Emitir recomendación clara.

## Criterio de cierre
La skill queda cerrada cuando se confirma que las capas relevantes están separadas o se indica con claridad la mezcla detectada.

## Evidencia mínima
- Capas identificadas.
- Mezclas detectadas o descartadas.
- Recomendación final.

## Prohibiciones
- No redacta contenido final de entregables o documentos de negocio.
- No abre ni autoriza puertas de control (gates) de fases.
- No modifica directamente archivos o carpetas de entrega final.
- No toma decisiones estratégicas de negocio, marketing o legal.
- No convierte hipótesis en hechos.
