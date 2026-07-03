---
name: auditar-trazabilidad-input-output
description: "Usar para comparar instrucción original, alcance permitido, archivos tocados, acciones ejecutadas y resultado reportado, detectando cambios de alcance, requisitos perdidos o conclusiones no soportadas."
---

# auditar-trazabilidad-input-output

## Propósito
Comparar una instrucción recibida con lo que realmente se ejecutó y se reportó.

## Cuándo usarla
Usarla para revisar trazabilidad entre solicitud, alcance permitido, archivos tocados, acciones realizadas y resultado reportado.

## Cuándo NO usarla
No usarla para tomar decisiones de negocio ni para abrir puertas de control (gates) de forma autónoma.

## Entradas
- Instrucción recibida.
- Alcance permitido.
- Archivos tocados.
- Acciones realizadas.
- Resultado reportado.

## Salidas
- Coincidencias entre instrucción y ejecución.
- `DICTAMEN_TRAZABILIDAD`.
- `TRAZABILIDAD_OK`
- `DESVIO_MENOR`
- `DESVIO_CRITICO`
- `ALCANCE_CAMBIADO`
- Cambios de alcance detectados.
- Requisitos perdidos.
- Conclusiones no soportadas.
- Veredicto de trazabilidad.

## Pasos obligatorios
1. Leer la instrucción original.
2. Leer el alcance permitido.
3. Comparar archivos tocados con los autorizados.
4. Comparar acciones realizadas con las pedidas.
5. Detectar omisiones y desvíos.
6. Comparar el reporte con la evidencia real.
7. Emitir veredicto.

## Criterio de cierre
La skill queda cerrada cuando la trazabilidad entre entrada, ejecución y salida queda clara y verificable.

## Evidencia mínima
- Instrucción original.
- Alcance permitido.
- Archivos tocados.
- Acciones realizadas.
- Resultado reportado.
- Veredicto de trazabilidad.

## Prohibiciones
- No redacta contenido final de entregables o documentos de negocio.
- No abre ni autoriza puertas de control (gates) de fases.
- No modifica directamente archivos o carpetas de entrega final.
- No toma decisiones estratégicas de negocio, marketing o legal.
- No convierte hipótesis en hechos.
