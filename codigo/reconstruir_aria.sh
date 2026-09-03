#!/bin/bash
# ================================================================
# reconstruir_aria.sh — Script de reconstruccion de ARIA V8
# Sesion 100 — Plan de Auditoria y Portabilidad
#
# Uso: se corre UNA VEZ en una maquina nueva con WSL2 ya instalado,
# antes de que exista ~/asistente. Deja todo listo para el primer
# arranque manual (no arranca ARIA solo, control manual siempre).
#
# Requiere: el ultimo backup completo accesible (ej. en un disco
# compartido /mnt/d/ARIA_BACKUPS/) y el archivo .env transportado
# por separado (nunca via git).
#
# ----------------------------------------------------------------
# Historia detrás de este código: /tecnico/metodologia_de_trabajo.md
# y /historia/11_epilogo.md documentan la disciplina de backup en tres
# capas (git + backup completo + tarea nocturna) que este script
# ayuda a restaurar en una máquina nueva; también /tecnico/instalacion.md
# para el resto del proceso de instalación manual que precede o sigue
# a esta reconstrucción.
#
# Sanitización para este repositorio: sin cambios funcionales. Se
# agregó este bloque de referencia cruzada. El resto del script es
# idéntico al real: no contiene rutas absolutas de una máquina
# específica (usa $HOME en todos los casos), ni credenciales, ni
# identificadores de usuario u hostname — las rutas a backups y al
# archivo .env se piden de forma interactiva en tiempo de ejecución,
# nunca hardcodeadas.
# ================================================================
set -e  # cortar ante cualquier error no manejado explicitamente

echo "=================================================="
echo "RECONSTRUCCION DE ARIA V8 — Sesion 100"
echo "=================================================="
echo ""

FALLOS=0

verificar() {
    local nombre="$1"
    local comando="$2"
    if eval "$comando" > /dev/null 2>&1; then
        echo "  OK: $nombre"
    else
        echo "  FALTA: $nombre"
        FALLOS=$((FALLOS + 1))
    fi
}

# Checkpoint/resume: permite retomar la reconstruccion desde el paso
# que fallo, sin tener que repetir pasos ya completados (instalar 295
# paquetes o descargar modelos de Ollama puede tardar mucho). El
# archivo vive FUERA de ~/asistente porque esa carpeta puede no existir
# todavia en la primera corrida. El Paso 7 (restaurar backup) NUNCA
# respeta el checkpoint a proposito -- siempre pide confirmacion
# interactiva, por ser el paso que sobreescribe archivos reales.
ARCHIVO_ESTADO="$HOME/.aria_reconstruccion_estado"

if [ "$1" = "--desde-cero" ]; then
    echo "Flag --desde-cero detectado: ignorando checkpoint previo."
    rm -f "$ARCHIVO_ESTADO"
fi

marcar_completo() {
    local paso="$1"
    echo "$paso" >> "$ARCHIVO_ESTADO"
}

paso_completo() {
    local paso="$1"
    [ -f "$ARCHIVO_ESTADO" ] && grep -qx "$paso" "$ARCHIVO_ESTADO"
}

if paso_completo paso1; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo "--- Paso 1: Verificando prerequisitos ---"

# Confirmar que estamos en WSL2 (no Linux nativo, no Mac)
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "  OK: Corriendo en WSL2"
else
    echo "  ADVERTENCIA: No se detecto WSL2 en /proc/version — este script fue"
    echo "  disenado y probado solo en WSL2. Continuar bajo tu propio riesgo."
fi

verificar "git instalado" "command -v git"
verificar "python3 instalado" "command -v python3"
verificar "curl instalado" "command -v curl"
verificar "ollama instalado" "command -v ollama"
verificar "sqlite3 instalado" "command -v sqlite3"
verificar "ffmpeg instalado" "command -v ffmpeg"
verificar "shellcheck instalado" "command -v shellcheck"
verificar "zstd instalado" "command -v zstd"
verificar "gcc instalado (build-essential)" "command -v gcc"
verificar "cmake instalado" "command -v cmake"

echo ""
    marcar_completo paso1
fi

if paso_completo paso2; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo "--- Paso 2: Verificando espacio en disco ---"
ESPACIO_DISPONIBLE_GB=$(df --output=avail -BG "$HOME" | tail -1 | tr -d 'G ')
echo "  Espacio disponible en \$HOME: ${ESPACIO_DISPONIBLE_GB}GB"
if [ "$ESPACIO_DISPONIBLE_GB" -lt 80 ]; then
    echo "  ADVERTENCIA: Se recomiendan al menos 80GB libres (modelos ~23GB + vectorstore ~16GB + documentos ~3GB + entorno ~8GB + git ~3GB + margen)."
    FALLOS=$((FALLOS + 1))
else
    echo "  OK: espacio suficiente"
fi

echo ""
echo "=================================================="
if [ "$FALLOS" -eq 0 ]; then
    echo "Prerequisitos OK. Continuando..."
else
    echo "Se encontraron $FALLOS problema(s). Revisar antes de continuar."
    echo "Instalar lo que falte, por ejemplo:"
    echo "  sudo apt update && sudo apt install -y git python3 python3-venv sqlite3 ffmpeg shellcheck curl zstd build-essential cmake"
    echo "  Ollama: curl -fsSL https://ollama.com/install.sh | sh"
fi
echo "=================================================="
echo ""
    marcar_completo paso2
fi

if paso_completo paso3; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo "--- Paso 3: Restaurando repositorio desde backup de git ---"

if [ -d "$HOME/asistente/.git" ]; then
    echo "  ADVERTENCIA: ya existe ~/asistente/.git — no se va a sobreescribir."
    echo "  Si queres reconstruir de cero, mové o borrá ~/asistente primero."
    exit 1
fi

read -rp "Ruta completa al archivo .bundle mas reciente (ej. /mnt/d/ARIA_BACKUPS/git/aria_repo_20260808_2110.bundle): " BUNDLE_PATH

if [ ! -f "$BUNDLE_PATH" ]; then
    echo "  ERROR: no se encontro el archivo en '$BUNDLE_PATH'"
    exit 1
fi

echo "  Verificando integridad del bundle..."
if ! git bundle verify "$BUNDLE_PATH" > /dev/null 2>&1; then
    echo "  ERROR: el bundle no es valido o esta corrupto."
    exit 1
fi
echo "  OK: bundle valido"

echo "  Clonando a ~/asistente..."
git clone "$BUNDLE_PATH" "$HOME/asistente"
echo "  OK: repositorio restaurado en ~/asistente"

cd "$HOME/asistente" || exit 1
echo "  Ultimo commit: $(git log -1 --oneline)"
echo ""
    marcar_completo paso3
fi

if paso_completo paso4; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo "--- Paso 4: Creando entorno virtual e instalando dependencias ---"

if [ -d "$HOME/asistente_env" ]; then
    echo "  ADVERTENCIA: ya existe ~/asistente_env — no se va a recrear."
else
    echo "  Creando entorno virtual..."
    python3 -m venv "$HOME/asistente_env"
    echo "  OK: entorno virtual creado"
fi

echo "  Activando entorno e instalando 295 paquetes (esto puede tardar varios minutos)..."
# shellcheck source=/dev/null
source "$HOME/asistente_env/bin/activate"
pip install --upgrade pip > /dev/null 2>&1
# Fix: con "set -e" activo, la variable STATUS=$? nunca llegaba a
# evaluarse si pip fallaba -- el script moria en la linea de pip antes
# de llegar ahi, y el bloque else con el mensaje explicativo quedaba
# como codigo muerto (confirmado con Kimi K3 + prueba aislada). El
# patron correcto es evaluar el comando directo dentro del if, igual
# al que ya usa el Paso 5 con "ollama pull".
if pip install --retries 5 --timeout 60 -r "$HOME/asistente/requirements_reconstruccion.txt"; then
    echo "  OK: dependencias instaladas correctamente"
else
    STATUS=$?
    echo "  ERROR: fallo la instalacion de dependencias (exit code $STATUS)"
    echo "  Revisar el log de pip arriba para ver que paquete fallo."
    exit $STATUS
fi
echo ""
    marcar_completo paso4
fi

if paso_completo paso5; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo ""
echo "--- Paso 4.5: Smoke test de imports criticos ---"
# Verifica que los paquetes de terceros mas usados por el codigo real
# de ARIA se puedan importar, antes de seguir con pasos mas largos
# (descarga de modelos). Atrapa temprano un conflicto de dependencias
# silencioso, en vez de descubrirlo recien al primer arranque real.
if python3 -c "import fastapi, chromadb, langchain, langchain_ollama, langchain_chroma, anthropic, openai, groq, docx, dotenv, requests; print('Imports OK')"; then
    echo "  OK: paquetes criticos importan correctamente"
else
    echo "  ERROR: fallo el import de al menos un paquete critico."
    echo "  Revisar el mensaje de Python arriba para ver cual fallo."
    exit 1
fi
echo ""

echo "--- Paso 5: Descargando modelos de Ollama ---"

if ! command -v ollama > /dev/null 2>&1; then
    echo "  Ollama no esta instalado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "  Verificando que Ollama este corriendo..."
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "  Ollama no responde, iniciando..."
    ollama serve > /tmp/ollama_reconstruccion.log 2>&1 &
    sleep 5
fi

MODELOS_CRITICOS=(
    "nomic-embed-text"
    "gemma4:e2b"
    "qwen2.5:7b"
    "qwen2.5:3b"
    "llama3.1:8b"
    "llama3.2:3b"
    "moondream"
)

# Reintentos: ollama pull es idempotente (retoma lo ya descargado, no
# empieza de cero), asi que reintentar ante un fallo transitorio de red
# es seguro. 3 intentos con 10s de espera entre cada uno.
for modelo in "${MODELOS_CRITICOS[@]}"; do
    echo "  Descargando $modelo..."
    INTENTO=1
    MAX_INTENTOS=3
    EXITO=0
    while [ $INTENTO -le $MAX_INTENTOS ]; do
        if ollama pull "$modelo"; then
            echo "    OK: $modelo (intento $INTENTO)"
            EXITO=1
            break
        else
            echo "    Intento $INTENTO/$MAX_INTENTOS fallo para $modelo"
            if [ $INTENTO -lt $MAX_INTENTOS ]; then
                echo "    Esperando 10s antes de reintentar..."
                sleep 10
            fi
        fi
        INTENTO=$((INTENTO + 1))
    done
    if [ $EXITO -eq 0 ]; then
        echo "    ERROR: fallo la descarga de $modelo tras $MAX_INTENTOS intentos"
    fi
done

echo ""
echo "  Recreando asistente-local desde el Modelfile..."
if [ -f "$HOME/asistente/asistente-local.Modelfile" ]; then
    if ollama create asistente-local -f "$HOME/asistente/asistente-local.Modelfile"; then
        echo "    OK: asistente-local recreado"
    else
        echo "    ERROR: fallo la creacion de asistente-local"
    fi
else
    echo "    ERROR: no se encontro asistente-local.Modelfile en el repositorio"
fi

echo ""
echo "  Modelos instalados:"
ollama list
echo ""
    marcar_completo paso5
fi

if paso_completo paso6; then
    echo "  (ya completado en una corrida anterior, saltando -- usar --desde-cero para forzar)"
else
echo "--- Paso 6: Recreando symlinks de CUDA ---"

sudo ln -sf "$HOME/asistente_env/lib/python3.12/site-packages/nvidia/cublas/lib/libcublas.so.12" /usr/lib/wsl/lib/libcublas.so.12 2>/dev/null
sudo ln -sf "$HOME/asistente_env/lib/python3.12/site-packages/nvidia/cublas/lib/libcublasLt.so.12" /usr/lib/wsl/lib/libcublasLt.so.12 2>/dev/null

if [ -L /usr/lib/wsl/lib/libcublas.so.12 ]; then
    echo "  OK: symlinks de CUDA creados"
else
    echo "  ADVERTENCIA: no se pudieron crear los symlinks (revisar permisos sudo)."
    echo "  api_voz.py podria no arrancar sin esto."
fi

echo ""
    marcar_completo paso6
fi

echo "--- Paso 7: Restaurando el ultimo backup completo ---"
echo ""
echo "  IMPORTANTE: esto va a sobreescribir archivos dentro de ~/asistente"
echo "  con el contenido del backup (vectorstore, memoria_personal, documentos, etc)."
echo ""

read -rp "  Ruta completa al backup completo mas reciente (ej. /mnt/d/ARIA_BACKUPS/completos/backup_completo_FECHA.tar.gz): " BACKUP_PATH

if [ ! -f "$BACKUP_PATH" ]; then
    echo "  ERROR: no se encontro el archivo en '$BACKUP_PATH'"
    exit 1
fi

echo "  Verificando integridad del backup..."
if ! tar -tzf "$BACKUP_PATH" > /dev/null 2>&1; then
    echo "  ERROR: el backup esta corrupto o incompleto."
    exit 1
fi
echo "  OK: backup integro"

echo "  Restaurando (esto puede tardar varios minutos, backup de ~12GB)..."
# Mismo fix que el Paso 4 (Patron: set -e mata la linea de tar antes
# de que STATUS=$? llegue a evaluarse, dejando el bloque else como
# codigo muerto). Comando directo dentro del if.
if tar -xzf "$BACKUP_PATH" -C "$HOME"; then
    echo "  OK: backup restaurado en ~/asistente"
else
    STATUS=$?
    echo "  ERROR: fallo la restauracion (exit code $STATUS)"
    exit $STATUS
fi

echo ""
echo "  IMPORTANTE: el archivo .env NO viene en el backup ni en git."
echo "  Debe copiarse a mano desde un canal seguro (USB, gestor de contraseñas)"
echo "  a la ruta: $HOME/asistente/.env"
read -rp "  Presiona Enter cuando hayas copiado el .env, para continuar..."

if [ -f "$HOME/asistente/.env" ]; then
    echo "  OK: .env encontrado"
else
    echo "  ADVERTENCIA: .env todavia no existe. ARIA no va a poder usar las APIs."
    echo "  Copialo antes del primer arranque."
fi
echo ""
echo "=================================================="
echo "RECONSTRUCCION COMPLETADA"
echo "=================================================="
echo ""
echo "Resumen:"
echo "  - Repositorio restaurado en: $HOME/asistente"
echo "  - Entorno virtual: $HOME/asistente_env"
echo "  - Modelos de Ollama: descargados/verificados"
echo "  - Symlinks de CUDA: creados"
echo "  - Backup completo: restaurado"
echo ""
echo "IMPORTANTE, antes del primer arranque, verificar a mano:"
echo "  1. Que ~/asistente/.env exista con todas las claves (ver ENTORNO.md seccion 5)"
echo "  2. Correr: cat ~/asistente/ENTORNO.md para revisar cualquier paso manual pendiente"
echo "  3. NO se arranca ARIA automaticamente -- esta es una decision consciente"
echo "     del proyecto (Sesion 98): el primer arranque siempre debe ser manual"
echo "     y supervisado, para ver en vivo si algo falla."
echo ""
echo "Para el primer arranque manual:"
echo "  cd ~/asistente && bash lanzar_asistente.sh"
echo ""
echo "Si algo falla en el primer arranque, revisar en este orden:"
echo "  1. test_basicos.py (corre solo al arrancar, muestra que esta OK/fallando)"
echo "  2. Symlinks de CUDA si api_voz no arranca (seccion 4 de ENTORNO.md)"
echo "  3. Variables de .env si algun agente da error de API key"
echo "=================================================="
