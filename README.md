# Portable Content Publisher

Base local y segura para transformar contenido en borradores publicables sin publicar nada real.

## Estado actual

- Flujo textual offline desde `texto_manual`.
- `ControlledModelAdapter` como modo por defecto.
- `MockModelAdapter` para pruebas deterministas.
- `LiteLLMModelAdapter` opcional detrás de `ModelAdapter`.
- Persistencia local en `LocalDraft` y evidencia `ExternalDryRun`.

## Arranque rápido

```bash
uv run python -m pytest -q
uv run python -m linkedin_content_system.cli.flujo_textual --help
```

## Ciclo textual local

Generar y revisar no requiere aprobación anticipada:

```bash
uv run python -m linkedin_content_system.cli.flujo_textual \
  --texto "Automatizar lo repetitivo deja más tiempo para aplicar criterio humano." \
  --id-entrada ejemplo_001 --output-dir output

uv run python -m linkedin_content_system.cli.flujo_textual \
  --accion ajustar --id-entrada ejemplo_001 \
  --feedback "Haz el inicio más directo." --output-dir output

uv run python -m linkedin_content_system.cli.flujo_textual \
  --accion aprobar --id-entrada ejemplo_001 --version 2 \
  --revisor "Revisión local" --output-dir output

uv run python -m linkedin_content_system.cli.flujo_textual \
  --accion preparar --id-entrada ejemplo_001 --output-dir output
```

Cada generación queda en `editorial_<id>/` con historial de versiones. Solo
una versión aprobada puede convertirse en `LocalDraft`. `--input-json` sigue
disponible para entradas estructuradas.

## Benchmark editorial local

```bash
uv run python -m linkedin_content_system.benchmark.editorial \
  --output-dir output/benchmark_editorial
```

Los cinco fixtures y dos perfiles de `benchmarks/editorial/` son sintéticos.
La ejecución técnica no sustituye la revisión humana definida en `rubrica.md`.
El smoke con proveedor real queda pendiente de autorización y credencial local.

## Configuración útil

- `LINKEDIN_CONTENT_AI_ADAPTER=controlled|mock|litellm`
- `LINKEDIN_CONTENT_AI_PROVIDER=<proveedor>`
- `LINKEDIN_CONTENT_AI_MODEL=<modelo>`
- `LINKEDIN_CONTENT_AI_API_BASE=<url-http-o-https-opcional>`
- `OLLAMA_API_BASE=http://<WINDOWS_HOST_IP>:11434`
- `LINKEDIN_CONTENT_AI_TIMEOUT_SECONDS=30`
- `LINKEDIN_CONTENT_AI_MAX_TOKENS=280`
- `LINKEDIN_CONTENT_PROFILE_DIR=./profiles`

## Dependencia opcional para IA real

El modo `litellm` no es obligatorio para usar el proyecto. Si se quiere activar la ruta real:

```bash
uv sync --extra ai-real
```

Las credenciales deben venir del entorno estándar del proveedor elegido y nunca se versionan en este repositorio.

Para Ollama en Windows accesible desde WSL, una configuración local típica es:

```bash
WINDOWS_HOST_IP=$(ip route show | awk '/default/ {print $3; exit}')
export OLLAMA_API_BASE="http://${WINDOWS_HOST_IP}:11434"
export LINKEDIN_CONTENT_AI_ADAPTER=litellm
export LINKEDIN_CONTENT_AI_PROVIDER=ollama
export LINKEDIN_CONTENT_AI_MODEL=ollama_chat/llama3.2:latest
```
