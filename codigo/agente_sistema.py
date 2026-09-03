#!/usr/bin/env python3
"""
agente_sistema.py — Estado de ARIA, archivos, exportar, function calling.
Hardware: CPU (IO puro, no necesita GPU)

---
REFERENCIA REAL, NO EJECUTABLE DE FORMA AISLADA: este es el código real
del proyecto (no una reconstrucción), pero depende de `agente_base.py`
(la clase base `AgenteBase` de la que hereda) y de otros módulos internos
(`exportar_pdf`, `resumen_diario`, `funciones`, `aria_paths`,
`chroma_client`, `cache_respuestas`, `logger_aria`) que no forman parte
de este repositorio — no se pudo verificar que `agente_base.py` en sí sea
publicable sin arrastrar más superficie interna del sistema. Por eso se
publica como referencia de cómo está escrito un agente real de ARIA, no
como parte del core mínimo ejecutable (ver `aria_core_minimo.py`, que sí
corre de punta a punta con lo que hay en esta carpeta).

Historia detrás de este patrón (agentes con detección por palabra clave,
registrados en un orquestador): /historia/07_los_bugs_que_ensenaron_mas.md
y /tecnico/arquitectura.md.

Sanitización para este repositorio: sin cambios funcionales. Se agregó
este bloque de referencia. El resto del archivo es idéntico al código
real: no contiene rutas absolutas de una máquina específica, credenciales
ni identificadores de usuario u hostname.
"""

import logging
from typing import Tuple, List
from agente_base import AgenteBase

log = logging.getLogger(__name__)


class AgenteSistema(AgenteBase):

    nombre      = "Sistema"
    descripcion = "Estado ARIA, archivos, exportar PDF, function calling, indexar"
    hardware    = "cpu"
    prioridad   = 4

    KEYWORDS = [
        "estado del sistema", "estado de aria",
        "que hora", "hora actual", "fecha de hoy",
        "cuanto es", "calcula", "calculame",
        "exporta la conversacion", "exportar pdf",
        "archivos recientes", "indexa documentos",
        "exporta el historial", "resumen diario",
    ]

    def _inicializar(self):
        log.info("Agente Sistema listo.")

    def responder(self, pregunta: str, contexto: dict = None) -> Tuple[str, List[str]]:

        # 0. Diagnostico ARIA
        if any(w in pregunta.lower() for w in ["diagnostico", "diagnóstico", "aria diagnostico"]):
            return diagnostico_aria(), []

        # 1. Exportar PDF
        try:
            from exportar_pdf import procesar_mensaje as proc_export
            resp = proc_export(pregunta)
            if resp:
                return resp, []
        except Exception:
            pass

        # 2. Resumen diario
        try:
            from resumen_diario import procesar_mensaje as proc_resumen
            llm = contexto.get("llm") if contexto else None
            resp = proc_resumen(pregunta, llm)
            if resp:
                return resp, []
        except Exception:
            pass

        # 3. Function calling (hora, calculo, estado, archivos)
        try:
            from funciones import detectar_y_ejecutar
            resp = detectar_y_ejecutar(pregunta)
            if resp:
                return resp, []
        except Exception:
            pass

        return "Comando de sistema no reconocido.", []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agente = AgenteSistema()
    print(agente.get_info())
    r, _ = agente.responder("que hora es?")
    print(r)


def diagnostico_aria() -> str:
    """
    Devuelve estado completo del sistema ARIA.
    Uso: aria "diagnostico"
    """
    import requests
    import sqlite3
    import subprocess
    from aria_paths import BASE_DIR
    from datetime import datetime

    BASE = BASE_DIR
    lineas = [f"\n=== DIAGNOSTICO ARIA === {datetime.now().strftime('%H:%M:%S')} ===\n"]

    # Ollama
    try:
        r = requests.get("http://localhost:11434", timeout=3)
        lineas.append("✅ Ollama: corriendo")
    except:
        lineas.append("❌ Ollama: NO responde")

    # api_voz
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=3)
        lineas.append("✅ api_voz: corriendo (puerto 8000)")
    except:
        lineas.append("❌ api_voz: NO responde (puerto 8000)")

    # Gradio
    try:
        r = requests.get("http://localhost:7861", timeout=3)
        lineas.append("✅ Gradio: corriendo (puerto 7861)")
    except:
        lineas.append("❌ Gradio: NO responde (puerto 7861)")

    # GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        gpu = result.stdout.strip()
        lineas.append(f"✅ GPU: {gpu}")
    except:
        lineas.append("❌ GPU: nvidia-smi no responde")

    # Memoria personal
    # Corrección (revisión Kimi, post-Fase 3): antes leía siempre
    # memoria_personal/conocimiento.json, el backend JSON viejo. memoria.py
    # (en esta misma carpeta) migró a SQLite por defecto hace tiempo — ver
    # /historia/05_memoria_y_conocimiento.md. Ahora respeta la misma
    # variable de entorno que memoria.py (MEMORIA_SQL) para contar del
    # backend que realmente está activo, en vez de asumir uno fijo.
    try:
        import os
        import json
        usar_sqlite = os.getenv("MEMORIA_SQL", "true").lower() == "true"
        if usar_sqlite:
            db_file = BASE / "memoria_personal" / "memoria.db"
            conn = sqlite3.connect(str(db_file))
            count = conn.execute(
                "SELECT COUNT(*) FROM memoria_datos WHERE activo = 1"
            ).fetchone()[0]
            conn.close()
        else:
            mem_file = BASE / "memoria_personal/conocimiento.json"
            datos = json.loads(mem_file.read_text(encoding="utf-8"))
            count = len(datos) if isinstance(datos, list) else len(datos.get("datos", []))
        lineas.append(f"✅ Memoria: {count} datos personales")
    except Exception as e:
        lineas.append(f"❌ Memoria: {e}")

    # ChromaDB
    try:
        from chroma_client import get_chroma_client
        client = get_chroma_client()
        cols = client.list_collections()
        total = sum(c.count() for c in cols)
        lineas.append(f"✅ ChromaDB: {total} chunks")
    except Exception as e:
        lineas.append(f"❌ ChromaDB: {e}")

    # Cache respuestas
    try:
        from cache_respuestas import cache_respuestas
        stats = cache_respuestas.stats()
        lineas.append(f"✅ Cache: {stats['activos']} activos / {stats['total']} total")
    except Exception as e:
        lineas.append(f"❌ Cache: {e}")

    # Logger — resumen hoy
    try:
        from logger_aria import aria_logger
        lineas.append(f"✅ Logger: {aria_logger.resumen_hoy()}")
    except Exception as e:
        lineas.append(f"❌ Logger: {e}")

    # VERSION
    try:
        version = (BASE / "VERSION").read_text().strip()
        lineas.append(f"✅ VERSION: {version}")
    except:
        lineas.append("❌ VERSION: no encontrado")

    lineas.append("\n" + "="*40 + "\n")
    return "\n".join(lineas)
