# Smoke real controlado

Estado: `PENDIENTE_DE_AUTORIZACION_Y_CREDENCIAL`.

Condiciones: instalar el extra `ai-real`, configurar localmente adapter,
proveedor, modelo, `OLLAMA_API_BASE` y la credencial estándar del proveedor
si aplica, usar solo los fixtures sintéticos y ejecutar una única pieza. No
incluir claves en el comando.

```bash
WINDOWS_HOST_IP=$(ip route show | awk '/default/ {print $3; exit}')
export OLLAMA_API_BASE="http://${WINDOWS_HOST_IP}:11434"
LINKEDIN_CONTENT_AI_ADAPTER=litellm \
LINKEDIN_CONTENT_AI_PROVIDER=ollama \
LINKEDIN_CONTENT_AI_MODEL=ollama_chat/llama3.2:latest \
LINKEDIN_CONTENT_AI_MAX_TOKENS=180 \
LINKEDIN_CONTENT_AI_TIMEOUT_SECONDS=120 \
LINKEDIN_CONTENT_PROFILE_DIR=benchmarks/editorial/profiles \
uv run --extra ai-real python -m linkedin_content_system.cli.flujo_textual \
  --input-json benchmarks/editorial/smoke_input.json \
  --output-dir output/smoke_real
```

Criterio PASS: una respuesta no vacía, completa y sin metatexto genera solo una
sesión editorial pendiente; no crea `LocalDraft`, no publica, no muestra
secretos y termina dentro del timeout. `sesion.json` debe conservar evidencia
saneada del adapter, proveedor, modelo, timeout, límite de tokens, duración,
commit, hashes de fixture, perfil y salida, estado técnico, estado estructural,
estado editorial y ausencia de publicación y `LocalDraft`. El smoke no cuenta
como benchmark ni activa feedback.
