# Decisiones de arquitectura

Este documento reúne las decisiones de diseño que marcaron el rumbo del proyecto, con el razonamiento real detrás de cada una — no una lista de opciones técnicas abstractas, sino lo que efectivamente se decidió y por qué, incluyendo los casos en que la decisión fue pragmática antes que ideal.

Cada decisión mayor está reformateada como ADR (Architecture Decision Record): Contexto, Decisión, Alternativas consideradas (cuando las hubo, documentadas) y Consecuencias. El contenido es el mismo que ya tenía este documento — solo cambió la forma, para que sea más fácil de escanear y de referenciar desde otras partes del repositorio.

---

## ADR-001 — WSL2 en vez de Ubuntu nativo

**Estado:** Aceptada (con revisión formal posterior, confirmada).

**Contexto:** al arrancar el proyecto se asumía que la máquina tenía Ubuntu en dual-boot. Al verificar el entorno real con `wsl --list --verbose`, apareció que en realidad era WSL2 — Ubuntu corriendo dentro de Windows, no una instalación nativa aparte. De esa confusión quedó una lección anotada explícitamente: antes de instalar nada, verificar el entorno real con comandos de diagnóstico, nunca asumir.

**Decisión:** quedarse con WSL2, no migrar a una instalación nativa en dual-boot.

**Alternativas consideradas:**
- **Ubuntu nativo (dual-boot):** rinde mejor con la GPU, aproximadamente un 10% más rápido, pero exige arrancar directamente en Linux cada vez (sin poder usar Windows en simultáneo).
- **WSL2 (elegida):** más cómodo para el uso diario, porque Ubuntu corre sin reiniciar la máquina ni perder acceso a Windows.

La decisión inicial fue quedarse con WSL2 por comodidad, dejando la migración a una instalación nativa como una mejora futura — no como una tarea pendiente urgente. Esa mejora futura se evaluó formalmente más adelante, unas semanas después de la instalación inicial (Sesión 33), y la conclusión fue no migrar: mover meses de trabajo y de datos ya indexados a una configuración nueva representaba un riesgo concreto de pérdida, frente a una ganancia de rendimiento que no era crítica para el uso real del sistema.

**Consecuencias:** la decisión se marcó como definitiva ("decisión definitiva, no se revisa"), sin plan de reabrirla salvo que apareciera una razón nueva y de peso. En el material disponible no queda registro de que la idea haya vuelto a plantearse formalmente después de esa fecha. Como contrapartida documentada, WSL2 trajo problemas propios que no habría tenido una instalación nativa — por ejemplo, el límite de memoria de WSL2 (~50% de la RAM física por defecto) causó cuelgues reales de producción meses después (Sesión 86), resueltos con un archivo `.wslconfig` explícito.

---

## ADR-002 — Separar ARIA y SabriBot en entornos distintos

**Estado:** Aceptada; extendida más adelante a un plan de separación física (no ejecutado al cierre del material disponible).

**Contexto:** ARIA y un proyecto de trading automatizado distinto —hoy conocido como SabriBot— convivieron desde etapas tempranas en la misma máquina, en carpetas y entornos completamente separados por regla explícita. Esa separación no fue una formalidad de entrada: se reforzó a partir de un incidente real, temprano en el proyecto, donde el trabajo terminó aplicándose por error sobre la terminal del sistema equivocado durante varios minutos, sin que nada avisara del error hasta que las respuestas dejaron de tener sentido.

**Decisión:** ARIA y SabriBot son y siguen siendo dos proyectos separados — sin mezclar capacidades, código ni entornos de ejecución.

**Consecuencias:** el razonamiento documentado para mantener (y más adelante profundizar) la separación es doble. Por un lado, ARIA es un asistente generalista —memoria personal, biblioteca de conocimiento, trading solo como una de varias funciones— mientras que SabriBot es, específicamente, un sistema de trading real; mezclar ambos multiplica el riesgo de que un error en uno afecte al otro, algo particularmente delicado cuando uno de los dos maneja decisiones de mercado reales. Por otro lado, separar físicamente permite que cada sistema se optimice para lo que realmente necesita, sin compartir recursos de hardware entre un asistente de uso diario y un sistema con expectativas de disponibilidad distintas.

Con el tiempo, esa separación lógica pasó a plantearse también como separación física: usar la máquina secundaria ("Pruebas") como el nuevo servidor de trabajo diario de ARIA, y transformar la máquina principal actual en la máquina dedicada a SabriBot. El propio plan establece terminar primero los pendientes reales de ARIA en curso —empezando por el Módulo 9 de autonomía (ver ADR-003)— antes de ejecutar esa migración. Sigue sin ejecutarse al cierre del material disponible.

---

## ADR-003 — Autonomía acotada, sumada en fases verificables (Módulo 9)

**Estado:** Aceptada; en ejecución progresiva (Fase 3 en período de prueba al cierre del material disponible).

**Contexto:** dar a ARIA capacidades de autonomía (leer carpetas, encadenar tareas, buscar en la web) implica un riesgo real si se hace de golpe y sin verificación — tanto de errores técnicos como de acciones no deseadas sobre datos o cuentas reales.

**Decisión:** ordenar el crecimiento de autonomía en fases numeradas (0 a 4), cada una construida sobre la anterior y dada por completa y estable en producción antes de habilitar la siguiente. Las primeras fases (0, 1 y 2) llevan tiempo en producción sin cambios. La Fase 3 —búsqueda web acotada— no le da a ARIA acceso libre a internet: cada caso de uso es un Handler específico, contra una API puntual y una lista explícita de dominios permitidos (`dominios_permitidos.json`) — tipo de cambio de moneda, precio de la plata, un índice de sentimiento de mercado. Cada caso nuevo pasa, además, por un período de prueba real antes de considerarse estable (dos semanas de uso sin incidentes de contenido no confiable, como mínimo, antes de sumar el siguiente caso).

**Alternativas consideradas y descartadas explícitamente**, documentadas junto con esta decisión:
- **"Modo Jefe"** (agentes autónomos tipo Plan-and-Execute, para planificar y ejecutar tareas por su cuenta sin supervisión directa): no llegó a construirse.
- **Webhooks públicos**: descartados — habrían ampliado la superficie de exposición del sistema sin una necesidad real que lo justificara.
- **Arranque automático del sistema al iniciar Windows**: descartado, por la misma razón.
- **Ejecución de operaciones de trading real desde ARIA**: descartada como límite de diseño, no como pendiente técnico — cualquier decisión de mercado la toma Alejandro Ubios, nunca el sistema, bajo ninguna circunstancia.

**Consecuencias:** el criterio de fondo, repetido en distintas decisiones a lo largo del proyecto, es el mismo: sumar autonomía de a un paso verificable por vez, con evidencia real de que cada paso funciona antes de dar el siguiente, en vez de construir capacidades amplias de entrada y confiar en que se comporten bien. Como costo, esto implica un desarrollo más lento de nuevas capacidades de autonomía — cada caso de uso nuevo de la Fase 3 pasa, como mínimo, por dos semanas de prueba antes de sumarse formalmente.

---

## ADR-004 — Descartar el fine-tuning (LoRA) como camino para agregar conocimiento

**Estado:** Aceptada (decisión de cierre; no se retoma sin razón nueva).

**Contexto:** durante el proyecto se evaluó si entrenar un adaptador LoRA (fine-tuning eficiente sobre el modelo local) era un camino viable para que ARIA "supiera más" sobre trading y los libros indexados. No fue una decisión tomada sin probar: se entrenó y completó un primer adaptador LoRA real de punta a punta —

> "Entrenamiento LoRA sobre Llama 3.1 8B (4-bit, vía unsloth): configuración conservadora (r=16, 2 épocas, batch efectivo de 8) pensada para validar el pipeline, no para maximizar calidad. Resultado: 50 pasos completados en aproximadamente 11 minutos, loss final de entrenamiento 1.61, adapter LoRA de 167 MB guardado en lora_trading_ia_v1/." (Sesión 68)

— y se dejó pendiente evaluar su calidad real contra el modelo base antes de decidir sobre un entrenamiento más largo (validación de esa evaluación en la Sesión 69).

**Decisión:** semanas después (Sesiones 103-104), se descartó el fine-tuning local como estrategia general para agregar conocimiento nuevo:

> "Fine-tuning local de ARIA con LoRA/Unsloth — evaluado tras ver un video sobre el tema; se descartó porque el objetivo real (que ARIA sepa más de trading/libros) ya está cubierto por el RAG existente, y todas las fuentes consultadas coinciden en que el fine-tuning es la herramienta equivocada para agregar conocimiento." (Sesión 103-104)

**Alternativas consideradas:**
- **Fine-tuning (LoRA/Unsloth)** — probado y funcional técnicamente, pero identificado como la herramienta equivocada para el objetivo real (agregar conocimiento nuevo, no ajustar tono o estilo).
- **RAG (ya existente)** — elegido como el mecanismo correcto para ese objetivo: agregar un libro o documento nuevo al vectorstore es más simple, más verificable y no requiere reentrenar nada.

**Consecuencias:** el pipeline de entrenamiento LoRA quedó documentado y probado (funciona), pero no se usa como estrategia activa del proyecto. La ampliación de la biblioteca de conocimiento del sistema sigue el camino del RAG (`ingesta.py` + ChromaDB) exclusivamente. No hay, en el material disponible, evidencia de que esta decisión se haya revisado después de las Sesiones 103-104.

---

## ADR-005 — ChromaDB como base de datos vectorial

**Estado:** Aceptada por defecto desde el inicio; sin revisión formal documentada.

**Contexto:** el proyecto necesitaba una base de datos vectorial para sostener el RAG (búsqueda semántica sobre documentos indexados) desde la primera sesión.

**Decisión:** usar ChromaDB. Es la base vectorial del proyecto desde la instalación inicial (Sesión 1, con el RAG funcionando sobre 76 chunks) y se mantiene como tal hasta el cierre del material disponible, con más de medio millón de chunks indexados.

**Alternativas consideradas:** **ninguna con respaldo documental.** A diferencia de otras decisiones de este documento (WSL2, LoRA), no encontré en el material disponible una comparación real entre ChromaDB y alguna alternativa (por ejemplo Qdrant, FAISS, Pinecone o Weaviate) — ni una sesión que explique por qué se eligió ChromaDB en particular sobre otra opción. Todo indica que fue la elección inicial de instalación, adoptada junto con el resto de la pila (Ollama, `nomic-embed-text`, `langchain-chroma`) y nunca reconsiderada, en vez de resultado de una evaluación comparativa. Esta ADR lo señala así, en vez de inventar un razonamiento retroactivo que no está respaldado por ninguna fuente.

**Consecuencias:** ChromaDB pasó por más de un incidente real de mantenimiento a lo largo del proyecto (una corrupción del índice que requirió reconstrucción completa en la Sesión 110, y episodios de duplicación masiva de chunks en las Sesiones 108-112 y 119) — ver [`/tecnico/arquitectura.md`](arquitectura.md), sección "Vectorstore y embeddings, en profundidad", para el detalle completo. Ninguno de esos incidentes llevó a reconsiderar la elección de ChromaDB en sí; se trataron como problemas de mantenimiento y de código propio (`ingesta.py`), no como una razón para migrar de base vectorial.

---

*Nota editorial: el contenido de los ADR-001 y ADR-002 es el mismo que ya tenía este documento antes de esta reestructuración (WSL2 y separación ARIA/SabriBot), solo reformateado — sus fuentes ya estaban verificadas con cita textual en la versión anterior: la decisión de WSL2 está documentada con cita textual completa, incluyendo la confusión inicial sobre el dual-boot; la separación ARIA/SabriBot combina un hecho documentado temprano (el incidente de la terminal equivocada, narrado en `/historia/02_los_primeros_tropiezos.md`) con el plan de arquitectura de largo plazo documentado en la Sesión 121, todavía sin ejecutar. El ADR-003 (límites de autonomía) también reformatea contenido ya existente, tomado de los manuales de sesión de agosto de 2026 y coincidente con la lista de "descartado explícitamente" de `/meta/estado_actual.md`. El ADR-004 (LoRA) es contenido nuevo en este documento —ya estaba resumido en `/meta/estado_actual.md` y `/meta/linea_de_tiempo.md`, pero no como ADR ni con esta cita textual completa de las Sesiones 68 y 103-104—, agregado ahora con sus citas primarias. El ADR-005 (ChromaDB) es enteramente nuevo: se verificó explícitamente, antes de escribirlo, si existía una comparación documentada con alguna alternativa — no la hay— y el documento lo declara así en vez de inventar una justificación retroactiva.*
