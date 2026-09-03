@echo off
REM arrancar_aria.bat — equivalente Windows de arrancar_aria.sh (Fase 3, Punto 3)
REM
REM Qué hace, en orden:
REM 1. Crea un entorno virtual si no existe (.\venv, relativo a este
REM    repositorio clonado).
REM 2. Lo activa, e instala requirements-core.txt si todavía no se
REM    instaló — SOLO chromadb + ollama, lo que codigo\aria_core_minimo.py
REM    usa de verdad. NO usa requirements.txt completo a propósito: ese
REM    incluye dependencias de voz que pueden fallar al compilar sin las
REM    herramientas de compilación de Windows instaladas (ver
REM    requirements-core.txt para el detalle de por qué existe este
REM    archivo separado, confirmado en Linux/WSL2 — no verificado
REM    específicamente en Windows, pero el mismo paquete pyaudio es el
REM    que en general requiere más pasos manuales para compilar ahí).
REM 3. Carga variables desde .env si existe (creado a partir de
REM    .env.example — ver tecnico\configuracion.md).
REM 4. Lanza codigo\aria_core_minimo.py, pasándole los argumentos que se
REM    le dieron a este script (la pregunta de prueba).
REM
REM A propósito NO dockeriza nada (mismo criterio que arrancar_aria.sh).

setlocal enabledelayedexpansion
cd /d "%~dp0"

if not exist venv (
    echo Creando entorno virtual ^(.\venv^)...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist venv\.requirements_core_instalados (
    echo Instalando dependencias del core minimo ^(requirements-core.txt: chromadb + ollama^)...
    pip install -q -r requirements-core.txt
    type nul > venv\.requirements_core_instalados
)

if exist .env (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" set "%%A=%%B"
    )
) else (
    echo ADVERTENCIA: no existe .env - copia .env.example a .env y completa lo que necesites.
    echo El core minimo va a correr igual, pero sin las variables que dependan de el ^(ver tecnico\configuracion.md^).
)

python codigo\aria_core_minimo.py %*
