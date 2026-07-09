# 00 — Brief de arquitectura pre-código

## 1. Qué problema resuelve

La creación de contenido profesional suele romperse por cuatro fricciones:

* la materia prima entra por canales distintos y no existe una normalización útil;
* el contenido pierde voz y coherencia al pasar por herramientas genéricas;
* cada canal se trabaja como un proceso manual aislado;
* no existe un bucle claro entre entrada, adaptación, revisión, salida y aprendizaje posterior.

El sistema que se quiere construir no es solo un publicador de LinkedIn ni solo una automatización por voz.

Es un sistema portable y agnóstico que permita transformar fuentes de contenido en piezas utilizables, revisables y escalables sin depender de un entorno específico de agentes.

## 2. Para quién sirve

El sistema está pensado para:

* profesionales B2B;
* consultores;
* fundadores;
* creadores expertos;
* equipos pequeños que producen contenido desde distintas fuentes y necesitan velocidad sin perder control editorial.

## 3. Producto esperado

El producto esperado es un **sistema portable de transformación y publicación de contenido**.

Su trabajo es:

```text
fuente de contenido
-> normalización
-> extracción de intención e idea
-> adaptación editorial por canal
-> revisión
-> aprobación humana
-> borrador o preparación de publicación
-> evidencia útil
-> retroalimentación
```

### 3.1 Identidad del sistema

La identidad del sistema no viene dada por:

* un único canal;
* un único tipo de entrada;
* un único proveedor;
* un único framework agéntico.

La identidad del sistema viene dada por su capacidad de:

* aceptar distintas fuentes;
* preservar voz y reglas;
* adaptar salida por canal;
* mantener control humano;
* preparar una operación reutilizable y escalable.

### 3.2 Primer corte operativo

El primer corte útil del sistema será:

* entrada manual en texto;
* generación de post para LinkedIn;
* validación editorial y de seguridad;
* aprobación humana usable;
* salida local en formato borrador listo.

Audio, transcripción, publicación real, visuales y otros canales llegarán después, sobre un flujo ya útil.

## 4. Principios base

* **Portabilidad:** el sistema debe poder operar con software normal, archivos, scripts, adaptadores y servicios propios, sin depender de un único entorno de agentes.
* **Agnosticismo de entrada:** texto, audio, transcripciones, documentos u otras fuentes son variantes de entrada, no productos distintos.
* **Agnosticismo de canal:** LinkedIn puede ser el primer canal operativo, pero la arquitectura no debe impedir otros canales posteriores.
* **Aprobación humana obligatoria:** no se debe publicar ni programar nada real sin confirmación humana explícita.
* **Local-first para validar:** el primer flujo debe probarse con salida local segura antes de cualquier integración real externa.
* **Separación entre visión y fotografía técnica:** la visión del producto y el estado actual del código no son lo mismo.

## 5. Módulos conceptuales del sistema

El sistema debería organizarse alrededor de estos módulos:

1. **Ingesta de fuentes:** recibe texto, audio u otras materias primas.
2. **Normalización:** convierte cada fuente en una base operable común.
3. **Perfil editorial:** define voz, restricciones, tono y preferencias.
4. **Transformación editorial:** genera piezas candidatas por canal.
5. **Revisión y validación:** comprueba calidad, seguridad, trazabilidad y publicabilidad.
6. **Aprobación humana:** actúa como gate de operación real.
7. **Salida y adaptadores:** generan borrador local, payload de publicación o publicación controlada.
8. **Aprendizaje y feedback:** permiten incorporar patrones útiles posteriores sin contaminar el núcleo.

## 6. Qué no debe confundirse con el producto

No son el producto:

* el framework agéntico usado para prototipar;
* los documentos de control;
* los gates por sí mismos;
* el pipeline offline actual como fin en sí mismo;
* el canal LinkedIn tratado como única identidad permanente.

## 7. Criterio para pasar a implementación

No se debe seguir escribiendo código guiado por documentación vieja o contradictoria.

Antes de avanzar, deben quedar claros:

* la visión vigente del producto;
* el alcance del MVP útil;
* el orden de implementación por valor;
* las restricciones de seguridad que sí siguen activas;
* qué parte del repositorio actual se reutiliza y cuál queda como estado técnico anterior.
