# Mapa técnico de contexto y pipeline offline

## 1. Propósito

Este documento tiene como propósito consolidar y detallar el mapa técnico de la arquitectura de contexto, anticontaminación de datos y ejecución del pipeline offline (Fases J a Q). Su objetivo principal es servir de referencia para los agentes y desarrolladores que operen sobre el sistema, aclarando los límites de diseño, las restricciones de seguridad locales y qué funcionalidades quedan fuera del alcance en la versión actual.

---

## 2. Estado técnico actual

El sistema cuenta con un motor offline implementado de manera determinista y local. Se han completado y validado las fases desde la J hasta la Q, garantizando la inmutabilidad de los datos, el desacoplamiento de servicios externos de inteligencia artificial (IA) o red, y la trazabilidad de cada paso del flujo.

---

## 3. Piezas implementadas

### ContextoTrabajo (Fase J)
- **Propósito**: Representar el contexto activo declarado para una tarea o cliente.
- **Campos**: Contiene el identificador determinista del contexto (`contexto_id`), el cliente lógico (`cliente_id`), la superficie (`superficie`), la campaña opcional (`campaña`), la lista de fuentes autorizadas (`fuentes_autorizadas`), el flag de permiso de datos reales (`datos_reales_permitidos`), el estado actual (`estado`) y las notas de seguridad relevantes (`notas_seguridad`).
- **Restricciones**: No realiza cargas de datos reales en disco ni de fuentes externas. Se rige por identificadores neutros y sintéticos.

### Validación de compatibilidad de contexto (Fase K)
- **Propósito**: Validar si los elementos involucrados en una ejecución son compatibles con el contexto activo de trabajo.
- **Acción**: Valida que coincidan el cliente, la superficie de destino y que las fuentes utilizadas estén declaradas en las fuentes autorizadas del contexto. Bloquea el procesamiento si se intentan utilizar datos reales sin autorización en el contexto (`datos_reales_permitidos=False`), evitando fugas o contaminación.

### Validación de cambio/reset de contexto (Fase L)
- **Propósito**: Detectar cuándo ocurre una transición de contexto de trabajo para evitar contaminación.
- **Acción**: Exige confirmación explícita si cambian campos críticos como el cliente, la superficie o los permisos de datos reales. No borra archivos físicos ni bases reales automáticamente; en su lugar, advierte y recomienda limpiezas manuales.

### EvidenciaContextoUsado (Fase N)
- **Propósito**: Registrar el rastro de la ejecución y certificar qué contexto de trabajo se declaró en la operación.
- **Campos**: Copia de forma inmutable los campos de `ContextoTrabajo` y registra el resultado de la operación (`PASS`, `WARN`, `BLOQUEADO`, `FAIL`), los artefactos generados, advertencias y bloqueos técnicos. Genera un hash `id_evidencia` determinista basado en los campos y no persiste archivos en disco en esta fase.

### Pipeline offline con contexto (Fase P)
- **Propósito**: Orquestar el flujo determinista local.
- **Acción**: Antes de iniciar, valida la compatibilidad del contexto. Si es incompatible, bloquea la ejecución. Si es compatible, coordina de forma secuencial la extracción de idea central, clasificación de la intención editorial, diagnóstico de base y generación de la evidencia de contexto.

### Exports públicos de contexto, evidencia y pipeline (Fases M, O, Q)
- **Propósito**: Disponer los imports públicos estables para la interacción pública con estas funcionalidades sin acoplar el núcleo interno.

---

## 4. Flujo offline con contexto

El flujo operacional offline V0 sigue la siguiente secuencia secuencial:
1. **Inicialización**: Se activa un contexto de trabajo con `activar_contexto_trabajo`.
2. **Validación de Cambio**: Si existe un contexto previo, se evalúa con `validar_cambio_contexto`.
3. **Petición del Pipeline**: Se invoca a `ejecutar_pipeline_contexto_offline` proporcionando el contexto, texto base y datos declarados de operación.
4. **Guardián de Compatibilidad**: El pipeline invoca internamente a `validar_compatibilidad_contexto`.
   - Si no es compatible: Se interrumpe el flujo y se retorna un resultado BLOQUEADO, sin ejecutar extracción de idea, intención ni diagnóstico.
   - Si es compatible: Se procede con el procesamiento determinista.
5. **Generación de Evidencia**: Se genera una instancia inmutable de `EvidenciaContextoUsado` que registra los parámetros y el resultado de la operación.

---

## 5. Reglas de anticontaminación V0

- **Aislamiento lógico estricto**: Cada operación debe asociarse a un único contexto. Queda prohibido mezclar datos, fuentes o campañas pertenecientes a diferentes contextos o clientes.
- **Datos Sintéticos por defecto**: Si `datos_reales_permitidos` es `False`, el sistema bloqueará cualquier intento de procesar información clasificada como real.
- **Límites de inferencia claros**: Se inyectan advertencias específicas en las notas de seguridad y en los límites de inferencia para recordar que los datos reales de producción o de negocio no deben ingresarse en los flujos V0.

---

## 6. Qué NO existe todavía

- **Persistencia física**: No se guardan registros ni evidencias en el sistema de archivos local ni en bases de datos externas de forma automatizada en esta fase de contexto.
- **Generación de borradores y publicación real**: El pipeline actual llega hasta el diagnóstico y la auditoría del contexto de trabajo; no genera posts finales ni se conecta a Metricool u otros adaptadores de salida para publicar.
- **Limpieza automática de bases**: Las advertencias de cambio de contexto solo notifican y guían al operador humano; no eliminan datos de forma física o automática.

---

## 7. Qué está prohibido antes de fases futuras

- **Uso de Datos Reales de Producción**: Está prohibido introducir PII (información de identificación personal), secretos, API Keys, tokens de acceso o datos reales de clientes en tests unitarios, prompts, código fuente o evidencias versionadas.
- **Conexiones a servicios Cloud/SaaS**: Queda prohibido integrar conectores reales con Google Drive, Notion, o APIs en vivo de LLM o Whisper.
- **Uso de Red**: Toda la lógica debe ejecutarse en local, sin dependencias a internet.

---

## 8. Relación con fases cerradas

Este sistema de contexto y pipeline offline (Fases J–Q) interactúa directamente con los contratos y lógica construida en las fases iniciales:
- **IdeaCentral (Fase D)**
- **IntencionEditorialClasificada (Fase E)**
- **Diagnóstico Base Editorial (Fase F)**

Todas estas se orquestan y aseguran bajo el paraguas de validación de compatibilidad proporcionada por `ContextoTrabajo`.

---

## 9. Criterio para avanzar a datos reales o fuentes externas

Para realizar la transición del estado offline/sintético a operaciones en vivo o almacenamiento real, se requiere:
1. Un contrato aprobado de persistencia local de evidencias en formato seguro.
2. Aprobación y auditoría explícita de seguridad sobre la gestión de PII y saneamiento de entradas.
3. Un entorno de trabajo (`ContextoTrabajo`) configurado explícitamente con `datos_reales_permitidos=True` y notas de seguridad debidamente auditadas.
