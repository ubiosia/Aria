# Instalación

Pasos base para levantar un entorno equivalente al de ARIA sobre Windows 11 + WSL2 (Ubuntu). Esta guía documenta el camino real que se siguió, incluyendo los errores encontrados en el camino — cada uno con su causa y su solución, porque en varios casos el mensaje de error no explicaba bien el problema real.

> Antes de instalar nada: verificar el entorno real con comandos de diagnóstico, nunca asumirlo. El proyecto arrancó asumiendo una instalación de Ubuntu en dual-boot que en realidad no existía — era WSL2. Ver [`/tecnico/decisiones.md`](decisiones.md) para el detalle de esa decisión.

## 0. Hardware utilizado

La máquina donde se instaló y corrió ARIA de punta a punta: procesador Intel i9-10900, placa de video NVIDIA RTX 3080 con 10 GB de memoria dedicada, y 48 GB de memoria RAM. Ese es el hardware documentado el primer día del proyecto, el 25 de mayo de 2026 (ver [`/historia/01_el_origen.md`](../historia/01_el_origen.md)).

No hay, en el material disponible, ninguna prueba documentada del sistema corriendo sobre hardware más modesto — menos VRAM, sin GPU dedicada, o menos RAM. Cualquier afirmación sobre un mínimo real inferior sería una suposición, no un hecho verificado, así que esta guía no la hace. Lo que sí está documentado es en qué se usa la GPU concretamente: aceleración de Whisper para reconocimiento de voz, cálculo de indicadores técnicos (RSI/MACD/EMAs) con CuPy, y los modelos de lenguaje locales servidos por Ollama. Un sistema sin GPU dedicada podría en teoría correr los mismos componentes sobre CPU, pero eso tampoco se probó ni se documentó en ninguna sesión.

**Nota práctica sobre la RAM:** WSL2, sin un archivo `.wslconfig` explícito, se limita por defecto a aproximadamente el 50% de la RAM física de la máquina — no toda. Esto generó cuelgues reales del sistema en producción cuando la RAM física disponible bajó en un momento del proyecto, hasta que se diagnosticó la causa y se corrigió subiendo el límite explícitamente en `.wslconfig` (fuera del repositorio de ARIA, en la carpeta de usuario de Windows). Vale la pena configurar ese límite desde el arranque inicial en vez de esperar a que aparezca el problema.

## 1. Instalar WSL2 en Windows

Desde PowerShell como administrador:

```powershell
wsl --install -d Ubuntu-24.04
```

**Decisión real tomada en el proyecto:** en una reinstalación completa del sistema, se optó explícitamente por Ubuntu 24.04 LTS en lugar de una versión más nueva (26.04) que se había usado antes. Los motivos documentados: Python 3.12 (estable, sin los bugs de `venv` que traía la versión más nueva de Python), drivers NVIDIA probados y estables, y soporte LTS garantizado por 5 años. Esta guía sigue esa misma elección.

Al finalizar la instalación, WSL pide crear un usuario Linux y su contraseña — es un usuario nuevo, propio de la instalación de Ubuntu, no la cuenta de Windows.

## 2. Actualizar Ubuntu e instalar dependencias del sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-dev portaudio19-dev \
    ffmpeg espeak-ng libespeak-ng-dev git wget curl zstd
```

## 3. Instalar Ollama (servidor local de modelos)

Ollama gestiona los modelos de lenguaje y expone una API local.

**Problema encontrado:** el instalador de Ollama falló con `ERROR: This version requires zstd for extraction`, porque la distribución de Ubuntu usada no trae `zstd` instalado por defecto. Se resuelve instalando esa dependencia antes de correr el instalador (ya incluida en el paso 2 de esta guía).

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Verificar que el servicio responde:
curl http://localhost:11434
# Respuesta esperada: "Ollama is running"
```

## 4. Descargar los modelos de IA

```bash
ollama pull llama3.1:8b          # modelo principal
ollama pull nomic-embed-text     # modelo de embeddings para RAG
```

Se creó además un modelo personalizado a partir del modelo base, con un `Modelfile` que fija un `SYSTEM prompt` explícito con la identidad del asistente. **Motivo:** sin ese prompt, el modelo base respondía en ocasiones identificándose como un asistente distinto (heredado de sus datos de entrenamiento) — fijar la identidad de forma explícita resolvió el problema por completo.

## 5. Entorno Python

**Problema encontrado:** `python3 -m venv` falló con `ensurepip is not available`, porque algunas distribuciones separan el módulo `venv` en un paquete aparte por versión de Python.

```bash
sudo apt install python3.<version>-venv -y
python3 -m venv ~/asistente_env
source ~/asistente_env/bin/activate
```

Instalar las dependencias principales sin fijar versiones exactas — el intento original con versiones fijas de `chromadb` y `langchain-chroma` generó un conflicto de dependencias irresoluble. Dejar que el gestor de paquetes resuelva la compatibilidad por sí solo evitó el problema:

```bash
pip install gradio ollama chromadb \
    langchain langchain-community langchain-ollama langchain-chroma \
    pypdf pymupdf python-docx docx2txt \
    faster-whisper pyaudio sounddevice soundfile \
    requests pydantic youtube-transcript-api
```

## 6. Síntesis de voz (TTS) offline

Se usó Piper para generar audio a partir de texto, de forma completamente local.

**Problema encontrado:** tras instalar Piper, el comando `piper --version` devolvía "Command not found" — el symlink apuntaba a una carpeta en vez de al binario ejecutable (la estructura de la descarga tiene una carpeta `piper` dentro de otra carpeta `piper`). Se resuelve verificando con `ls -la` a dónde apunta el symlink antes de asumir que está bien, y corrigiéndolo para que apunte al binario real, no a la carpeta contenedora.

## 7. GPU para el reconocimiento de voz (Whisper)

**Problema encontrado, recurrente:** tras un reinicio de la máquina, `nvidia-smi` dejaba de funcionar dentro de Ubuntu con el error "could not communicate with the NVIDIA driver". La causa es que la ruta de librerías de WSL2 (`/usr/lib/wsl/lib`) no queda incluida por defecto en el `PATH` del sistema Linux. La solución permanente es agregar esa ruta al `.bashrc`:

```bash
echo 'export PATH=/usr/lib/wsl/lib:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

## 8. Micrófono

WSL2 no tiene acceso directo y estable al hardware de audio de Windows. La solución adoptada no es técnicamente elegante, pero es robusta: grabar el audio del lado de Windows y pasarlo a Linux a través de una carpeta compartida entre ambos sistemas, en vez de intentar forzar una comunicación directa de hardware entre Windows y WSL2.

## 9. Estructura de carpetas mínima

El proyecto vive en `~/asistente/`, dentro del usuario de Linux (no en una carpeta de Windows montada, salvo para los documentos a indexar — ver más abajo). La estructura mínima real, documentada a lo largo de las sesiones, es:

```
~/asistente/
├── aria_core.py           # punto de entrada de la lógica de respuesta
├── ingesta.py              # indexa documentos nuevos al RAG (ChromaDB)
├── agente_sistema.py        # agente de diagnóstico y estado del sistema
├── agente_noticias.py       # agente de noticias/sentimiento
├── cache_respuestas.py      # caché de respuestas ya generadas
├── logger_aria.py           # logging estructurado a JSONL
├── ohlcv_cache.py           # caché de velas de precio (trading)
├── decision_log.py          # registro de decisiones de trading
├── watchdog.py               # supervisa los procesos y reinicia si hace falta
├── telegram_bot.py          # integración con Telegram
├── test_basicos.py           # suite de pruebas mínimas del sistema
├── rollback.sh                # vuelve el código a un tag de git anterior
├── start_aria.sh              # arranca todos los servicios en orden (ver sección 10)
└── logs/
    └── aria_YYYY-MM-DD.jsonl  # un archivo de log por día
```

Los documentos a indexar en el RAG viven en Windows, en una carpeta que ARIA lee (montada desde `/mnt/c/...` o sincronizada) — no dentro de `~/asistente/`. El patrón real documentado fue una carpeta de Windows dedicada a esto (`Documents\Documentos IA\`), detectada e indexada automáticamente en cada arranque. Formatos soportados: PDF, Word (`.docx`), TXT, Markdown y CSV.

`~/asistente_env/` (el entorno virtual de Python, paso 5) vive fuera de `~/asistente/`, como carpeta hermana — no es parte del código del proyecto y no se versiona con git.

## 10. Ejemplo de script de arranque (sanitizado)

El proyecto real usa `start_aria.sh` para levantar todos los servicios en orden, con verificación de salud en cada paso. El ejemplo de abajo **no es el código fuente original** (no se dispone del archivo literal para publicar) — es una reconstrucción fiel de la lógica documentada en las sesiones donde se creó y ajustó el script, pensada para que alguien pueda replicar el mismo comportamiento:

```bash
#!/bin/bash
# start_aria.sh — arranque ordenado de todos los servicios de ARIA
# Reconstrucción sanitizada del comportamiento documentado del script real.

cd ~/asistente
source ~/asistente_env/bin/activate

# 1. Matar procesos viejos antes de arrancar.
# IMPORTANTE: el patrón de pkill debe matchear el comando REAL del proceso
# (visible en `ps aux`), no el nombre del archivo .py que uno cree que corre.
# Un bug real del proyecto: "pkill -f api_voz.py" no mataba nada porque el
# proceso real corría como "uvicorn api_voz:app" — dejaba procesos zombies
# vivos y el puerto ocupado en el siguiente arranque.
pkill -f "api_aria:app" 2>/dev/null
pkill -f "api_voz:app" 2>/dev/null
pkill -f "telegram_bot" 2>/dev/null
pkill -f "gradio_app" 2>/dev/null
sleep 2

# 2. Verificar la variable de modo antes de levantar nada.
echo "TRADING_MODE actual: ${TRADING_MODE:-no seteado}"

# 3. Levantar los servicios EN ORDEN, con verificación de salud entre cada uno.
uvicorn api_aria:app --host 0.0.0.0 --port 8001 &
sleep 5
curl -sf http://localhost:8001 > /dev/null || echo "ERROR: api_aria no responde"

uvicorn api_voz:app --host 0.0.0.0 --port 8000 &
# Whisper tarda más de 5 segundos en cargar en GPU — un sleep corto acá
# generaba falsos "ERROR: api_voz no responde" en el chequeo de salud.
# Se ajustó a 15 segundos tras confirmar la causa real.
sleep 15
curl -sf http://localhost:8000 > /dev/null || echo "ERROR: api_voz no responde"

python telegram_bot.py &
sleep 3

python gradio_app.py &
sleep 3
curl -sf http://localhost:7861 > /dev/null || echo "ERROR: gradio_app no responde"

echo "=== ARIA arrancado ==="
```

Sin rutas de disco reales, sin credenciales y sin nombres de host — solo el orden de arranque, los puertos usados y la lógica de verificación que el proyecto real documentó como necesaria para un arranque limpio y repetible.

## 11. Verificación final

Antes de dar la instalación por terminada, confirmar cada componente por separado: que Ollama responde, que el modelo personalizado se identifica correctamente, que el entorno Python activa sin errores, que Piper genera un archivo de audio de prueba, que `nvidia-smi` reporta la GPU, y que una pregunta de prueba real a través de la interfaz obtiene una respuesta coherente.

---

*Nota editorial: los pasos y errores de las secciones 2 a 8 (y la sección 11) están documentados con cita textual completa en el manual técnico interno del proyecto, correspondiente a las primeras semanas de instalación (mayo-junio de 2026), tal como ya constaba en la versión anterior de esta guía. Las secciones agregadas en esta ampliación tienen distinto grado de certeza y se distinguen así: el hardware (sección 0) y el comando `wsl --install -d Ubuntu-24.04` con la comparación Ubuntu 24.04 vs. 26.04 (sección 1) están tomados con cita textual de una reinstalación completa documentada en la Sesión 18 (1 de junio de 2026) y de la Sesión 1 (25 de mayo de 2026) respectivamente. La nota sobre el límite de memoria de WSL2 (sección 0) está tomada con cita textual de la Sesión 86. La estructura de carpetas (sección 9) es una reconstrucción a partir de referencias reales a archivos y rutas dispersas en múltiples sesiones (principalmente las primeras 22 y la 41-42) — no existe, en el material disponible, una única sesión que documente el árbol completo de una sola vez. El script de arranque (sección 10) es una reconstrucción de comportamiento documentado (Sesiones 41-42), explícitamente marcada como tal en el cuerpo del documento: no es el código fuente original, que no está disponible para publicar. Se generalizaron rutas de disco y nombres de usuario reales que aparecían en las fuentes originales, siguiendo la regla de privacidad de este repositorio.*
