# Instrucción Operativa para Agentes IA

## 1. Identidad y estado del proyecto

* **Identidad actual:** Portable Content Publisher: sistema portable y agnóstico de transformación de contenido, orientado a convertir distintas fuentes de entrada en piezas publicables, revisables y reutilizables.
* **Estado actual:** El repositorio contiene una base offline y determinista ya construida, especialmente fuerte en contratos, validadores, `LocalDraftPublisher`, trazabilidad y control local. El producto final deseado todavía está en transición.
* **Prioridad actual:** Recuperar el rumbo de producto sin perder seguridad, reutilizando lo útil del repositorio actual y evitando nuevas capas de sobregobernanza.

> [!IMPORTANT]
> **Directiva de transición:** La visión y el alcance vigentes se definen en `docs/00_brief_arquitectura_pre_codigo.md`, `docs/01_alcance_si_no.md`, `docs/05_fases_implementacion.md` y `docs/09_plan_implementacion_post_planeacion.md`.
> 
> Si un documento técnico o histórico contradice esos archivos, prevalece la documentación núcleo vigente.

## 2. Orden de lectura y fuente de verdad

Orden recomendado de lectura:
1. `docs/00_brief_arquitectura_pre_codigo.md`
2. `docs/01_alcance_si_no.md`
3. `docs/05_fases_implementacion.md`
4. `docs/09_plan_implementacion_post_planeacion.md`
5. `docs/02_contrato_entrada_contenido.md`
6. `docs/03_contrato_perfil_narrativo.md`
7. `docs/04_contrato_salida.md`
8. `docs/06_contrato_calidad_post_linkedin.md`
9. `docs/architecture/ADR-000_Decisiones_Tecnicas_Base.md`
10. `docs/10_mapa_tecnico_contexto_pipeline_offline.md`

Documentos derivados o no rectores:
* `docs/07_gates_futuros_v1.md`
* `docs/08_skills_producto_linkedin_futuras.md`
* `docs/Control/`

`docs/Control/` se trata como archivo histórico y de transición; no es fuente normativa activa para nuevas decisiones salvo auditoría explícita.

## 3. Principios operativos

* **Producto antes que ritual:** El objetivo no es cerrar fases por sí mismas, sino acercar el sistema a un flujo útil real.
* **Portabilidad real:** El sistema no debe depender de un agente, proveedor, canal o tipo único de entrada para ser valioso.
* **LinkedIn como arranque probable, no obligatorio ni único:** LinkedIn puede ser el primer canal operativo por practicidad, pero si otra red social resulta mejor para iniciar el desarrollo, puede priorizarse sin contradecir la identidad del producto.
* **Texto primero, otras fuentes después:** El primer flujo útil debe poder arrancar desde texto manual. Audio, video u otras fuentes entran por adaptación progresiva.
* **Reutilizar antes de rehacer:** Contratos, validadores, adaptadores mock y `LocalDraftPublisher` deben aprovecharse cuando ayuden al nuevo rumbo.
* **Gobernanza proporcional:** Solo se documenta, valida o gatea lo necesario para evitar errores, fugas de datos, malas publicaciones o acoplamientos dañinos.

## 4. Reglas de seguridad que siguen vigentes

Estas reglas siguen activas aunque el producto esté en transición:

* No introducir PII, secretos, credenciales ni datos reales de cliente en tests, fixtures, docs generales, prompts versionados ni evidencias versionadas.
* No exponer rutas locales absolutas, logs crudos ni estructura interna al usuario final.
* No acoplar el núcleo del sistema a un proveedor externo concreto.
* No ejecutar publicación real, programación real ni integraciones con datos reales sin aprobación explícita.
* No crear nuevas dependencias externas o nuevas automatizaciones de alto riesgo sin justificar el valor de producto y el impacto.

## 5. Qué evitar en esta etapa

* Expandir `ContextoTrabajo` o el pipeline offline si no desbloquea producto real.
* Crear nuevas skills de gobernanza o más capas documentales sin necesidad concreta.
* Tratar cualquier documento histórico como si siguiera definiendo el rumbo.
* Introducir omnicanal, visuales, analítica avanzada o multiusuario antes de consolidar el primer flujo útil.

## 6. Diferencia entre lógica flexible y lógica determinista

* **Flexible:** redacción, adaptación editorial, revisión de tono, selección de formato, generación de variantes.
* **Determinista:** validación de estructura, PII, aprobación, rutas, persistencia local, trazabilidad, manifests y estados.

## 7. Cierre y trazabilidad de tareas

Cada reporte del agente debe declarar:
1. Archivos leídos, creados o modificados.
2. Comandos ejecutados y validaciones hechas.
3. Estado Git y búsqueda de rutas locales absolutas.
4. Riesgos pendientes.
5. Veredicto:
   * `PASS`: cumple alcance y restricciones.
   * `WARN`: cumple con riesgos menores o deuda pendiente.
   * `FAIL`: incumple criterios de aceptación.
   * `BLOQUEADO`: requiere tocar archivos prohibidos, usar datos no autorizados o resolver una contradicción de rumbo no aclarada.

## 8. Control Git

* Ejecutar `git status --short` si existe repositorio Git.
* Prohibido hacer commit o push sin aprobación explícita.
