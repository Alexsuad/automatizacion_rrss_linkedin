# Plan 005: Prueba de valor del flujo textual local con entrada realista

> **Executor instructions**: Follow this plan step by step. Keep the scope small: prove whether the current controlled textual flow already yields a useful LocalDraft from a realistic text input. Do not introduce real providers, network, Metricool, MCP or audio. When done, update `plans/README.md`.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/004-generacion-textual-util-con-adapter-controlado.md
- **Category**: tests
- **Planned at**: commit `38ec530`, 2026-07-10

## Why this matters

We already have a local portable flow, but we still need a realistic answer to a product question: does `texto manual -> ControlledModelAdapter -> LocalDraft` look useful enough to justify moving toward real AI later?

## Current state

- `src/linkedin_content_system/ai/controlled_adapter.py` already builds a useful local draft from the textual prompt.
- `src/linkedin_content_system/cli/flujo_textual.py` already routes the CLI through the controlled adapter by default.
- `tests/use_cases/test_ejecutar_flujo_textual_controlado.py` exists and can be extended to characterize a realistic input.

## Scope

**In scope**:
- `plans/README.md`
- `plans/005-prueba-valor-flujo-textual-local.md`
- `src/linkedin_content_system/ai/controlled_adapter.py`
- `tests/ai/test_controlled_adapter.py`
- `tests/cli/test_flujo_textual.py`
- `tests/use_cases/test_ejecutar_flujo_textual_controlado.py`

**Out of scope**:
- `src/linkedin_content_system/publishers/`
- `src/linkedin_content_system/contracts/`
- `src/linkedin_content_system/use_cases/ejecutar_flujo_textual.py`
- `docs/`
- `docs/Control/`
- provider SDKs, keys, network, Metricool, MCP, audio, visuals, analytics

## Steps

1. Add a compact plan entry to `plans/README.md` and create this file as the versionable plan record.
2. Use a realistic Spanish text input to exercise the CLI end-to-end with `ControlledModelAdapter`.
3. If the output still feels obviously repetitive or mock-like, make the smallest possible adjustment in `controlled_adapter.py` and cover it with a test.
4. Add or tune characterisation tests so the expected output contains a legible hook, a clear development line, a reasonable CTA, and no mock marker.
5. Run `uv run python -m pytest -q tests/ai tests/cli tests/use_cases`, then `uv run python -m pytest -q`, then `uv run python -m compileall -q src tests`.

## Acceptance criteria

- The CLI with a realistic text input generates a `LocalDraft`.
- The output reads like a human-usable draft, not a mock stub.
- The controlled adapter preserves the user's explicit idea and CTA.
- No real provider, network, Metricool or MCP is introduced.
- Tests and compileall pass.

## STOP conditions

- If the only way to get a useful draft is to touch publishers, contracts, or the main textual use case.
- If the output requires a real AI provider or network.
- If the resulting evidence would need to version sensitive data or local absolute paths.

