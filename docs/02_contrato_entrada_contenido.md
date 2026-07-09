# 02 — Contrato de entrada de contenido

## 1. Propósito del documento

Este documento define el contrato mínimo que debe cumplir cualquier entrada antes de ser procesada por el sistema.

Su función no es describir una única fuente concreta, sino establecer una forma común de normalizar materias primas distintas para que el resto del pipeline pueda operar con coherencia.

## 2. Principio rector

La identidad del sistema no depende de una entrada única.

La regla general es:

```text
fuente_original
-> normalización
-> sanitización / validación
-> materia_prima_contenido
```

La **materia prima de contenido** es el objeto normalizado que consume el pipeline editorial.

## 3. Tipos de entrada admitidos

El sistema debe poder admitir progresivamente distintas fuentes.

### 3.1 Tipos previstos por contrato

| Tipo de entrada | Rol | Descripción |
| :--- | :--- | :--- |
| `texto_manual` | Operativo inmediato | Texto escrito manualmente por el usuario para disparar el flujo útil inicial. |
| `audio` | Expansión prioritaria | Nota de voz o archivo de audio que requiere transcripción antes de normalizarse. |
| `transcripcion` | Soporte | Texto procedente de audio, video u otra fuente ya transcrita. |
| `borrador_existente` | Soporte | Pieza previa que se quiere mejorar, adaptar o reutilizar. |
| `documento_base` | Expansión futura | Documento, nota larga o material de referencia del que se extrae contenido. |

### 3.2 Restricción operativa actual

Aunque el contrato ya contempla múltiples tipos de entrada, el primer flujo útil vigente se valida con:

* `texto_manual` como entrada operativa inicial;
* LinkedIn como primer canal operativo;
* salida local antes de cualquier integración real externa.

## 4. Estructura común de entrada normalizada

Toda entrada, venga de donde venga, debe converger en una estructura conceptual como esta:

```json
{
  "id_entrada": "in_001",
  "tipo_entrada": "texto_manual",
  "fecha_creacion": "2026-07-08T10:30:00Z",
  "perfil_narrativo": "perfil_autor_principal",
  "canales_destino": ["linkedin"],
  "texto_base": "idea normalizada y lista para procesar",
  "intencion_editorial": {
    "estado_intencion_editorial": "parcial",
    "audiencia_objetivo": "fundadores B2B",
    "objetivo_del_post": "explicar una idea operativa",
    "pilar_contenido": "sistemas de contenido",
    "tipo_de_post": "educativo",
    "dolor_o_tension": "perder tiempo en flujos poco útiles",
    "idea_central": "primero hay que validar flujo útil, no solo control interno",
    "cta_intencionado": "invitar a reflexión",
    "nivel_de_promocion": "nulo"
  },
  "metadatos_origen": {
    "origen": "manual",
    "idioma": "es"
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

## 5. Campos mínimos obligatorios

| Campo | Obligatorio | Descripción |
| :--- | :--- | :--- |
| `id_entrada` | Sí | Identificador único de la entrada. |
| `tipo_entrada` | Sí | Tipo de fuente normalizada. |
| `perfil_narrativo` | Sí | Identificador del perfil editorial o narrativo que debe gobernar la salida. |
| `canales_destino` | Sí | Lista de canales para los que se quiere adaptar la pieza. Puede empezar con `linkedin` como primer canal operativo. |
| `texto_base` | Sí | Contenido textual ya utilizable por el pipeline editorial. |
| `intencion_editorial` | Sí | Bloque editorial del sistema. Puede estar completo, parcial o tentativo, pero debe declararse. |
| `estado_privacidad` | Sí | Estado de sanitización y riesgos de privacidad. |
| `restricciones` | Sí | Reglas operativas mínimas del flujo. |

## 6. Reglas por tipo de entrada

### 6.1 `texto_manual`

* No requiere transcripción.
* Debe poder activar el primer flujo útil del sistema.
* Es la entrada recomendada para validar producto antes de ampliar fuentes.

### 6.2 `audio`

* Requiere transcripción antes de entrar al pipeline editorial.
* La transcripción bruta no debe tratarse como salida pública ni evidencia abierta.
* Debe existir control de privacidad antes de enviar esa transcripción a cualquier etapa posterior.

### 6.3 `transcripcion`

* Puede proceder de audio, video o sistema externo.
* Debe considerarse equivalente a una fuente intermedia, no necesariamente a una entrada final segura.
* También debe pasar control de privacidad y normalización.

### 6.4 `borrador_existente` y `documento_base`

* Se aceptan como materia prima de reutilización o adaptación.
* No autorizan inventar contexto, experiencia ni intención no presentes en la fuente.

## 7. Reglas de privacidad y seguridad

1. Ninguna entrada puede avanzar si contiene PII o secretos sin tratar.
2. La materia prima normalizada debe ser apta para pasar al pipeline sin exponer datos sensibles.
3. No deben registrarse rutas locales absolutas, tokens ni credenciales en metadatos o evidencias.
4. Si una fuente no puede normalizarse de forma segura, el flujo debe detenerse.

## 8. Reglas de intención editorial

El bloque `intencion_editorial` es obligatorio como estructura, aunque sus campos no siempre lleguen completos.

Estados admitidos:

* `completa`
* `parcial`
* `tentativa`

Reglas:

* si está `completa`, el sistema debe respetarla;
* si está `parcial`, el sistema puede refinarla sin inventar;
* si está `tentativa`, el sistema puede ordenar y aclarar, pero no fabricar hechos, autoridad ni enfoque no soportado.

## 9. Validaciones mínimas de entrada

Antes de pasar a generación o adaptación, el sistema debe verificar:

1. `id_entrada` válido y no vacío;
2. `tipo_entrada` reconocido;
3. `texto_base` presente o fuente suficiente para derivarlo;
4. `estado_privacidad.sanitizado == true`;
5. `perfil_narrativo` informado;
6. `intencion_editorial.estado_intencion_editorial` válido;
7. `canales_destino` informado;
8. `nivel_de_promocion` dentro de valores permitidos si se declara.

Si falla cualquiera de estas comprobaciones, la entrada no debe avanzar.

## 10. Relación con el estado actual del código

Este contrato ya refleja la dirección deseada del producto.

Eso no implica que todo el código actual soporte todavía:

* todos los tipos de entrada;
* múltiples canales operativos;
* transcripción real integrada;
* publicación real.

Esas capacidades se habilitarán por fases posteriores.

La regla de trabajo sigue siendo:

```text
primero ajustar contrato
después ajustar salidas y decisiones técnicas
después tocar código
```
