# Plan 003: Salida externa dry-run sin proveedor real

> **Executor instructions**: Este plan prepara una salida externa simulada sin conectar Metricool, MCP, API keys ni proveedores reales. Sigue el orden de los pasos y no conviertas esta fase en una integración real por accidente.
>
> **Drift check (run first)**: `git diff --stat e5bd839..HEAD -- plans/README.md plans/002-saneamiento-rumbo-y-frontera-publicacion-portable.md plans/003-salida-externa-dry-run-sin-proveedor-real.md docs/04_contrato_salida.md docs/09_plan_implementacion_post_planeacion.md src/linkedin_content_system/publishers/ports.py src/linkedin_content_system/publishers/dryrun.py src/linkedin_content_system/publishers/__init__.py tests/publishers/test_dryrun_publisher.py tests/publishers/test_publisher_port.py`
> Si alguno de los archivos en alcance cambió desde la redacción de este plan, compara el estado vivo con los fragmentos de contexto antes de avanzar. Si no coincide, para y reporta.

## Estado

- **Prioridad**: P1
- **Esfuerzo**: M
- **Riesgo**: MED
- **Depends on**: plans/002-saneamiento-rumbo-y-frontera-publicacion-portable.md
- **Categoría**: direction
- **Planned at**: commit `e5bd839`, 2026-07-08
- **Estado final**: DONE

## Objetivo

Crear una fase coherente para preparar una salida externa simulada o `dry_run` usando la frontera portable de publicación ya creada, sin publicar nada realmente y sin conectar aún proveedores externos. El resultado debe dejar evidencia local verificable de cómo quedaría una publicación externa preparada.

## Alcance

- Crear un publisher dry-run que cumpla `PublicationPublisherPort`.
- Persistir evidencia local en una carpeta propia `external_dryrun_<id_entrada>/`.
- Declarar en la evidencia que el modo es `dry_run`, el proveedor es `simulated_external` y que no hubo publicación real.
- Mantener `LocalDraftPublisher` funcionando sin romper tests.
- Añadir tests específicos para el nuevo publisher y para la frontera compartida.
- Afinar mínimamente `docs/04` y `docs/09` para reflejar esta etapa futura.

## Fuera de alcance

- No crear `MetricoolPublisher`, `MCP`, `OpenAIPublisher`, `GeminiPublisher` ni integraciones reales.
- No usar red.
- No tocar el flujo textual ya aceptado.
- No tocar `LocalDraftPublisher` salvo compatibilidad del puerto o seguridad si fuera estrictamente necesario.
- No modificar `docs/06_contrato_calidad_post_linkedin.md`.
- No modificar `docs/08_skills_producto_linkedin_futuras.md`.
- No tocar credenciales ni `.env`.
- No renombrar `src/linkedin_content_system`.

## Criterios de aceptación

1. Existe un `ExternalDryRunPublisher` o equivalente.
2. Cumple `PublicationPublisherPort`.
3. Persiste una evidencia local verificable en `external_dryrun_<id_entrada>/`.
4. La evidencia declara explícitamente `modo=dry_run`, `proveedor=simulated_external` y `no_publicado_realmente=true`.
5. No hay proveedor real ni red.
6. No rompe `LocalDraftPublisher`.
7. No toca el flujo textual aceptado.
8. La suite completa pasa.

## Verificación

- `./.venv/bin/python -m pytest -q tests/publishers`
- `./.venv/bin/python -m pytest -q`
- `./.venv/bin/python -m compileall -q src tests`
- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `rg -n "/home/|file:///|C:/Users|C:\\\\Users|/mnt/data|\\\\\\\\wsl\\$" plans docs src tests`
- `rg -n "metricool|mcp|api_key|OPENAI_API_KEY|GEMINI|DEEPSEEK|ANTHROPIC|Bearer|sk-" src tests plans docs`

## Deuda técnica esperada

- `LocalDraftPublisher` seguirá siendo la implementación local principal y todavía no habrá un adaptador externo real.
- La evidencia externa seguirá siendo simulada y local, por lo que la frontera de publicación quedará lista pero no operativa con proveedores.
- El repositorio conservará terminología histórica vinculada a LinkedIn en documentos no tocados por esta misión.

## Relación con planes anteriores

- `Plan 001` dejó listo el flujo textual offline/mock con aprobación humana y `LocalDraft`.
- `Plan 002` saneó el rumbo y creó la frontera portable de publicación.
- `Plan 003` usa esa frontera para preparar una salida externa simulada sin integrar proveedores reales.

## Pasos

### Paso 1: Declarar la etapa en documentación de transición

Actualizar `docs/04_contrato_salida.md` y `docs/09_plan_implementacion_post_planeacion.md` para introducir la salida externa simulada como evolución futura de la frontera portable.

**Verificar**: la documentación menciona claramente `dry_run`, `simulated_external` y que no se trata de una publicación real.

### Paso 2: Crear el publisher dry-run

Implementar `src/linkedin_content_system/publishers/dryrun.py` con un publisher que cumpla `PublicationPublisherPort`, escriba su propia carpeta `external_dryrun_<id_entrada>/` y genere evidencia local verificable.

**Verificar**: importar el publisher sin errores y crear evidencia local sin usar red.

### Paso 3: Exportar la frontera

Actualizar `src/linkedin_content_system/publishers/__init__.py` para exportar el nuevo publisher y mantener `PublicationPublisherPort` accesible.

**Verificar**: `from linkedin_content_system.publishers import ExternalDryRunPublisher` funciona.

### Paso 4: Cubrir con tests

Crear `tests/publishers/test_dryrun_publisher.py` para comprobar contrato, persistencia, anti-overwrite, path traversal, seguridad de contenido y no uso de red.

**Verificar**: `./.venv/bin/python -m pytest -q tests/publishers/test_dryrun_publisher.py tests/publishers/test_publisher_port.py tests/publishers/test_localdraft.py` -> exit 0.

### Paso 5: Cerrar con regresión completa

Ejecutar la suite completa, `compileall` y el grep de contaminación.

**Verificar**: todas las comprobaciones de la sección "Verificación" pasan.

## Test plan

- Nuevo test: `tests/publishers/test_dryrun_publisher.py`
- Tests a preservar:
  - `tests/publishers/test_localdraft.py`
  - `tests/publishers/test_publisher_port.py`
- Casos mínimos:
  - crea carpeta y archivos esperados;
  - evidencia con `dry_run`, `simulated_external` y `no_publicado_realmente=true`;
  - rechazo de sobrescritura silenciosa;
  - rechazo de `id_entrada` vacío o con traversal;
  - rechazo de contenido inseguro;
  - no usa red.

## Criterios de cierre

- [ ] `ExternalDryRunPublisher` existe y cumple el puerto.
- [ ] `tests/publishers/test_dryrun_publisher.py` existe y pasa.
- [ ] `./.venv/bin/python -m pytest -q tests/publishers` pasa.
- [ ] `./.venv/bin/python -m pytest -q` pasa.
- [ ] `./.venv/bin/python -m compileall -q src tests` pasa.
- [ ] `rg -n ...` no muestra contaminación nueva en código activo.

## STOP conditions

Para y reporta si:

- Hacer el dry-run externo obliga a conectar un proveedor real o a crear una arquitectura paralela.
- La evidencia local no puede expresar el modo `dry_run` y `no_publicado_realmente` sin tocar contratos base.
- El contenido de la salida requiere modificar el flujo textual ya aceptado.
- El grep descubre API keys, red o nombres de proveedores reales en código productivo nuevo.
