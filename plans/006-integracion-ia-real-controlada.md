# Plan 006: Integración IA real controlada detrás de `ModelAdapter`

> **Executor instructions**: Follow this plan step by step. Keep the seam existing and never let the real provider escape `ai/`. Default behavior must remain offline-safe. When done, update `plans/README.md` with the final status.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: HIGH
- **Depends on**: plans/005-prueba-valor-flujo-textual-local.md
- **Category**: integration
- **Planned at**: 2026-07-10
- **Status after implementation**: IMPLEMENTED_PENDING_REAL_SMOKE

## Objective

Add a real AI generation path behind `ModelAdapter` so the repository can switch from the controlled local adapter to a provider-backed adapter without changing the core flow, publishing code, or contracts.

## Product value

This plan answers the next product question: can the same textual flow produce useful drafts with a real provider when configuration enables it, while staying safe, testable, and reversible?

## Current state

- `ModelAdapter` already exists and is consumed by the CLI and use cases.
- `ControlledModelAdapter` is the default safe path.
- `MockModelAdapter` remains available for deterministic tests.
- The ADR already lists LiteLLM as an evaluable provider option.

## Chosen provider layer

Use LiteLLM behind `ModelAdapter`.

Why:

- it matches the existing ADR as an evaluable option;
- it keeps provider selection outside the core;
- it allows a single seam for future provider changes.

## Configuration variables

- `LINKEDIN_CONTENT_AI_ADAPTER` with values `controlled`, `mock`, or `litellm`.
- provider/model variables consumed only by the adapter layer.
- timeout settings with a finite default.
- standard provider credentials from environment only.

## Fallback policy

- Default: `controlled`.
- Explicit `mock`: deterministic tests and local fallback.
- Explicit real provider: use LiteLLM only when configured.
- Unknown adapter: fail clearly.
- Missing credential or provider failure: raise a clear adapter/configuration error and never publish.

## Test policy

- Offline tests must keep passing without internet.
- Real-provider code must be testable with monkeypatch or a fake client.
- The CLI must still yield `LocalDraft` in controlled mode.

## Smoke policy

- A real smoke call is optional and only happens if credentials already exist.
- If credentials are absent, the plan stops at `IMPLEMENTED_PENDING_REAL_SMOKE`.
- No smoke call may publish content or touch publishers.

## Smoke real

Preparar input sintético válido:

```bash
cat > /tmp/plan006_smoke_input.json <<'JSON'
{
  "id_entrada": "plan006_smoke_001",
  "tipo_entrada": "texto_manual",
  "texto_base": "La automatización útil reduce tareas repetitivas sin reemplazar el criterio humano.",
  "intencion_editorial": {
    "estado_intencion_editorial": "completa",
    "audiencia_objetivo": "Profesionales y equipos pequenos",
    "objetivo_del_post": "Crear un borrador breve con tono natural y una pregunta final concreta",
    "idea_central": "Automatizar lo repetitivo sin sustituir el criterio humano",
    "cta_intencionado": "¿Que tarea repetitiva automatizarias primero?"
  },
  "perfil_narrativo": {
    "id_perfil": "perfil_smoke_plan_006"
  },
  "canales_destino": ["linkedin"],
  "estado_privacidad": {
    "sanitizado": true
  },
  "restricciones": {}
}
JSON
```

Comando:

`LINKEDIN_CONTENT_AI_ADAPTER=litellm LINKEDIN_CONTENT_AI_PROVIDER=<proveedor> LINKEDIN_CONTENT_AI_MODEL=<modelo> LINKEDIN_CONTENT_AI_MAX_TOKENS=120 UV_CACHE_DIR=/tmp/uv-cache uv run python -m linkedin_content_system.cli.flujo_textual --input-json /tmp/plan006_smoke_input.json --output-dir /tmp/plan006-smoke-output --estado-aprobacion aprobado --revisor "Smoke Local" --fecha-aprobacion 2026-07-10T12:00:00Z`

Fixture:

```text
Idea central: La automatización útil reduce tareas repetitivas sin reemplazar el criterio humano.
Audiencia: profesionales y equipos pequeños.
Objetivo: crear un borrador breve de LinkedIn con tono natural y una pregunta final concreta.
```

Criterio PASS:

- respuesta no vacía;
- LocalDraft/evidencia creada;
- sin publicación;
- sin secretos en salida;
- una sola llamada;
- dentro del timeout.

Resultado:

- `PENDIENTE` en este entorno por ausencia de credenciales configuradas.

## Acceptance criteria

- A provider-backed adapter exists behind `ModelAdapter`.
- The default mode remains `ControlledModelAdapter`.
- `MockModelAdapter` still works for tests.
- The CLI still generates `LocalDraft`.
- Unknown adapter selection fails explicitly.
- The suite stays offline-safe.
- No publication code changes are required.

## STOP conditions

- The integration requires touching `publishers/`.
- The core must import a provider SDK directly.
- The provider requires hardcoded keys or versioned secrets.
- The only workable path removes the offline mode.
- The provider choice contradicts the ADR or current architecture.

## Files expected to change

- `plans/README.md`
- `plans/006-integracion-ia-real-controlada.md`
- `pyproject.toml`
- `uv.lock`
- `src/linkedin_content_system/ai/`
- `tests/ai/`
- `tests/cli/`
- `tests/use_cases/`
- `.env.example` only if it already exists or becomes strictly necessary
