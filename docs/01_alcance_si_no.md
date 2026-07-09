# 01 — Alcance SÍ/NO

## 1. Propósito del documento

Este documento define el alcance del nuevo MVP útil del sistema.

Su función es evitar dos errores:

* seguir construyendo alrededor de una visión antigua;
* abrir demasiado pronto un sistema que todavía no consolidó su primer flujo valioso.

## 2. Qué sí entra en el MVP actual

| Elemento | Detalle e implicación |
| :--- | :--- |
| **Entrada manual en texto** | Es la primera forma de entrada operativa para acelerar validación de producto. |
| **Arquitectura preparada para múltiples fuentes** | El sistema debe poder crecer a audio, transcripciones, documentos o vídeo, aunque no todas entren a la vez. |
| **LinkedIn como canal inicial probable** | Es una opción práctica para validar utilidad, pero no una obligación rígida si otra red resulta mejor para empezar. |
| **Generación de borrador útil** | El sistema debe producir una pieza que una persona realmente quiera revisar o usar. |
| **Perfil narrativo / voz** | La salida debe respetar voz, reglas y límites editoriales. |
| **Validación mínima real** | Debe existir control de PII, seguridad, trazabilidad y calidad editorial suficiente. |
| **Aprobación humana usable** | La aprobación no puede ser solo un dato de contrato; debe existir como interacción operativa. |
| **Salida local lista** | El primer éxito real es un borrador local útil y persistible. |
| **Adaptadores desacoplados** | Las integraciones futuras deben entrar por puertos y adaptadores, no por acoplamiento al núcleo. |
| **Preparación de publicación futura** | El sistema debe poder llegar a `dry_run` de publicación cuando el flujo local ya sea útil. |

## 3. Qué no entra todavía

| Elemento | Motivo / destino |
| :--- | :--- |
| **Omnicanal simultáneo** | El sistema es portable, pero no conviene intentar varios canales reales a la vez en el primer corte. |
| **Publicación real sin aprobación humana** | Rompe el criterio de seguridad y control editorial. |
| **Automatización de engagement** | Likes, comentarios, DMs, scraping o growth hacking quedan fuera. |
| **Visuales como requisito del primer éxito** | Carruseles, imágenes o video son importantes, pero no deben bloquear el flujo textual útil. |
| **Analítica avanzada** | El feedback posterior llegará después del primer flujo operativo. |
| **UI completa** | Puede llegar más adelante; no es requisito para validar el valor del sistema. |
| **Multiusuario / multi-cliente operacional** | No es prioridad hasta que el flujo principal esté probado. |
| **Dependencia obligatoria de un entorno de agentes** | El sistema debe poder sostenerse como software normal. |

## 4. Reglas de alcance

1. **LinkedIn como arranque probable, no obligatorio ni único:** el MVP puede comenzar con LinkedIn por practicidad, pero si otra red permite validar antes el producto, también puede priorizarse.
2. **Texto primero, no único:** el primer flujo útil arranca por texto, pero el producto debe poder crecer a otras fuentes.
3. **Primero valor, luego sofisticación:** si una capacidad no mejora el primer flujo útil, no entra aún.
4. **No bloquear con documentación antigua:** ningún documento histórico debe restringir el nuevo alcance si contradice esta definición.
5. **Seguridad intacta:** mover el alcance no autoriza usar PII, secretos, publicación real ni integraciones externas sin control.

## 5. Secuencia de ampliación prevista

Una vez validado el MVP útil, el orden previsto de crecimiento es:

1. entrada textual útil;
2. aprobación humana usable;
3. salida local lista;
4. audio y transcripción;
5. preparación de publicación en `dry_run`;
6. publicación real controlada;
7. visuales;
8. analítica y retroalimentación;
9. nuevos canales.
