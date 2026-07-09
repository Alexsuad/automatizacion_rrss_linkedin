# Plan 004: La generación textual útil se activa mediante un adaptador controlado

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step. If anything in STOP conditions happens, stop and report back. Do not touch publication code beyond what is explicitly listed here. When done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e5bd839..HEAD -- src/linkedin_content_system/ai src/linkedin_content_system/cli/flujo_textual.py src/linkedin_content_system/use_cases/generar_post_mock.py src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py tests/ai tests/use_cases tests/cli plans/README.md`
> If any in-scope file changed since this plan was written, compare the current state excerpts below with the live code before proceeding. On mismatch, stop and report only if there is a real contradiction with the plan, not just harmless drift.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED
- **Depends on**: plans/003-salida-externa-dry-run-sin-proveedor-real.md
- **Category**: direction
- **Planned at**: commit `e5bd839`, 2026-07-10

## Why this matters

Hoy el flujo textual ya está aislado por contrato, pero la generación sigue pasando por un helper de mock y por un `MockModelAdapter` que produce una salida claramente artificial. Eso sirve para seguridad, pero no para utilidad de producto. El siguiente salto valioso es introducir un adaptador de generación más útil, configurable y todavía local-safe, de forma que el repositorio pueda avanzar sin publicar nada real y sin convertir la IA en un acoplamiento duro.

## Current state

- `src/linkedin_content_system/ai/ports.py:5-20` define `ModelAdapter`, el puerto interno que desacopla el núcleo de proveedores concretos.
- `src/linkedin_content_system/ai/mock_adapter.py:6-30` contiene `MockModelAdapter`, que devuelve un texto determinista con la marca `[BORRADOR SIMULADO DE POST]`.
- `src/linkedin_content_system/use_cases/generar_post_mock.py:4-14` solo delega en `adapter.generar_texto(...)`; el nombre sigue anclado al mock aunque el puerto ya sea genérico.
- `src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py:141-172` orquesta el flujo textual y llama a `generar_post_mock(...)` antes de persistir en `LocalDraft`.
- `src/linkedin_content_system/cli/flujo_textual.py:78-90` instancia `MockModelAdapter()` directamente en el camino normal del CLI.
- `tests/ai/test_mock_adapter.py:5-61` valida el comportamiento determinista actual del mock.
- `tests/use_cases/test_ejecutar_flujo_textual.py:48-155` asegura que el flujo textual siga funcionando y hoy todavía espera la marca del mock en una rama de test.
- `tests/cli/test_flujo_textual.py:53-80` cubre el CLI, que hoy también arranca con `MockModelAdapter`.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Full tests | `python -m pytest -q` | exit 0 |
| Compile check | `python -m compileall -q src tests` | exit 0 |
| Secret/path grep | `rg -n -e "/home/" -e "file:///" -e "C:/Users" -e "C:\\\\Users" -e "/mnt/data" -e "\\\\\\\\wsl\\$" src tests plans docs` | no new matches in touched code |
| Provider grep | `rg -n "metricool|mcp|api_key|OPENAI_API_KEY|GEMINI|DEEPSEEK|ANTHROPIC|Bearer|sk-" src tests plans docs` | only expected historical/test references |

## Scope

**In scope**:
- `src/linkedin_content_system/ai/ports.py`
- `src/linkedin_content_system/ai/mock_adapter.py`
- `src/linkedin_content_system/ai/__init__.py`
- `src/linkedin_content_system/ai/` new file or files for a controlled adapter/factory
- `src/linkedin_content_system/use_cases/generar_post_mock.py`
- `src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py`
- `src/linkedin_content_system/cli/flujo_textual.py`
- `tests/ai/test_mock_adapter.py`
- `tests/ai/test_*` new tests for the controlled adapter
- `tests/use_cases/test_ejecutar_flujo_textual.py`
- `tests/cli/test_flujo_textual.py`
- `plans/README.md`

**Out of scope**:
- `src/linkedin_content_system/publishers/` and any publication behavior
- `docs/Control/`
- any real provider SDK, API key plumbing, network call, or credential file
- package renames
- `Metricool`, `MCP`, or publication real

## Steps

### Step 1: Lock the desired behavior before changing the wiring

Add or adjust characterization tests so the repo makes one thing explicit: the use case needs useful editorial text, not the literal mock marker. Keep the existing mock tests that prove determinism and offline safety, but add a new test for the future controlled adapter shape: richer body, clear hook, CTA, and no dependency on network or secrets.
Apply TDD proportionally here: write the behavioral test first, then the smallest implementation that makes it pass, then re-run the focused test command before moving on.

**Verify**: `python -m pytest -q tests/ai tests/use_cases tests/cli` → all green with the new characterization test passing.

### Step 2: Introduce a controlled adapter path in `src/linkedin_content_system/ai/`

Add a new adapter or small factory that still implements `ModelAdapter`, but can be selected in a controlled way from code configuration rather than being hardcoded to `MockModelAdapter`. The default path should remain local-safe. If the new adapter is semireal, it must still be deterministic or locally reproducible in tests and must not require network or credentials. Keep `MockModelAdapter` as the fallback and as the stable test double.

**Verify**: `python -m pytest -q tests/ai` → the adapter tests pass and there is no test that requires external connectivity.

### Step 3: Switch composition, not the contract

Update the CLI composition root so it instantiates the selected adapter via the new control point instead of hardcoding `MockModelAdapter()`. Keep `ejecutar_flujo_textual(...)` injecting a `ModelAdapter` exactly as it does now; do not expand the use case signature. If `generar_post_mock(...)` stays for compatibility, make it a thin wrapper only; if it is no longer needed, remove it only after confirming no call sites remain inside the repo.
Do not remove `generar_post_mock.py` unless the executor verifies that all call sites are gone and the deletion is a small, local change.

**Verify**: `python -m pytest -q tests/cli tests/use_cases` → the CLI still writes `LocalDraft`, and the textual flow still passes with injected adapters.

### Step 4: Re-baseline the suite and the index

Run the full test suite and compile check. Then update `plans/README.md` so Plan 004 appears in order with the correct dependency on Plan 003 and a TODO status until execution lands.

**Verify**: `python -m pytest -q` and `python -m compileall -q src tests` → both exit 0; `git status --short` shows only the intended plan/docs changes for this handoff.

## Test plan

- Add a focused test for the new controlled adapter in `tests/ai/`.
- Keep `tests/ai/test_mock_adapter.py` as the regression fence for offline determinism.
- Keep `tests/use_cases/test_ejecutar_flujo_textual.py` asserting that the textual flow still reaches `LocalDraft` with injected adapters.
- Keep `tests/cli/test_flujo_textual.py` proving the CLI path still works end to end.
- Verification command: `python -m pytest -q` → all pass, including the new adapter coverage.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] The CLI no longer hardcodes `MockModelAdapter` as the only composition path.
- [ ] There is a controlled adapter path in `src/linkedin_content_system/ai/` that still honors `ModelAdapter`.
- [ ] `MockModelAdapter` remains available and offline-safe for tests.
- [ ] The textual flow still produces `LocalDraft` and does not touch publication code.
- [ ] `python -m pytest -q` exits 0.
- [ ] `python -m compileall -q src tests` exits 0.
- [ ] The grep commands above do not reveal new unauthorized providers, secrets, or local path leaks in touched code.
- [ ] `plans/README.md` lists Plan 004 with the right dependency and status.
- [ ] The final report includes `git diff --name-only`, `git diff --stat`, and an explicit confirmation that `src/linkedin_content_system/publishers/` and `docs/Control/` were not touched.

## STOP conditions

Stop and report back if:

- The new adapter would need a real provider SDK, API key, or network call to be useful.
- `generar_post_mock(...)` turns out to be imported from outside this repository or from an out-of-scope module you did not inspect.
- The only way to make the new adapter work is to change publication code, `docs/Control/`, or the package name.
- The new output cannot stay local-safe while being more useful than the current mock.

## Maintenance notes

- Future provider integrations should slot behind the same `ModelAdapter` seam; do not bypass it from the CLI or use case.
- Keep `MockModelAdapter` as the simplest regression tool even after the controlled adapter lands.
- Reviewers should pay special attention to whether the new path adds hidden config, hidden network dependencies, or a second generation abstraction that duplicates the existing one.
