# /codigo/ — código real, sanitizado

Esta carpeta contiene código real de ARIA, tal como corre en producción, con solo los cambios mínimos necesarios para publicarlo: datos personales y rutas específicas de una máquina removidos o genéricos, sin alterar la lógica. No son fragmentos de ejemplo ni reconstrucciones — son los archivos reales (ver el resumen de cambios más abajo, archivo por archivo).

## Archivos

- **`memoria.py`** — sistema de memoria personal de ARIA (backend SQLite con interfaz idéntica a la versión JSON original). Historia: [`/historia/05_memoria_y_conocimiento.md`](../historia/05_memoria_y_conocimiento.md), el bug del "dónde vivo" diagnosticado tres veces. También en [`/tecnico/bugs_famosos.md`](../tecnico/bugs_famosos.md), sección "El volcado de memoria personal".
- **`auditar_decision.py`** — comando de solo lectura que reconstruye, a partir de `aria_traces.db`, por qué ARIA respondió lo que respondió a una pregunta puntual. Mencionado en [`/historia/07_los_bugs_que_ensenaron_mas.md`](../historia/07_los_bugs_que_ensenaron_mas.md) como parte de la respuesta de fondo del proyecto a esa etapa de bugs.
- **`config_dominios.py`** — configuración centralizada de detección de dominio/enrutamiento, que reemplazó tres listas hardcodeadas desincronizadas. Es, en código, la corrección del bug protagonista de [`/historia/07_los_bugs_que_ensenaron_mas.md`](../historia/07_los_bugs_que_ensenaron_mas.md) (la lista de categorías hardcodeada).
- **`reconstruir_aria.sh`** — script de reconstrucción para levantar ARIA en una máquina nueva desde un backup. Relacionado con la disciplina de backup en tres capas descripta en [`/historia/11_epilogo.md`](../historia/11_epilogo.md) y en [`/tecnico/metodologia_de_trabajo.md`](../tecnico/metodologia_de_trabajo.md).

## Qué se sanitizó, archivo por archivo

**memoria.py**: se quitó "ana" (nombre real de un familiar) de la lista interna de términos de búsqueda usada para responder "quién es mi señora/esposa" — la búsqueda sigue funcionando igual por las palabras genéricas "señora"/"esposa". Se agregó el bloque de referencia cruzada al inicio. Sin ningún otro cambio: el resto del archivo, incluida la mención a "Alejandro" en dos lugares (docstring y una etiqueta de contexto para el LLM), se dejó igual — el nombre ya es público en el resto de este repositorio y no hay nada más sensible alrededor de esas menciones.

**auditar_decision.py**: sin cambios de contenido. Se agregó el bloque de referencia cruzada al inicio. El archivo no tenía ningún dato personal, ruta absoluta ni credencial — la ruta a la base de datos se resuelve vía un módulo interno (`aria_paths`) no incluido en este repositorio.

**config_dominios.py**: se reemplazaron ocho nombres reales de familiares de Alejandro (lista interna de palabras clave del dominio "personal", usada para que el enrutador reconozca menciones a la familia del usuario) por marcadores genéricos `[NOMBRE_FAMILIAR_N]`. Se agregó el bloque de referencia cruzada al inicio. El resto de las listas de palabras clave (trading, tecnología, IA, programación) son términos genéricos del dominio, no datos personales, y se dejaron sin cambios — incluyendo nombres de educadores de trading públicos (ver nota abajo).

**reconstruir_aria.sh**: sin cambios de contenido. Se agregó el bloque de referencia cruzada al inicio. El script no tenía ninguna ruta absoluta de una máquina específica (usa `$HOME` en todos los casos), ni credenciales, ni nombre de usuario/hostname — las rutas a backups y al archivo `.env` se piden de forma interactiva, nunca hardcodeadas.

**Nota sobre `config_dominios.py`**: la lista de palabras clave de trading incluye varios apellidos ("villegas", "arango", "velez", "oliver velez") y un nombre de ciudad ("villahermosa") que parecen corresponder a educadores o referentes públicos de trading, en la misma línea que "sabri" (Sabri Conessa, ya acreditado en este repositorio). No se modificaron porque no hay evidencia de que sean datos personales de Alejandro o de su familia, pero quedan señalados acá para que se confirme en la revisión conjunta.

## Escaneo final de privacidad

Se corrió `scan_secrets.py` sobre los 4 archivos ya sanitizados, en conjunto, contra una carpeta de trabajo temporal (no sobre esta carpeta directamente). Resultado: sin credenciales, tokens, rutas absolutas de usuario, ni identificadores de máquina. Únicas coincidencias: menciones a "Alejandro" (2, en `memoria.py`, ya evaluadas como de bajo riesgo — nombre público en el resto del repositorio) y menciones a nombres de plataformas de trading ("binance", "bingx", en `config_dominios.py`, no son secretos). Sin resultados de la búsqueda dirigida de "alejandro_ia" (usuario WSL2) o "DESKTOP-PKP99MR" (hostname) en ninguno de los 4 archivos.

---

*Pendiente de confirmación de Alejandro y del consejo de IAs antes de subir estos archivos a git.*
