# Runbook benchmark editorial real

Ejecutar el benchmark real del Plan 007 con el flujo editorial vigente y sin
publicación.

```bash
WINDOWS_HOST_IP=$(ip route show | awk '/default/ {print $3; exit}')

export OLLAMA_API_BASE="http://${WINDOWS_HOST_IP}:11434"
export LINKEDIN_CONTENT_AI_ADAPTER="litellm"
export LINKEDIN_CONTENT_AI_PROVIDER="ollama"
export LINKEDIN_CONTENT_AI_MODEL="ollama_chat/llama3.2:latest"
export LINKEDIN_CONTENT_AI_TIMEOUT_SECONDS="240"
export LINKEDIN_CONTENT_AI_MAX_TOKENS="240"

UV_CACHE_DIR=/tmp/uv-cache \
uv run python -m linkedin_content_system.benchmark.editorial \
  --fixtures benchmarks/editorial/fixtures.json \
  --profiles-dir benchmarks/editorial/profiles \
  --feedback-json benchmarks/editorial/feedback_plan.json \
  --output-dir output/benchmark_real_<timestamp>
```

Criterios mínimos:

- 5 sesiones `editorial_*` completas;
- 2 ciclos `v1 -> feedback -> v2`;
- sin `LocalDraft`;
- sin publicación;
- evidencia con proveedor, modelo, hashes y estados;
- cualquier metatexto, invención experiencial no respaldada o cierre incompleto
  bloquea la pieza y hace fallar el lote.
