# Smoke real controlado

Estado: `PENDIENTE_DE_AUTORIZACION_Y_CREDENCIAL`.

Condiciones: instalar el extra `ai-real`, configurar localmente adapter,
proveedor, modelo y credencial estándar del proveedor, usar solo los fixtures
sintéticos y ejecutar una única pieza. No incluir claves en el comando.

```bash
LINKEDIN_CONTENT_AI_ADAPTER=litellm \
LINKEDIN_CONTENT_AI_PROVIDER=<proveedor> \
LINKEDIN_CONTENT_AI_MODEL=<modelo> \
LINKEDIN_CONTENT_AI_MAX_TOKENS=180 \
LINKEDIN_CONTENT_AI_TIMEOUT_SECONDS=30 \
uv run python -m linkedin_content_system.cli.flujo_textual \
  --input-json benchmarks/editorial/smoke_input.json \
  --output-dir output/smoke_real
```

Criterio PASS: una respuesta no vacía genera solo una sesión editorial
pendiente; no crea `LocalDraft`, no publica, no muestra secretos y termina
dentro del timeout. Conservar solo proveedor, modelo, duración, estado y ruta
relativa de evidencia.
