#!/bin/bash
# arrancar_aria.sh — arranque simple del core mínimo (Fase 3, Punto 3)
#
# Qué hace, en orden:
# 1. Crea un entorno virtual si no existe (./venv, relativo a este
#    repositorio clonado). Nota: esto es distinto de la convención real
#    del proyecto (~/asistente_env como carpeta hermana de ~/asistente/,
#    ver /tecnico/instalacion.md sección 5) — acá se usa ./venv porque
#    este repositorio se clona en cualquier lugar, no vive fijo en
#    ~/asistente/.
# 2. Lo activa, e instala requirements-core.txt si todavía no se instaló
#    (SOLO chromadb + ollama — lo que aria_core_minimo.py usa de verdad;
#    ver la nota dentro de ese archivo). NO usa requirements.txt completo
#    a propósito: ese incluye dependencias de voz que necesitan paquetes
#    de sistema (portaudio19-dev, ver /tecnico/instalacion.md sección 2)
#    y hacen fallar la instalación completa si no están — se confirmó
#    este bloqueo corriendo la instalación real sin ese paquete.
# 3. Carga variables desde .env si existe (creado a partir de
#    .env.example — ver /tecnico/configuracion.md para qué es cada una).
# 4. Lanza codigo/aria_core_minimo.py, pasándole los argumentos que se
#    le dieron a este script (la pregunta de prueba).
#
# A propósito NO dockeriza nada (Fase 3: no agregar esa capa de
# complejidad antes de que lo básico funcione). Sirve para correr el
# core mínimo local, sin nada más.

set -e

DIR_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR_SCRIPT"

if [ ! -d venv ]; then
    echo "Creando entorno virtual (./venv)..."
    python3 -m venv venv
fi

# shellcheck source=/dev/null
source venv/bin/activate

if [ ! -f venv/.requirements_core_instalados ] || [ requirements-core.txt -nt venv/.requirements_core_instalados ]; then
    echo "Instalando dependencias del core mínimo (requirements-core.txt: chromadb + ollama)..."
    pip install -q -r requirements-core.txt
    touch venv/.requirements_core_instalados
fi

if [ -f .env ]; then
    set -a
    # shellcheck source=/dev/null
    source .env
    set +a
else
    echo "ADVERTENCIA: no existe .env — copiá .env.example a .env y completá lo que necesites."
    echo "El core mínimo va a correr igual, pero sin las variables que dependan de él (ver tecnico/configuracion.md)."
fi

python3 codigo/aria_core_minimo.py "$@"
