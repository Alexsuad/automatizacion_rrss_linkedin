# ADR-000: Decisiones Técnicas Base

## 1. Estado del ADR

Estado: vigente con visión corregida

Este ADR registra las decisiones técnicas base del sistema en su nueva etapa:

* producto portable y agnóstico;
* primer flujo útil validado desde texto manual;
* LinkedIn como primer canal operativo;
* salida local segura antes de integraciones reales.

Este documento ya no debe leerse como ADR de un “publicador automático desde audio para LinkedIn”, sino como base técnica del sistema corregido de rumbo.

## 2. Contexto

El repositorio actual ya contiene una base útil en:

* contratos;
* validadores;
* `LocalDraftPublisher`;
* trazabilidad;
* flujo offline determinista;
* tests.

Pero el producto deseado es más amplio que ese estado actual.

La arquitectura debe permitir:

* múltiples fuentes de entrada;
* transformación editorial reutilizable;
* salidas desacopladas;
* crecimiento por canales;
* aprobación humana obligatoria;
* expansión progresiva sin rehacer el núcleo.

## 3. Matriz de decisiones técnicas

| Decisión | Estado | Motivo | Alternativas | Riesgo | Cuándo reevaluar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Python como base** | Aceptado | El repositorio actual ya está construido sobre Python y encaja bien con validación, scripts, IA y adaptadores. | Node.js, Go. | Mayor consumo que lenguajes compilados. | Si la portabilidad multiplataforma o el rendimiento se vuelven críticos. |
| **2. Pydantic para contratos** | Aceptado | Permite contratos explícitos y validación fuerte entre entradas, salidas y diagnósticos. | Diccionarios sin esquema. | Rigidez si el contrato cambia rápido. | Si el costo de evolución supera el beneficio de seguridad. |
| **3. Puertos y adaptadores** | Aceptado | Protege el núcleo frente a canales, entradas, proveedores y publicadores concretos. | Acoplamiento directo a SDKs o servicios. | Más abstracción inicial. | Si el sistema deja de necesitar portabilidad, algo hoy no deseado. |
| **4. Local-first para la primera validación** | Aceptado | El primer éxito real debe ocurrir sin publicar en vivo ni depender de red. | Empezar por integración externa real. | Puede retrasar feedback de adaptadores reales si se prolonga demasiado. | Cuando el flujo útil local ya esté consolidado. |
| **5. LinkedIn como primer canal operativo** | Aceptado | Permite validar valor en un canal concreto sin cerrar la arquitectura a otros canales. | Omnicanal desde el inicio. | Confundir “primer canal” con “identidad permanente”. | Cuando el flujo textual útil y la salida local ya estén estabilizados. |
| **6. Texto manual como primera entrada operativa** | Aceptado | Es la forma más rápida de validar el flujo útil antes de ampliar fuentes. | Empezar por audio, video o ingesta compleja. | Que el equipo olvide luego ampliar entradas. | Cuando el flujo textual útil esté probado en operación real. |
| **7. Audio como entrada prioritaria de expansión** | Candidata prioritaria | Sigue siendo una fuente valiosa para el producto, pero no debe bloquear el primer éxito. | Postergar toda entrada distinta a texto. | Añadir complejidad demasiado pronto. | Al entrar en la fase de ampliación de entradas. |
| **8. `LocalDraftPublisher` como primera salida implementada** | Aceptado | Ya existe, es segura y útil para validar persistencia local y publicabilidad. | Empezar por publicador real. | Convertirlo en dogma y no en implementación inicial. | Cuando entren payloads o adaptadores externos reales. |
| **9. Evidencia local en JSON/Markdown** | Aceptado | Facilita inspección, trazabilidad y debugging sin base de datos obligatoria. | Persistencia temprana en DB. | Fragmentación manual si crece demasiado. | Si aparecen necesidades reales de multiusuario, búsqueda o panel. |
| **10. Sanitización de PII y secretos como obligación transversal** | Aceptado | La seguridad no depende del canal ni del tipo de entrada. | Sanitización opcional o tardía. | Filtros demasiado agresivos. | Si se detecta pérdida significativa de contexto útil. |
| **11. `dry_run` antes de publicación real** | Aceptado | Permite preparar salidas y adaptadores sin ejecutar acciones reales. | Ir directo a publicación en vivo. | Falsa sensación de preparación si nunca se conecta el adaptador real. | Cuando el flujo local útil y la aprobación humana ya estén maduros. |
| **12. Adaptador de publicación desacoplado** | Aceptado | El sistema no debe depender de un único publicador externo. | Integración directa en dominio. | Más trabajo de modelado de salida. | Cuando exista el primer payload real de publicación. |
| **13. LiteLLM como opción de proveedor IA** | Candidata evaluable | Puede ayudar a mantener portabilidad entre proveedores de generación. | SDK directo de un único proveedor. | Otra capa de abstracción. | Cuando se conecte el primer proveedor real de IA. |
| **14. Faster-Whisper u otro transcriptor local** | Candidata evaluable | Puede resolver la expansión a audio con privacidad y coste controlado. | Whisper API remota, otro motor local. | Requisitos de hardware y mantenimiento. | Cuando la fase de audio entre en ejecución real. |
| **15. Framework agéntico como implementación opcional, no identidad** | Aceptado | El producto debe sobrevivir a Claude, ADK u otro entorno. | Acoplar la arquitectura al framework del prototipo. | Duplicar lógica entre software y agentes si no se diseña bien. | Si aparece un runtime estable que realmente simplifique operación sin acoplar producto. |

## 4. Reglas de arquitectura

1. **El núcleo no depende de un proveedor ni de un entorno agéntico.**
2. **La entrada se modela por contrato común, no por fuente única.**
3. **La salida se modela por contrato portable, no por una sola implementación concreta.**
4. **La aprobación humana sigue siendo un gate obligatorio para cualquier salida real.**
5. **Toda integración externa debe entrar por adaptador desacoplado.**
6. **Las reglas de seguridad y privacidad son invariantes del sistema.**

## 5. Fronteras mínimas del dominio

Para sostener portabilidad real, el sistema debería interactuar mediante fronteras como estas:

* **Puerto de modelo/generación**
* **Puerto de transcripción**
* **Puerto de publicación/preparación de salida**
* **Puerto de persistencia/evidencia**
* **Puerto de aprobación humana**
* **Puerto de revisión/validación automática**

No implica que todos estén implementados hoy.
Implica que la arquitectura debe dejar espacio para ellos.

## 6. Qué no decide este ADR

Este ADR no fija todavía:

* el proveedor real de IA;
* el motor real de transcripción;
* el primer adaptador real de publicación en producción;
* la UI final;
* el segundo canal operativo;
* el modelo de multiusuario.

Esas decisiones pertenecen a ADRs posteriores o a fases donde ya exista necesidad real.

## 7. Consecuencia práctica

Después de este ADR, el orden correcto de evolución sigue siendo:

```text
contrato de entrada
-> contrato de salida
-> decisiones técnicas alineadas
-> cambios de código
```

Y la prioridad de producto sigue siendo:

```text
texto útil
-> aprobación usable
-> salida local lista
-> ampliación de entradas
-> preparación/publicación
```
