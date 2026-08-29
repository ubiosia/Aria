# Instalación

Pasos base para levantar un entorno equivalente al de ARIA sobre Windows 11 + WSL2 (Ubuntu). Esta guía documenta el camino real que se siguió, incluyendo los errores encontrados en el camino — cada uno con su causa y su solución, porque en varios casos el mensaje de error no explicaba bien el problema real.

> Antes de instalar nada: verificar el entorno real con comandos de diagnóstico, nunca asumirlo. El proyecto arrancó asumiendo una instalación de Ubuntu en dual-boot que en realidad no existía — era WSL2. Ver [`/tecnico/decisiones.md`](decisiones.md) para el detalle de esa decisión.

## 1. Actualizar Ubuntu e instalar dependencias del sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-dev portaudio19-dev \
    ffmpeg espeak-ng libespeak-ng-dev git wget curl zstd
```

## 2. Instalar Ollama (servidor local de modelos)

Ollama gestiona los modelos de lenguaje y expone una API local.

**Problema encontrado:** el instalador de Ollama falló con `ERROR: This version requires zstd for extraction`, porque la distribución de Ubuntu usada no trae `zstd` instalado por defecto. Se resuelve instalando esa dependencia antes de correr el instalador (ya incluida en el paso 1 de esta guía).

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Verificar que el servicio responde:
curl http://localhost:11434
# Respuesta esperada: "Ollama is running"
```

## 3. Descargar los modelos de IA

```bash
ollama pull llama3.1:8b          # modelo principal
ollama pull nomic-embed-text     # modelo de embeddings para RAG
```

Se creó además un modelo personalizado a partir del modelo base, con un `Modelfile` que fija un `SYSTEM prompt` explícito con la identidad del asistente. **Motivo:** sin ese prompt, el modelo base respondía en ocasiones identificándose como un asistente distinto (heredado de sus datos de entrenamiento) — fijar la identidad de forma explícita resolvió el problema por completo.

## 4. Entorno Python

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

## 5. Síntesis de voz (TTS) offline

Se usó Piper para generar audio a partir de texto, de forma completamente local.

**Problema encontrado:** tras instalar Piper, el comando `piper --version` devolvía "Command not found" — el symlink apuntaba a una carpeta en vez de al binario ejecutable (la estructura de la descarga tiene una carpeta `piper` dentro de otra carpeta `piper`). Se resuelve verificando con `ls -la` a dónde apunta el symlink antes de asumir que está bien, y corrigiéndolo para que apunte al binario real, no a la carpeta contenedora.

## 6. GPU para el reconocimiento de voz (Whisper)

**Problema encontrado, recurrente:** tras un reinicio de la máquina, `nvidia-smi` dejaba de funcionar dentro de Ubuntu con el error "could not communicate with the NVIDIA driver". La causa es que la ruta de librerías de WSL2 (`/usr/lib/wsl/lib`) no queda incluida por defecto en el `PATH` del sistema Linux. La solución permanente es agregar esa ruta al `.bashrc`:

```bash
echo 'export PATH=/usr/lib/wsl/lib:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

## 7. Micrófono

WSL2 no tiene acceso directo y estable al hardware de audio de Windows. La solución adoptada no es técnicamente elegante, pero es robusta: grabar el audio del lado de Windows y pasarlo a Linux a través de una carpeta compartida entre ambos sistemas, en vez de intentar forzar una comunicación directa de hardware entre Windows y WSL2.

## 8. Verificación final

Antes de dar la instalación por terminada, confirmar cada componente por separado: que Ollama responde, que el modelo personalizado se identifica correctamente, que el entorno Python activa sin errores, que Piper genera un archivo de audio de prueba, que `nvidia-smi` reporta la GPU, y que una pregunta de prueba real a través de la interfaz obtiene una respuesta coherente.

---

*Nota editorial: los pasos y errores de esta guía están documentados con cita textual completa en el manual técnico interno del proyecto, correspondiente a las primeras semanas de instalación (mayo-junio de 2026). Se generalizaron rutas de disco y nombres de usuario reales que aparecían en la fuente original, siguiendo la regla de privacidad de este repositorio.*
