# 02 — Contrato de entrada de contenido

## 1. Propósito del documento

Este documento define la estructura mínima y el contrato de validación que debe cumplir cualquier entrada antes de ser procesada por el flujo de generación y publicación del sistema.

Su función es normalizar la entrada de datos (donde el archivo de audio es el flujo principal, y se proveen entradas auxiliares para pruebas) bajo un esquema único denominado **materia prima de contenido**.

---

## 2. Principio de normalización y privacidad

El flujo de procesamiento de entrada se rige bajo el siguiente esquema:

```text
entrada_original (Audio / Nota de voz)
↓
normalización + transcripción local (Faster-Whisper)
↓
sanitización de PII / revisión de privacidad (Gate local)
↓
materia_prima_contenido (Estructurada bajo contrato)
```

**Regla de privacidad obligatoria:** Toda nota de voz o transcripción debe auditarse localmente para evitar la fuga de información personal identificable (PII) o credenciales hacia proveedores externos (LLMs en la nube o adaptadores de publicación).

> [!IMPORTANT]
> El directorio de trazabilidad pública del flujo (`trace/`) bajo ninguna circunstancia debe guardar PII ni transcripciones en bruto. La transcripción bruta sólo puede existir como un artefacto local privado dentro de la carpeta del kit (`output/kit_<id>/private/raw_transcript.txt`) de forma restringida, o no guardarse.

---

## 3. Tipos de entrada admitidos en V1

| Tipo de entrada | Rol en V1 | Descripción |
| :--- | :--- | :--- |
| `audio` | **Flujo Principal** | Nota de voz o archivo de audio principal que se transcribe mediante Faster-Whisper local. |
| `texto_bruto` | **Auxiliar / Pruebas** | Modo de prueba o manual para validar flujos de redacción sin usar audio. |
| `borrador_existente` | **Auxiliar / Pruebas** | Modo de soporte para optimización de textos de LinkedIn ya escritos. |

---

## 4. Estructura común de entrada normalizada

El objeto normalizado que consume el orquestador (ADK) debe estructurarse bajo el siguiente formato conceptual:

```json
{
  "id_entrada": "in_lnk_001",
  "tipo_entrada": "audio",
  "fecha_creacion": "2026-07-03T11:15:00Z",
  "perfil_narrativo": "perfil_profesional_linkedin",
  "canales_destino": ["linkedin"],
  "intencion_editorial": {
    "estado_intencion_editorial": "completa",
    "audiencia_objetivo": "desarrolladores backend",
    "objetivo_del_post": "educar sobre Faster-Whisper",
    "pilar_contenido": "tecnología",
    "tipo_de_post": "educativo",
    "dolor_o_tension": "la latencia en la transcripción local",
    "idea_central": "Faster-Whisper optimiza la transcripción local de audio",
    "cta_intencionado": "sugerir guardar si resulta de valor",
    "nivel_de_promocion": "nulo"
  },
  "texto_base": "transcripción limpia del audio una vez sanitizada y revisada de PII",
  "metadatos_origen": {
    "ruta_archivo": "input/nota_voz_001.m4a",
    "nombre_archivo": "nota_voz_001.m4a",
    "idioma": "es",
    "duracion_segundos": 120
  },
  "estado_privacidad": {
    "sanitizado": true,
    "pii_detectada": false,
    "advertencias": []
  },
  "restricciones": {
    "no_inventar_datos": true,
    "requiere_aprobacion_humana": true
  }
}
```

---

## 5. Campos mínimos obligatorios

| Campo | Obligatorio | Descripción |
| :--- | :--- | :--- |
| `id_entrada` | Sí | Identificador único del lote de entrada. |
| `tipo_entrada` | Sí | Tipo de entrada (`audio`, `texto_bruto`, `borrador_existente`). |
| `perfil_narrativo` | Sí | Nombre del archivo o identificador del perfil narrativo del autor. |
| `canales_destino` | Sí | Debe contener únicamente `["linkedin"]` en V1. |
| `intencion_editorial`| Sí | Objeto de metadata editorial del sistema (obligatorio como bloque). Sus campos pueden venir completos o parciales. Debe incluir el campo `estado_intencion_editorial` (`completa \| parcial \| tentativa`). Si está marcado como `parcial` o `tentativa`, el sistema no inventará información y la futura skill `extraer-idea-central-linkedin` refinará el contenido usando solo input autorizado. |
| `texto_base` | Sí | Contenido textual normalizado y libre de PII listo para procesar. |
| `estado_privacidad`| Sí | Indicador del estado de revisión de privacidad y sanitización. |
| `restricciones` | Sí | Reglas y gates operativos del flujo. |

---

## 6. Reglas específicas para la entrada de Audio (Flujo Principal)

Para las entradas de tipo `audio`, se deben aplicar las siguientes directrices:
* **Transcripción Offline:** La transcripción se realizará mediante un adaptador local (Faster-Whisper) para garantizar la privacidad y reducir costes operativos.
* **Privacidad de la Traza:** La transcripción bruta que contenga posibles datos sensibles **no** se registrará en la traza pública (`trace/`). Solo se permite almacenar una referencia local privada restringida (`output/kit_<id>/private/raw_transcript.txt`) o descartar la versión sin sanitizar tras el filtrado.
* **Privacidad de Origen:** No se registrarán metadatos de audio que contengan información personal o rutas locales absolutas del sistema del usuario que puedan revelar secretos o PII.
* **Control de Errores:** Si el audio está corrupto o la transcripción falla, el flujo se detiene inmediatamente marcando un error en la traza y previniendo cualquier llamada externa.

---

## 7. Validaciones mínimas de entrada (Gate de Entrada)

Antes de avanzar a la etapa de generación y orquestación con ADK, el validador del sistema debe corroborar:
1. Existencia del archivo de audio físico si `tipo_entrada == "audio"`.
2. Validar que `canales_destino` contenga exclusivamente `linkedin`.
3. Confirmar que el `texto_base` no esté vacío y que `estado_privacidad.sanitizado` sea `true`.
4. El perfil narrativo especificado debe coincidir con un perfil local válido.
5. Validar que `intencion_editorial.nivel_de_promocion` contenga uno de los valores permitidos: `nulo | bajo | medio | alto`.
6. Regla de promoción: Si `nivel_de_promocion` es `alto`, el post debe marcarse en el diagnóstico final como `WARN` y requerir revisión humana reforzada antes de cualquier aprobación para publicación.
7. Validar el estado de la intención: Confirmar que `intencion_editorial` posee un `estado_intencion_editorial` válido. Si está marcada como `parcial` o `tentativa`, se autoriza a refinar pero se prohíbe inventar información. El gate de entrada bloqueará el flujo si no existe ningún insumo (audio, transcripción o texto bruto) suficiente para derivar la intención.

Si alguna de estas comprobaciones falla, el sistema detendrá el flujo inmediatamente.
