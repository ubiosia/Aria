# /codigo/ — código real, sanitizado (y un core mínimo didáctico)

La mayoría de esta carpeta es código real de ARIA, tal como corre en producción, con solo los cambios mínimos necesarios para publicarlo: datos personales y rutas específicas de una máquina removidos o genéricos, sin alterar la lógica. La excepción es `aria_core_minimo.py`, marcado como tal en su propio encabezado — es código nuevo, escrito para este repositorio, no una copia del orquestador real (ver por qué en la sección de más abajo).

## Archivos

**Reales, sanitizados:**

- **`memoria.py`** — sistema de memoria personal de ARIA (backend SQLite con interfaz idéntica a la versión JSON original). Historia: [`/historia/05_memoria_y_conocimiento.md`](../historia/05_memoria_y_conocimiento.md), el bug del "dónde vivo" diagnosticado tres veces. También en [`/tecnico/bugs_famosos.md`](../tecnico/bugs_famosos.md), sección "El volcado de memoria personal".
- **`auditar_decision.py`** — comando de solo lectura que reconstruye, a partir de `aria_traces.db`, por qué ARIA respondió lo que respondió a una pregunta puntual. Mencionado en [`/historia/07_los_bugs_que_ensenaron_mas.md`](../historia/07_los_bugs_que_ensenaron_mas.md) como parte de la respuesta de fondo del proyecto a esa etapa de bugs.
- **`config_dominios.py`** — configuración centralizada de detección de dominio/enrutamiento, que reemplazó tres listas hardcodeadas desincronizadas. Es, en código, la corrección del bug protagonista de [`/historia/07_los_bugs_que_ensenaron_mas.md`](../historia/07_los_bugs_que_ensenaron_mas.md) (la lista de categorías hardcodeada).
- **`reconstruir_aria.sh`** — script de reconstrucción para levantar ARIA en una máquina nueva desde un backup. Relacionado con la disciplina de backup en tres capas descripta en [`/historia/11_epilogo.md`](../historia/11_epilogo.md) y en [`/tecnico/metodologia_de_trabajo.md`](../tecnico/metodologia_de_trabajo.md).
- **`agente_sistema.py`** y **`agente_noticias.py`** — dos agentes de dominio reales, tal como están escritos en producción. **No corren de forma aislada**: ambos heredan de `agente_base.AgenteBase`, que no está incluido en este repositorio (ver la sección "Por qué `aria_core.py` no está publicado" más abajo). Se publican como referencia de cómo está escrito un agente real, no como parte del core mínimo ejecutable.

**Nuevo, didáctico — Fase 3, Punto 2 ("core mínimo ejecutable"):**

- **`aria_core_minimo.py`** — versión mínima del orquestador, escrita para este repositorio, que sí corre de punta a punta: usa el `config_dominios.py` real de esta misma carpeta para rutear una pregunta, busca contexto en una colección local de ChromaDB, y le pasa el resultado a un modelo de Ollama. Con fallbacks claros si Ollama no está corriendo o la colección todavía no existe. Ver la explicación completa en el encabezado del archivo y la sección de abajo.

## Por qué `aria_core.py` no está publicado

El orquestador real (`aria_core.py`) importa alrededor de 30 módulos internos del proyecto: 15 agentes de dominio (`agente_trading.py`, `agente_ia.py`, `agente_programacion.py`, etc.), un registro de skills, working memory, recuperación de estado, y más. Publicarlo tal cual — sanitizado o no — rompería en el primer `import`, porque ninguno de esos módulos está ni va a estar en este repositorio. No cumpliría el objetivo de esta fase (que alguien clone el repo y vea algo corriendo), así que se optó por lo siguiente, evaluado y confirmado por Alejandro:

- `aria_core.py` real: **no se publica**.
- `agente_sistema.py` y `agente_noticias.py`: se publican como referencia real (ver arriba), rotulados como no ejecutables de forma aislada.
- `aria_core_minimo.py`: se escribe nuevo, genuinamente ejecutable, usando el patrón documentado en [`/tecnico/arquitectura.md`](../tecnico/arquitectura.md) (enrutar → RAG → LLM) y el código real ya publicado de `config_dominios.py`.

## Qué se sanitizó, archivo por archivo

**memoria.py**: se quitó "ana" (nombre real de un familiar) de la lista interna de términos de búsqueda usada para responder "quién es mi señora/esposa" — la búsqueda sigue funcionando igual por las palabras genéricas "señora"/"esposa". Se agregó el bloque de referencia cruzada al inicio. Sin ningún otro cambio: el resto del archivo, incluida la mención a "Alejandro" en dos lugares (docstring y una etiqueta de contexto para el LLM), se dejó igual — el nombre ya es público en el resto de este repositorio y no hay nada más sensible alrededor de esas menciones.

**auditar_decision.py**: sin cambios de contenido. Se agregó el bloque de referencia cruzada al inicio. El archivo no tenía ningún dato personal, ruta absoluta ni credencial — la ruta a la base de datos se resuelve vía un módulo interno (`aria_paths`) no incluido en este repositorio.

**config_dominios.py**: se reemplazaron ocho nombres reales de familiares de Alejandro (lista interna de palabras clave del dominio "personal", usada para que el enrutador reconozca menciones a la familia del usuario) por marcadores genéricos `[NOMBRE_FAMILIAR_N]`. Se agregó el bloque de referencia cruzada al inicio. El resto de las listas de palabras clave (trading, tecnología, IA, programación) son términos genéricos del dominio, no datos personales, y se dejaron sin cambios — incluyendo nombres de educadores de trading públicos (ver nota abajo).

**reconstruir_aria.sh**: sin cambios de contenido. Se agregó el bloque de referencia cruzada al inicio. El script no tenía ninguna ruta absoluta de una máquina específica (usa `$HOME` en todos los casos), ni credenciales, ni nombre de usuario/hostname — las rutas a backups y al archivo `.env` se piden de forma interactiva, nunca hardcodeadas.

**agente_sistema.py**: sin cambios de contenido. Se agregó el bloque de referencia explicando por qué no corre de forma aislada. Sin datos personales — la única coincidencia del escaneo es `127.0.0.1` (loopback, usado para verificar que `api_voz` responde en el propio diagnóstico), no una dirección de red real.

**agente_noticias.py**: sin cambios de contenido. Se agregó el mismo tipo de bloque de referencia. `BASE_DIR` se resuelve vía `Path.home()`, igual que en `memoria.py` — sin ruta absoluta hardcodeada.

**aria_core_minimo.py**: archivo nuevo (no sanitización — no hay original real detrás). Ver la sección "Verificación funcional" más abajo.

**Nota sobre `config_dominios.py`**: la lista de palabras clave de trading incluye varios apellidos ("villegas", "arango", "velez", "oliver velez") y un nombre de ciudad ("villahermosa") que parecen corresponder a educadores o referentes públicos de trading, en la misma línea que "sabri" (Sabri Conessa, ya acreditado en este repositorio). No se modificaron porque no hay evidencia de que sean datos personales de Alejandro o de su familia, pero quedan señalados acá para que se confirme en la revisión conjunta.

## Escaneo final de privacidad

Se corrió `scan_secrets.py` sobre los 4 archivos ya sanitizados, en conjunto, contra una carpeta de trabajo temporal (no sobre esta carpeta directamente). Resultado: sin credenciales, tokens, rutas absolutas de usuario, ni identificadores de máquina. Únicas coincidencias: menciones a "Alejandro" (2, en `memoria.py`, ya evaluadas como de bajo riesgo — nombre público en el resto del repositorio) y menciones a nombres de plataformas de trading ("binance", "bingx", en `config_dominios.py`, no son secretos). Sin resultados de la búsqueda dirigida de "alejandro_ia" (usuario WSL2) o "DESKTOP-PKP99MR" (hostname) en ninguno de los 4 archivos.

Este mismo escaneo se repitió sobre `agente_sistema.py`, `agente_noticias.py` y `aria_core_minimo.py` (Fase 3, Punto 2): única coincidencia, `127.0.0.1` en `agente_sistema.py` (loopback, no una dirección real).

## Verificación funcional de `aria_core_minimo.py`

No es solo "compila" — se corrió de punta a punta, con el `config_dominios.py` real:

- **Enrutamiento real**: "que es un order block" → `[dominio detectado: trading]`; "que es un arbol binario" → `[dominio detectado: programacion]`. Sin mocks — es el mismo `detectar_dominio()` que usa ARIA en producción.
- **Colección de ChromaDB inexistente**: mensaje claro (`todavía no existe la colección 'dataset_trading'...`) en vez de una excepción sin explicación.
- **Colección de ChromaDB vacía**: mensaje claro (`la colección '...' existe pero está vacía`).
- **Ollama no disponible**: `ollama.generate()` lanza `ConnectionError` real (confirmado en este entorno, que no tiene Ollama corriendo) — capturado y traducido a un mensaje que dice exactamente qué hacer (`ollama serve`, `ollama pull llama3.1:8b`).
- **Recuperación real de contexto (RAG)**: se creó una colección de ChromaDB local con documentos de prueba y una función de embedding determinística (el modelo de embeddings por defecto de ChromaDB necesita descargar un archivo ONNX la primera vez, y este entorno de verificación no tiene salida a internet — por eso se usó un embedding de prueba en vez del real, solo para confirmar que la lógica de recuperación de `aria_core_minimo.py` arma bien el contexto a partir de lo que devuelve `collection.query()`). En una instalación real, con salida a internet, ChromaDB descarga su modelo de embeddings por defecto la primera vez que se usa — comportamiento estándar de la librería, no algo específico de este archivo.

No se pudo probar una llamada real a Ollama (no hay un servidor Ollama corriendo en este entorno de verificación) — el camino de éxito de `preguntar_a_ollama()` no está probado end-to-end, solo su manejo de errores.

## `arrancar_aria.sh` / `arrancar_aria.bat` (Fase 3, Punto 3) y `requirements-core.txt`

Están en la raíz del repositorio, no en esta carpeta — arrancan todo el proyecto, no solo `/codigo/`. Se documentan acá porque están directamente ligados a `aria_core_minimo.py`.

**Por qué existe `requirements-core.txt` aparte de `requirements.txt`**: se probó instalar `requirements.txt` completo en un entorno limpio, sin los paquetes de sistema de `/tecnico/instalacion.md` sección 2 (en particular `portaudio19-dev`). `pip install` falló completo — no parcial — al intentar compilar `pyaudio` (`fatal error: portaudio.h: No such file or directory`), sin llegar a instalar `chromadb` ni `ollama`, aunque `aria_core_minimo.py` no usa audio para nada. `requirements-core.txt` tiene solo lo que ese archivo importa de verdad (`chromadb`, `ollama` — confirmado revisando sus imports, no de memoria); `arrancar_aria.sh`/`.bat` lo usan por defecto.

**Verificación real de `arrancar_aria.sh`**: se corrió, dos veces, en una copia aislada del repositorio simulando un clon nuevo (entorno sin `venv/`, sin `.env`, sin Ollama corriendo). Primera corrida (35 s): creó el `venv`, instaló `requirements-core.txt` sin bloquearse, avisó por la falta de `.env`, ruteó la pregunta con `config_dominios.py` real, y mostró los mensajes claros de ChromaDB/Ollama ya descritos arriba. Segunda corrida (0.6 s): no reinstaló dependencias — el archivo de marca (`venv/.requirements_core_instalados`) funcionó como se esperaba.

**No verificado**: `arrancar_aria.bat` — este entorno de verificación es Linux, sin Windows disponible para correrlo. Se escribió siguiendo la misma lógica que `arrancar_aria.sh`, pero no se puede confirmar que el bloque de carga de `.env` en batch (más frágil que su equivalente en bash) funcione igual en todos los casos — si falla al cargar alguna variable con comillas o espacios, revisar ese bloque a mano.

## Correcciones técnicas (revisión de Kimi, posteriores a la publicación inicial)

Después de la primera publicación, Kimi revisó los 4 archivos y señaló 8 puntos, aplicados todos:

- **`config_dominios.py`**: comentario de advertencia sobre los placeholders `[NOMBRE_FAMILIAR_N]` (sin reemplazarlos, esa parte del dominio "personal" queda inerte al clonar el repo). Se unificó `_normalizar_para_cache()` para que reutilice `normalizar()` en vez de reimplementar la misma lógica de tildes/minúsculas con un segundo `import unicodedata`.
- **`memoria.py`**: `buscar_dato()` ya no arma el tramo `LIKE` de la consulta con f-string (los valores siempre fueron parametrizados con `?`, pero se evita también depender de f-strings para la estructura). `importar()` ahora hace los `INSERT` dentro de una transacción (`with self._conn:`), para no dejar datos parciales si falla a mitad de camino. Se eliminó un segundo bloque de parsing de "olvida en X horas" en `procesar_mensaje()` que era redundante con el primero (alcanzable solo en un caso borde degenerado).
- **`auditar_decision.py`**: el import de `aria_paths` ahora tiene un fallback (mismo patrón que usa `memoria.py`) para que el script se pueda correr como ejemplo aislado, fuera del entorno completo de ARIA.
- **`reconstruir_aria.sh`**: notas de advertencia agregadas como comentarios — el Paso 6 (symlinks de CUDA) asume Python 3.12 y la estructura de paquetes NVIDIA de esa versión; el Paso 7 (restaurar backup) no tiene rollback y puede sobreescribir archivos existentes, incluido un `.env` ya copiado a mano.

Se verificó que los 3 archivos Python siguen compilando (`py_compile`) y que el script bash parsea sin errores (`bash -n`), y se corrió una prueba funcional de `memoria.py` (aprender, la búsqueda puntual "donde vivo", el bloque TTL restante, e `importar()` con la transacción nueva) sin cambios de comportamiento.

---

*Pendiente de confirmación de Alejandro y del consejo de IAs antes de subir estos archivos a git.*
