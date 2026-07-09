# Plan 001: Consolidar el flujo util textual end-to-end

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report - do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e5bd839..HEAD -- src/linkedin_content_system/use_cases/__init__.py src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py src/linkedin_content_system/cli/__init__.py src/linkedin_content_system/cli/flujo_textual.py tests/use_cases/test_exports_use_cases.py tests/use_cases/test_ejecutar_flujo_textual.py tests/cli/test_flujo_textual.py`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `e5bd839`, 2026-07-08

## Why this matters

The repo already has the pieces to validate and persist a safe local draft, but
it still does not expose the product flow that the current docs define as the
first success condition. The target is explicit in
`docs/05_fases_implementacion.md:14-35`: `texto manual -> normalizacion minima -> extraccion de idea e intencion -> generacion de pieza -> validacion -> aprobacion humana -> LocalDraft listo`.

`docs/09_plan_implementacion_post_planeacion.md:67-79` also says the next
operational step is to consolidate `texto manual -> post usable -> revision ->
aprobacion -> LocalDraft`. Until that exists as one callable use case plus one
operator-facing entrypoint, the repo remains strong in contracts and controls
but weak in actual product usefulness.

## Current state

- Product intent and scope:
  - `docs/00_brief_arquitectura_pre_codigo.md:61-71` defines the first useful cut as manual text, LinkedIn post generation, validation, human approval, and local draft output.
  - `docs/01_alcance_si_no.md:16-25` keeps text input first, LinkedIn as probable initial channel, and requires usable human approval and local-ready output.
  - `AGENTS.md:31-36` says "Texto primero" and "LinkedIn como arranque probable, no obligatorio ni unico".

- Input contract is already prepared for the new product direction:
  - `src/linkedin_content_system/contracts/entrada.py:48-57` defines `EntradaContenido` with `tipo_entrada`, `texto_base`, `canales_destino`, `estado_privacidad`, and `restricciones`.
  - `src/linkedin_content_system/contracts/entrada.py:60-76` already enforces non-empty text and normalized non-duplicate channels.
  - Excerpt:

```python
# src/linkedin_content_system/contracts/entrada.py:48-57
class EntradaContenido(BaseModel):
    id_entrada: str
    tipo_entrada: TipoEntrada
    fecha_creacion: Optional[str] = None
    texto_base: str
    intencion_editorial: IntencionEditorial
    perfil_narrativo: PerfilNarrativoReferencia
    canales_destino: List[str] = Field(default_factory=lambda: ["linkedin"])
```

- Deterministic building blocks already exist:
  - `src/linkedin_content_system/use_cases/extraer_idea_central.py:4-28`
  - `src/linkedin_content_system/use_cases/extraer_intencion_editorial.py:5-51`
  - `src/linkedin_content_system/use_cases/diagnosticar_base_editorial.py:6-83`
  - `src/linkedin_content_system/use_cases/generar_post_mock.py:4-14`
  - Excerpt:

```python
# src/linkedin_content_system/use_cases/generar_post_mock.py:4-14
def generar_post_mock(texto_base: str, adapter: ModelAdapter) -> str:
    if not texto_base or not texto_base.strip():
        raise ValueError("El texto base no puede estar vacío.")
    if adapter is None:
        raise ValueError("El adapter no puede ser None.")
    return adapter.generar_texto(prompt=texto_base.strip())
```

- Safe local output already exists:
  - `src/linkedin_content_system/flows/simulacion_local.py:11-59` assembles `SalidaLocalDraft` and simulated evidence in memory.
  - `src/linkedin_content_system/use_cases/generar_borrador_local.py:8-31` persists that flow using `LocalDraftPublisher`.
  - `src/linkedin_content_system/publishers/localdraft.py:13-69` writes `post.md`, `diagnostico.json`, `salida_v1.json`, and `manifest.json` under `localdraft_<id_entrada>/`.
  - Excerpt:

```python
# src/linkedin_content_system/use_cases/generar_borrador_local.py:8-16
def generar_borrador_local_desde_simulacion(
    entrada: EntradaContenido,
    post: PostCandidato,
    diagnostico: DiagnosticoEditorial,
    aprobacion: AprobacionHumana,
    base_dir: str,
    clock: Optional[Callable[[], str]] = None,
```

- Publication safety already exists and should be reused, not reimplemented:
  - `src/linkedin_content_system/validators/publicacion.py:33-76` resolves `EstadoPublicabilidad`.
  - `src/linkedin_content_system/validators/publicacion.py:139-151` validates the final `SalidaLocalDraft` and rejects PII, secrets, local paths, missing approval, and non-publicable states.

- There is still no end-to-end textual use case and no operator entrypoint:
  - `src/linkedin_content_system/use_cases/__init__.py:1-26` exports multiple small use cases but nothing like `ejecutar_flujo_textual`.
  - A repo-wide search for `argparse`, `click`, `typer`, `__main__`, or `if __name__ ==` returned no matches, so there is no existing CLI or local runner for this flow.

- Existing approval contracts are split:
  - `src/linkedin_content_system/contracts/salida.py:37-74` defines `AprobacionHumana`, which is what `SalidaLocalDraft` and `validators/publicacion.py` already consume.
  - `src/linkedin_content_system/contracts/validacion_aprobacion_humana.py:5-28` defines a separate `DecisionAprobacionHumana` / `ResultadoValidacionAprobacionHumana` pair used only by `use_cases/validar_aprobacion_humana.py`.
  - For this plan, do **not** widen scope to reconcile both approval systems. Use `AprobacionHumana` because it is the one already wired into the safe local draft path.

- Repo conventions to match:
  - Use small functions in `src/linkedin_content_system/use_cases/`, with deterministic validation and no hidden side effects; see `extraer_idea_central.py` and `generar_post_mock.py`.
  - Tests are pytest files under `tests/<area>/` with direct fixtures and explicit edge cases; use `tests/use_cases/test_generar_borrador_local.py:12-186` and `tests/flows/test_simulacion_local.py:13-155` as structural patterns.
  - The current verified regression command is `./.venv/bin/pytest -q`, which passed with `316 passed in 0.69s` when this plan was written.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Baseline suite | `./.venv/bin/pytest -q` | exit 0; all tests pass |
| Targeted use-case tests | `./.venv/bin/pytest -q tests/use_cases/test_ejecutar_flujo_textual.py` | exit 0 |
| Targeted CLI tests | `./.venv/bin/pytest -q tests/cli/test_flujo_textual.py` | exit 0 |
| Import smoke | `./.venv/bin/python -c "from linkedin_content_system.use_cases import ejecutar_flujo_textual"` | exit 0 |
| CLI smoke | `./.venv/bin/python -m linkedin_content_system.cli.flujo_textual --help` | exit 0 |
| Final regression | `./.venv/bin/pytest -q` | exit 0; old and new tests pass |

## Scope

**In scope** (the only files you should modify):
- `src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py` (new)
- `src/linkedin_content_system/use_cases/__init__.py`
- `src/linkedin_content_system/cli/__init__.py` (new)
- `src/linkedin_content_system/cli/flujo_textual.py` (new)
- `tests/use_cases/test_exports_use_cases.py`
- `tests/use_cases/test_ejecutar_flujo_textual.py` (new)
- `tests/cli/test_flujo_textual.py` (new)

**Out of scope** (do NOT touch, even though they look related):
- `src/linkedin_content_system/contracts/entrada.py` - already aligned with the new product direction.
- `src/linkedin_content_system/contracts/salida.py` - keep the current output contract stable in this plan.
- `src/linkedin_content_system/contracts/validacion_aprobacion_humana.py` and `src/linkedin_content_system/use_cases/validar_aprobacion_humana.py` - separate legacy approval path; not needed to close the first useful flow.
- `src/linkedin_content_system/use_cases/ejecutar_pipeline_contexto_offline.py` and any `ContextoTrabajo` files - `AGENTS.md` explicitly says not to expand that pipeline unless it unlocks product.
- Any docs, ADRs, or `AGENTS.md`.
- Any real publication adapter, credential handling, external API call, audio input, or omnichannel abstraction.

## Git workflow

- Branch: `advisor/001-consolidar-flujo-util-textual`
- No repo-specific commit convention was established during recon. If the operator asks for commits, keep them small and descriptive, one logical change per commit.
- Do NOT push or open a PR unless the operator explicitly asks.

## Steps

### Step 1: Add failing tests for the missing end-to-end textual flow

Create `tests/use_cases/test_ejecutar_flujo_textual.py` first, before writing production code.
Model its fixture style after `tests/use_cases/test_generar_borrador_local.py` and its
behavioral assertions after `tests/flows/test_simulacion_local.py`.

The new test file should cover at least these cases:

1. Happy path:
   - `EntradaContenido` with `TipoEntrada.TEXTO_MANUAL`
   - `canales_destino` containing `linkedin` (it may contain additional channels too)
   - `MockModelAdapter`
   - approved `AprobacionHumana`
   - temp output directory
   - expected result: localdraft directory exists, manifest is returned, and `post.md` contains generated text.
2. Reject non-text input:
   - same shape, but `tipo_entrada != TipoEntrada.TEXTO_MANUAL`
   - expected result: `ValueError` with a clear message that this use case only closes the textual flow.
3. Reject missing LinkedIn in the target channels for this first cut:
   - `canales_destino=["x"]` or equivalent
   - expected result: `ValueError`
   - do **not** require LinkedIn to be the only channel; only require that this flow can produce the initial LinkedIn draft.
4. Reject non-approved output:
   - approved flow should write files
   - pending or rejected approval should raise and leave no artifact directory.
5. Preserve deterministic wiring:
   - use a spy adapter implementing `ModelAdapter`
   - assert the prompt passed into the adapter contains the original `texto_base`
   - also assert it includes at least one derived signal from the deterministic extraction path (`idea_central` or classified intention summary), so the new flow is not just a thin alias to `generar_post_mock(texto_base, adapter)`.

Keep the tests focused on the new flow contract. Do not test `LocalDraftPublisher` internals again beyond artifact existence; those paths are already covered elsewhere.

**Verify**: `./.venv/bin/pytest -q tests/use_cases/test_ejecutar_flujo_textual.py` -> fails because the new use case does not exist yet.

### Step 2: Implement one orchestration use case for the textual flow

Create `src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py` with a
single public function named `ejecutar_flujo_textual`.

Target shape:

- Inputs:
  - `entrada: EntradaContenido`
  - `adapter: ModelAdapter`
  - `aprobacion: AprobacionHumana`
  - `base_dir: str`
  - optional `clock`
- Output:
  - return the `ManifestEvidencia` produced by `generar_borrador_local_desde_simulacion`

Required orchestration order:

1. Validate that the flow is only used for `TipoEntrada.TEXTO_MANUAL`.
2. Validate that `"linkedin"` is present in `entrada.canales_destino`.
3. Derive `IdeaCentral` by calling `extraer_idea_central(entrada.texto_base)`.
4. Derive `IntencionEditorialClasificada` by calling `extraer_intencion_editorial(...)`.
5. Run `diagnosticar_base_editorial(...)`.
6. Build a deterministic prompt string locally inside this module.
   - Do not change `ModelAdapter`.
   - Do not add a generic prompt framework.
   - The prompt must include:
     - `entrada.texto_base`
     - `idea.idea_central`
     - `intencion.resumen_intencion`
     - any explicit user intent already present in `entrada.intencion_editorial` that helps preserve voice or audience
7. Generate the post text using the injected adapter.
8. Wrap it into `PostCandidato`.
9. Create a minimal deterministic `DiagnosticoEditorial` in this same module.

For the temporary deterministic `DiagnosticoEditorial`, keep it intentionally narrow.
Do **not** invent a new architecture layer. Use one private helper in this module,
with heuristics explicit enough to test. Recommended baseline:

- `compliance=FAIL` only if the generated text cannot pass the existing privacy/secret/local-path validators.
- `claridad_idea=PASS` when the post is non-empty and contains some signal from the extracted idea; otherwise `WARN`.
- `audiencia=PASS` when `entrada.intencion_editorial.audiencia_objetivo` is present; otherwise `WARN`.
- `hook=PASS` when the first line exists and is not blank; otherwise `WARN`.
- `voz_cliente=PASS` when `perfil_narrativo.id_perfil` exists and the prompt included it or equivalent voice context; otherwise `WARN`.
- `autenticidad=PASS` by default unless compliance or traceability already force a harder state.
- `cta=PASS` only if the generated text contains an explicit conversational or action-oriented close; otherwise `WARN`.
- `riesgo_generico=BAJO` unless compliance fails.
- `estado_revision=FAIL` on compliance failure, `WARN` if any field is `WARN`, otherwise `PASS`.

This helper must remain deterministic and side-effect free. Keep the heuristics
documented by tests, not by new docs.

10. Call `generar_borrador_local_desde_simulacion(...)` with the original `entrada`,
    the generated `PostCandidato`, the deterministic `DiagnosticoEditorial`, the
    supplied `AprobacionHumana`, and `base_dir`.

Important boundaries:

- Reuse the existing validators and publisher path. Do not reimplement path checks,
  publicability checks, traceability checks, or file writing.
- Stay local-first. No real network, no credentials, no provider-specific code.
- If the deterministic editorial helper becomes impossible to express without
  changing existing contracts, stop and report rather than creating a second
  parallel contract family.

**Verify**:
- `./.venv/bin/python -c "from linkedin_content_system.use_cases import ejecutar_flujo_textual"` -> exit 0
- `./.venv/bin/pytest -q tests/use_cases/test_ejecutar_flujo_textual.py` -> all pass

### Step 3: Export the new use case through the existing package surface

Update `src/linkedin_content_system/use_cases/__init__.py` to export
`ejecutar_flujo_textual`, following the current flat export style.
Also update `tests/use_cases/test_exports_use_cases.py` so the export is covered.

Do not reorganize the package or create a broader application layer in this step.
Keep the diff surgical and consistent with the current `__all__` style.

**Verify**:
- `./.venv/bin/python -c "from linkedin_content_system.use_cases import ejecutar_flujo_textual"` -> exit 0
- `./.venv/bin/pytest -q tests/use_cases/test_exports_use_cases.py tests/use_cases/test_ejecutar_flujo_textual.py` -> all pass

### Step 4: Add a minimal operator-facing CLI for human approval and local output

Create a new package `src/linkedin_content_system/cli/` with:

- `__init__.py`
- `flujo_textual.py`

Use only the standard library (`argparse`, `json`, `sys`, `pathlib` or `os`).
Do not add dependencies.

The CLI must support the minimum operator workflow:

1. Read an `EntradaContenido` JSON file from disk.
2. Build an `AprobacionHumana` from explicit CLI args.
3. Execute the new `ejecutar_flujo_textual(...)` use case using `MockModelAdapter`.
4. Print a concise success message including `id_entrada` and the generated localdraft path or manifest identifier.
5. On validation failure, print a concise error to stderr, exit non-zero, and avoid partial success messaging.

Recommended CLI interface:

- `--input-json <path>` (required)
- `--output-dir <path>` (required)
- `--estado-aprobacion aprobado|pendiente|rechazado|requiere_ajustes` (required)
- `--revisor <texto>` (required when approval is approved)
- `--fecha-aprobacion <iso8601>` (optional; if omitted on approved state, generate current UTC timestamp inside the CLI)
- `--comentarios <texto>` (optional)
- `--tipo-aprobacion simple|reforzada` (default `simple`)
- `--motivo-revision-reforzada <texto>` (required when the CLI builds a reinforced approval)

Implementation rules:

- Map CLI values into the existing `AprobacionHumana` enum values, not raw strings left loose in the flow.
- Keep the CLI thin: parse args, load JSON, instantiate contracts, call the use case, print result.
- Do not duplicate business rules already enforced by Pydantic or validators, except for user-friendly preflight messages when they are trivial.
- Do not add support for real model adapters, API keys, or other channels in this plan.

**Verify**:
- `./.venv/bin/python -m linkedin_content_system.cli.flujo_textual --help` -> exit 0
- `./.venv/bin/pytest -q tests/cli/test_flujo_textual.py` -> all pass

### Step 5: Add CLI tests that prove the flow is actually operable

Create `tests/cli/test_flujo_textual.py`. Keep it local and deterministic.
Use `tmp_path` and JSON built inside the test; do not add committed fixture files.

Cover at least:

1. `--help` exits 0.
2. Approved input produces a `localdraft_<id_entrada>/` directory under the chosen output path.
3. Pending or rejected approval exits non-zero and does not write the localdraft directory.
4. Invalid JSON or contract validation failure exits non-zero with a concise error message.

Use `subprocess.run(...)` with the repo virtualenv Python to exercise the module
exactly as an operator would:

- `./.venv/bin/python -m linkedin_content_system.cli.flujo_textual ...`

Do not mock the CLI internals unless a specific branch is impossible to hit otherwise.
The point of these tests is to prove the flow is usable, not just importable.

**Verify**: `./.venv/bin/pytest -q tests/cli/test_flujo_textual.py` -> all pass

### Step 6: Run the full regression suite and confirm scope discipline

Run the full suite once the new use case and CLI are green.
Then confirm no unrelated files were touched.

**Verify**:
- `./.venv/bin/pytest -q` -> exit 0
- `git status --short` -> only the in-scope files above are modified

## Test plan

- New tests:
  - `tests/use_cases/test_ejecutar_flujo_textual.py`
  - `tests/cli/test_flujo_textual.py`
- Existing tests to use as structural patterns:
  - `tests/use_cases/test_generar_post_mock.py` for adapter injection and deterministic expectations
  - `tests/use_cases/test_generar_borrador_local.py` for artifact assertions
  - `tests/flows/test_simulacion_local.py` for approval and publicability behavior
- Coverage expectations:
  - happy path from `EntradaContenido` text input to localdraft persistence
  - rejection of unsupported input type
  - rejection when the first-cut LinkedIn channel is absent
  - prompt composition includes derived signals, not only raw text
  - CLI success and CLI failure paths

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `./.venv/bin/python -c "from linkedin_content_system.use_cases import ejecutar_flujo_textual"` exits 0
- [ ] `./.venv/bin/python -m linkedin_content_system.cli.flujo_textual --help` exits 0
- [ ] `./.venv/bin/pytest -q tests/use_cases/test_ejecutar_flujo_textual.py tests/cli/test_flujo_textual.py` exits 0
- [ ] `./.venv/bin/pytest -q` exits 0
- [ ] No files outside the in-scope list are modified (`git status --short`)
- [ ] `plans/README.md` row for plan `001` is updated by the executor after completion

## STOP conditions

Stop and report back (do not improvise) if:

- The code at the locations cited in "Current state" no longer matches the excerpts or behaviors described here.
- Closing the flow cleanly would require changing `EntradaContenido`, `SalidaLocalDraft`, `LocalDraftPublisher`, or `validators/publicacion.py`.
- You discover that the current safe local draft path cannot be driven by a deterministic `DiagnosticoEditorial` without breaking existing tests.
- The CLI appears to require a real external adapter, network call, or credential to be useful.
- A step's verification fails twice after a reasonable fix attempt.

## Maintenance notes

- This plan intentionally closes only the first useful textual slice. Audio, transcriptions, publication preparation, and real publication remain separate follow-up phases.
- The split between `AprobacionHumana` and `DecisionAprobacionHumana` is deferred on purpose. If that duplication starts causing bugs after this plan lands, address it in a separate refactor plan, not opportunistically here.
- Reviewers should pay special attention to whether the new deterministic editorial helper stays truly local-first and whether the CLI remains a thin adapter rather than a second business-logic layer.
- If later phases add other channels, revisit the `"linkedin" in canales_destino` gate in this use case rather than broadening this plan retroactively.
