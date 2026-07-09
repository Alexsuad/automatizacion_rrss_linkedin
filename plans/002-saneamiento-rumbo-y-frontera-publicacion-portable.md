# Plan 002: Saneamiento de rumbo y frontera portable de publicacion

> **Executor instructions**: Este plan consolida el rumbo del repositorio como Portable Content Publisher y deja lista una frontera genérica de publicación sin abrir integraciones reales. Sigue las verificaciones al final de cada paso y no improvises si un supuesto no encaja con el estado real del repo.
>
> **Drift check (run first)**: `git diff --stat e5bd839..HEAD -- pyproject.toml AGENTS.md plans/README.md docs/Control/README.md docs/03_contrato_perfil_narrativo.md docs/04_contrato_salida.md docs/09_plan_implementacion_post_planeacion.md src/linkedin_content_system/publishers/ports.py src/linkedin_content_system/publishers/localdraft.py src/linkedin_content_system/publishers/__init__.py tests/publishers/test_publisher_port.py tests/publishers/test_localdraft.py`
> Si algún archivo en alcance cambió desde que se redactó este plan, compara los fragmentos de "Estado actual" contra el código vivo antes de seguir. Si hay desajuste, para y reporta.

## Estado

- **Prioridad**: P1
- **Esfuerzo**: M
- **Riesgo**: MED
- **Depende de**: plans/001-consolidar-flujo-util-textual.md
- **Categoría**: direction
- **Planned at**: commit `e5bd839`, 2026-07-08
- **Estado inicial**: DONE

## Objetivo

Dejar el repositorio presentado y organizado como un Portable Content Publisher, con LinkedIn tratado como primer canal implementado y no como identidad total del sistema. Al mismo tiempo, establecer un puerto mínimo de publicación que describa la capacidad genérica de preparar o guardar una salida sin acoplarla a `LocalDraftPublisher` como única implementación.

## Alcance

- Ajustar el rumbo documental y de metadata para que el producto deje de presentarse como LinkedIn-only.
- Crear una frontera portable de publicación en `src/linkedin_content_system/publishers/ports.py`.
- Adaptar `LocalDraftPublisher` a ese puerto sin cambiar su comportamiento aceptado.
- Añadir tests del puerto y mantener los tests existentes de `LocalDraftPublisher`.
- Aislar `docs/Control` como histórico/no rector.

## Fuera de alcance

- No tocar el flujo textual ya aceptado.
- No crear `MetricoolPublisher`, `OpenAIPublisher`, `GeminiPublisher` ni ningún adaptador real.
- No usar red.
- No tocar credenciales, `.env`, API keys, MCP o integraciones externas.
- No renombrar `src/linkedin_content_system`.
- No hacer refactor masivo ni mover contratos base.

## Criterios de aceptación

1. El proyecto se describe como Portable Content Publisher, no como producto LinkedIn-only.
2. LinkedIn queda explícito como primer canal implementado, no como identidad total.
3. `docs/Control` queda marcado como histórico y no rector.
4. Existe un puerto genérico de publicación.
5. `LocalDraftPublisher` cumple ese puerto.
6. `LocalDraftPublisher` mantiene su comportamiento de seguridad y persistencia local.
7. La suite completa sigue pasando.
8. No hay integración externa real.

## Verificación

- `./.venv/bin/python -m pytest -q tests/publishers`
- `./.venv/bin/python -m pytest -q`
- `./.venv/bin/python -m compileall -q src tests`
- `git status --short`
- `git diff --stat`
- `git diff --name-only`
- `rg -n "/home/|file:///|C:/Users|C:\\\\Users|/mnt/data|\\\\\\\\wsl\\$" pyproject.toml plans AGENTS.md docs src tests`

## Estado actual

- `pyproject.toml` todavía describe el proyecto como un sistema de LinkedIn a partir de borradores de voz.
- `AGENTS.md` ya habla de sistema portable, pero conviene reforzar que `docs/Control` es histórico y que LinkedIn no es la identidad total.
- `docs/03_contrato_perfil_narrativo.md` y `docs/04_contrato_salida.md` siguen nombrando LinkedIn en la primera frase y necesitan una lectura más portable.
- `docs/09_plan_implementacion_post_planeacion.md` ya tiene una transición útil, pero le falta explicitar la frontera portable de publicación y la secuencia futura.
- `src/linkedin_content_system/publishers/localdraft.py` ya protege contra sobrescritura y degrada borradores mock a `no_publicable`; no debe perderse eso.
- `src/linkedin_content_system/publishers/__init__.py` aún solo expone `LocalDraftPublisher`, así que la frontera portable no existe todavía.

## Pasos

### Paso 1: Alinear metadata y documentos de rumbo

Actualizar `pyproject.toml`, `AGENTS.md`, `docs/Control/README.md`, `docs/03_contrato_perfil_narrativo.md`, `docs/04_contrato_salida.md` y `docs/09_plan_implementacion_post_planeacion.md` para que el proyecto se lea como Portable Content Publisher con LinkedIn como primer canal.

**Verificar**: leer los archivos editados y comprobar que ya no presentan LinkedIn como identidad total del producto.

### Paso 2: Crear el puerto genérico de publicación

Crear `src/linkedin_content_system/publishers/ports.py` con un protocolo mínimo para `guardar(...)` que represente la capacidad de persistir o preparar una salida de publicación sin depender de `LocalDraftPublisher`.

**Verificar**: importar el puerto desde `src/linkedin_content_system/publishers/ports.py` sin errores.

### Paso 3: Hacer que LocalDraftPublisher cumpla el puerto

Adaptar `src/linkedin_content_system/publishers/localdraft.py` si hace falta para que encaje de forma explícita con el puerto, pero sin alterar su comportamiento aceptado: sigue guardando localmente, sigue rechazando sobrescritura silenciosa y sigue dejando el mock como `no_publicable`.

**Verificar**: `tests/publishers/test_localdraft.py` sigue pasando sin cambios funcionales no deseados.

### Paso 4: Exponer la frontera y cubrirla con tests

Exportar el puerto desde `src/linkedin_content_system/publishers/__init__.py` si corresponde y añadir `tests/publishers/test_publisher_port.py` para comprobar que `LocalDraftPublisher` conforma el puerto y que el contrato mínimo de `guardar` queda estable.

**Verificar**: `./.venv/bin/python -m pytest -q tests/publishers/test_publisher_port.py tests/publishers/test_localdraft.py` -> exit 0.

### Paso 5: Cerrar la fase con regresión completa

Ejecutar la suite completa, el `compileall` y el grep de contaminación para asegurar que no se introdujo acoplamiento a proveedores reales ni rutas locales en código nuevo.

**Verificar**: todas las comprobaciones de la sección "Verificación" pasan.

## Test plan

- Nuevo test: `tests/publishers/test_publisher_port.py`
- Tests existentes a preservar:
  - `tests/publishers/test_localdraft.py`
- Patrones a seguir:
  - tests simples, estructurales, sin mocks complejos
  - assertions sobre comportamiento observable, no sobre detalles internos del puerto

## Criterios de cierre

- [ ] `pyproject.toml` ya no describe el producto como LinkedIn-only.
- [ ] `docs/Control/README.md` existe y deja claro que `docs/Control` es histórico/no rector.
- [ ] `src/linkedin_content_system/publishers/ports.py` existe.
- [ ] `LocalDraftPublisher` cumple el puerto.
- [ ] `tests/publishers/test_publisher_port.py` existe y pasa.
- [ ] `./.venv/bin/python -m pytest -q` pasa.
- [ ] `./.venv/bin/python -m compileall -q src tests` pasa.
- [ ] `rg -n ...` no muestra contaminación nueva en código o documentación activa.

## STOP conditions

Para y reporta si:

- Alguno de los documentos permitidos exige tocar `docs/06` o `docs/08`.
- La frontera portable no puede expresarse sin crear una arquitectura paralela.
- Hacer que `LocalDraftPublisher` cumpla el puerto obliga a cambiar su comportamiento aceptado.
- El grep descubre rutas locales o secretos reales en archivos activos no diseñados como fixtures negativos.
