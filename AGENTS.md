# Instrucción Operativa para Agentes IA (V1)

## 1. Identidad y Estado del Proyecto
* **Identidad:** Sistema V1 para convertir audio en posts de LinkedIn con revisión de calidad, aprobación humana (gate), adaptadores de publicación y evidencia local.
* **Estado actual:** Implementación local inicial offline (Fases 0–5 cerradas). Prohibido avanzar a LLM, ADK runtime, Metricool, Whisper, Google Drive o nuevas features sin auditoría y aprobación explícita.

* **Alcance del documento:** `AGENTS.md` no reemplaza contratos, ADR, skills, gates ni workflows; solo fija el marco operativo global.
* **Política antes que código:** Primero contrato → luego gate → luego script → luego código.

## 2. Fuente de Verdad y Orden de Lectura
Orden recomendado de lectura:
1. `docs/00_brief_arquitectura_pre_codigo.md` (Visión)
2. `docs/01_alcance_si_no.md` (Alcance)
3. `docs/02_contrato_entrada_contenido.md` (Entrada)
4. `docs/03_contrato_perfil_narrativo.md` (Perfil narrativo)
5. `docs/04_contrato_salida.md` (Salida)
6. `docs/06_contrato_calidad_post_linkedin.md` (Calidad LinkedIn)
7. `docs/05_fases_implementacion.md` (Fases)
8. `docs/architecture/ADR-000_Decisiones_Tecnicas_Base.md` (Decisiones técnicas)

*   **Documentación de Planeación Adicional:** `docs/07_gates_futuros_v1.md` y `docs/08_skills_producto_linkedin_futuras.md` son lecturas complementarias de planeación bajo demanda.
*   **Skills de Gobernanza vs. Producto:** Existen skills físicas de gobernanza en `.agents/skills/` para auditar y controlar el trabajo actual del agente. Las skills de producto de LinkedIn son de fase futura y **no** deben crearse todavía.

## 3. Glosario Operativo
* **Agente:** Rol con criterio propio.
* **Skill:** Tarea repetible y acotada.
* **Regla:** Restricción transversal.
* **Gate:** Punto de aprobación o bloqueo.

## 4. IA Flexible vs. Python Determinista
* **Lógica IA (Flexible):** Redactar post, adaptar tono, diagnosticar y sugerir CTA.
* **Lógica Python (Determinista):** Validar estructura, campos, aprobación, evidencia, PII, rutas y estados.

## 5. Trazabilidad Obligatoria
Flujo lógico: `audio → transcripción → intención editorial inicial → idea central estructurada → post → diagnóstico → aprobación → publicación/adaptador → evidencia`.

## 6. Reglas y Límites V1
* **Canal exclusivo:** LinkedIn. Quedan excluidos: Instagram, X/Twitter, carruseles, imágenes, video, dashboards, analítica, multiusuario y MCP complejos.
* **Primera meta futura:** Pipeline local end-to-end con `LocalDraftPublisher` y evidencia local. No usar Metricool real como primera prueba.
* **Desacoplamiento:** No acoplar el núcleo a ningún proveedor (Gemini, OpenAI, LiteLLM, Metricool, Faster-Whisper, ADK).
* **Contexto de cliente:** Los datos del cliente deben residir fuera del core en archivos intercambiables (ej. `contexto_cliente.md`). Google Drive o Notion son sedes futuras posibles, no runtime actual.
* **Gestión del cambio:** Si cambia el cliente, voz, sector, audiencia, oferta, canal o adaptador, evaluar impacto antes de seguir.
* **Salida final:** No exponer al usuario final prompts internos, nombres de agentes, rutas locales, logs crudos ni estructura interna.

## 7. Candidatos Futuros (No Implementados)
* **Skills candidatas:** Las skills físicas actuales en `.agents/skills/` son solo de gobernanza agéntica. Las skills de producto LinkedIn no existen todavía y se documentan únicamente en `docs/08_skills_producto_linkedin_futuras.md`. No crear skills de producto sin contrato aprobado, validación de Marketing/RRSS y uso de `crear-skill-desde-contrato`.
* **Gates candidatos:** Validar entrada; validar PII/sanitización; validar calidad editorial; validar aprobación humana; validar publicación/dry_run; validar evidencia local; validar ausencia de rutas absolutas/secretos.

## 8. Reporte y Cierre de Tarea
Cada reporte del agente debe declarar obligatoriamente:
1. Archivos leídos, creados o modificados.
2. Comandos ejecutados y validaciones hechas.
3. Estado Git y búsqueda de rutas locales absolutas.
4. Riesgos pendientes.
5. Veredicto:
   * **PASS:** Cumple alcance y restricciones.
   * **WARN:** Cumple con riesgos menores.
   * **FAIL:** Incumple criterios de aceptación.
   * **BLOQUEADO:** Requiere tocar archivos prohibidos o abrir código sin autorización.

## 9. Control Git
* Ejecutar `git status --short` si existe repositorio Git. Prohibido hacer commits o push sin aprobación explícita.
