# ADR-000: Decisiones Técnicas Base (V1)

Este documento registra las decisiones tecnológicas y de diseño fundamentales para el **Publicador automático desde audio para LinkedIn** (V1).

---

## Matriz de Decisiones Técnicas

| Decisión | Estado | Motivo | Alternativas descartadas por ahora | Riesgo | Cuándo reevaluar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Python como base** | Aceptado | Ecosistema nativo para IA, Faster-Whisper y Google ADK. | Node.js, Go. | Mayor consumo de recursos que lenguajes compilados. | Si la portabilidad en plataformas sin Python es crítica. |
| **2. Google ADK inicial** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Orquestación estructurada de agentes y sesiones de desarrollo. | LangChain, desarrollo propio desde cero. | Acoplamiento inicial a las convenciones del framework. | Al finalizar la Fase 1C si se detecta sobrecarga técnica. |
| **3. Faster-Whisper local** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Transcripción local offline barata y con alta privacidad. | OpenAI Whisper API (nube). | Requisitos de hardware local (CPU/GPU) mínimos. | Si se requiere transcribir audios de más de 30 minutos de forma masiva. |
| **4. Pydantic para contratos**| Aceptado | Validación estricta y tipado estático en entradas/salidas. | Diccionarios JSON nativos. | Rigidez inicial si los contratos cambian frecuentemente. | Al inicio de la fase de código de los validadores. |
| **5. LinkedIn en V1** | Aceptado | Enfoque de canal único para validar la publicación automática. | X/Twitter, Instagram. | Alcance limitado en la primera entrega. | Al consolidar la Fase 1C y entrar a planeación de V2. |
| **6. Metricool como adaptador** | Aceptado | Evita el desarrollo propio de OAuth y apoya multi-cuenta. | API Directa de LinkedIn, Buffer. | Cambios de tarifas o de API de la plataforma Metricool. | Si se requiere control total del flujo OAuth en V2. |
| **7. LocalDraftPublisher** | Aceptado | Base offline de testing que simula la publicación local. | Mocks en código de testing sin persistencia en disco. | Ninguno relevante. | Al iniciar la fase de pruebas de integración. |
| **8. Puertos y adaptadores** | Aceptado | Protege el núcleo del negocio frente a dependencias externas. | Arquitectura monolítica clásica. | Mayor nivel de abstracción inicial. | Al planificar la Fase 2 (expansión omnicanal). |
| **9. JSON/Markdown local** | Aceptado | Evidencias legibles en local sin dependencias de base de datos. | SQLite, PostgreSQL. | Gestión manual de archivos y potencial fragmentación. | Si el sistema evoluciona a multiusuario o panel web (V2). |
| **10. Sanitización de PII** | Aceptado | Garantiza que no se envíen datos personales a LLMs externos. | Enviar transcripción en bruto. | Filtros muy restrictivos que eliminen contexto del audio. | En la Fase 1.5 (Robustez y pruebas). |
| **11. Modo dry_run** | Aceptado | Simulación del adaptador Metricool sin publicar contenido real. | Publicación en producción directa. | Falsos positivos de conectividad. | Al iniciar el testing de integración con Metricool. |
| **12. Exclusión de V2 en V1** | Aceptado | Acotar el desarrollo de carruseles, imágenes, UI y X a V2. | Implementación total omnicanal. | Pérdida de interés funcional en la V1 omnicanal. | Tras estabilizar el flujo real de LinkedIn (Fase 1C). |
| **13. LiteLLM como adaptador** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Evita la dependencia rígida de un proveedor de LLM específico. | SDK de Vertex / OpenAI directo en dominio. | Dependencia de una librería adicional de abstracción. | Si se estandariza el uso de un único LLM local/nube corporativo. |
| **14. ADK Artifacts** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Almacenamiento idóneo para audios, transcripciones y archivos pesados. | Almacenar binarios en base de datos. | Gestión local de archivos pesados. | Si la escalabilidad en la nube requiere almacenamiento de objetos distribuido. |
| **15. Session State ligero** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Almacenamiento en memoria para estados efímeros y referencias locales. | Persistencia en base de datos para cada paso de ejecución. | Pérdida de estado ante reinicios del proceso. | Al escalar a arquitectura multiusuario en V2. |
| **16. Callbacks para trazas** | CANDIDATA / EVALUABLE (NO OBLIGATORIA EN V1 LOCAL) | Provee desacoplamiento total en el sistema de logs y trazabilidad. | Escritura directa de logs dentro de la lógica del dominio. | Complejidad inicial de suscripción a eventos. | Si el rendimiento se ve afectado por alto volumen de eventos. |

---

## Reglas de Arquitectura

1. **Principio de Aislamiento:** El núcleo (dominio) no conoce a los adaptadores. Metricool y Faster-Whisper deberán consumir los contratos definidos en [02_contrato_entrada_contenido.md](../02_contrato_entrada_contenido.md) y [04_contrato_salida.md](../04_contrato_salida.md); cuando exista código, esos contratos se implementarán mediante interfaces internas.
2. **Seguridad Absoluta:** Ningún token, API Key de LLM o PII de audio bruta debe registrarse en la carpeta de trazas públicas (`trace/`).
3. **Fuente de Verdad:** Este repositorio rige el comportamiento técnico del sistema. Toda desviación de este ADR debe proponerse en un nuevo archivo incremental (`ADR-001_...`).

---

## Puertos Mínimos del Dominio

Para aislar el núcleo de implementaciones concretas, el dominio interactuará a través de los siguientes puertos mínimos:
*   **Puerto_Modelo:** adaptador de modelo evaluable; LiteLLM puede ser candidato.
*   **Puerto_Publicacion:** Interfaz de programación y publicación (ej. LocalDraftPublisher, Metricool).
*   **Puerto_Transcripcion:** adaptador de transcripción local o externo; Faster-Whisper puede ser candidato.
*   **Puerto_Almacenamiento:** almacenamiento local primero; ADK Artifacts puede evaluarse después.
*   **Puerto_Revision:** Interfaz para validación automática del post.
*   **Puerto_Aprobacion:** Interfaz del gate de aprobación humana.
