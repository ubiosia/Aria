#!/usr/bin/env python3
"""
agente_noticias.py — Monitorea noticias crypto y tecnologia. Hardware: CPU

---
REFERENCIA REAL, NO EJECUTABLE DE FORMA AISLADA: este es el código real
del proyecto (no una reconstrucción), pero depende de `agente_base.py`
(la clase base `AgenteBase`), del paquete `ddgs` (no incluido en
`requirements.txt` de este core mínimo — no es parte del core, es
búsqueda web opcional) y de un archivo `sitios_preferidos.json` que no
se publica en este repositorio. Se publica como referencia de cómo está
escrito un agente real de ARIA, no como parte del core mínimo ejecutable
(ver `aria_core_minimo.py`, que sí corre de punta a punta con lo que hay
en esta carpeta).

Historia detrás de este patrón (agentes con detección por palabra clave,
registrados en un orquestador): /historia/07_los_bugs_que_ensenaron_mas.md
y /tecnico/arquitectura.md.

Sanitización para este repositorio: sin cambios funcionales. Se agregó
este bloque de referencia. El resto del archivo es idéntico al código
real: no contiene rutas absolutas de una máquina específica, credenciales
ni identificadores de usuario u hostname — BASE_DIR se resuelve vía
Path.home(), igual que en memoria.py y auditar_decision.py.
"""

import json
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Tuple, List
from agente_base import AgenteBase

log = logging.getLogger(__name__)
BASE_DIR = Path.home() / "asistente"
NOTICIAS_FILE = BASE_DIR / "memoria_personal" / "ultimas_noticias.json"


class AgenteNoticias(AgenteBase):
    nombre      = "Noticias"
    descripcion = "Noticias crypto y tecnologia en background (CPU)"
    hardware    = "cpu"
    prioridad   = 7

    KEYWORDS = [
        "noticias", "novedades", "que paso", "que hay",
        "noticias de hoy", "noticias crypto", "noticias bitcoin",
        "noticias ethereum", "noticias tecnologia",
    ]

    def _inicializar(self):
        NOTICIAS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._monitor_activo = False

    def responder(self, pregunta: str, contexto: dict = None) -> Tuple[str, List[str]]:
        msg = pregunta.lower()
        if any(w in msg for w in ["crypto","bitcoin","btc","ethereum","eth"]):
            return self._buscar_noticias("crypto")
        elif any(w in msg for w in ["tecnologia","tech","ia"]):
            return self._buscar_noticias("tecnologia")
        return self._buscar_noticias("general")

    def _buscar_noticias(self, categoria: str) -> Tuple[str, List[str]]:
        try:
            from ddgs import DDGS
            sitios_file = BASE_DIR / "sitios_preferidos.json"
            sitios = json.load(open(sitios_file)) if sitios_file.exists() else {}
            queries = {
                "crypto":     "noticias bitcoin ethereum crypto hoy",
                "tecnologia": "noticias tecnologia IA hoy",
                "general":    "noticias crypto tecnologia hoy",
            }
            query = queries.get(categoria, queries["general"])
            sitios_usar = (sitios.get("noticias",[]) + sitios.get("trading",[]))[:4]
            resultados = []
            for sitio in sitios_usar:
                try:
                    with DDGS() as ddgs:
                        res = list(ddgs.text(f"site:{sitio} {query}", max_results=2))
                    for r in res:
                        resultados.append({"titulo": r.get("title",""), "cuerpo": r.get("body","")[:200], "fuente": sitio})
                except Exception:
                    continue
            if not resultados:
                with DDGS() as ddgs:
                    res = list(ddgs.text(query, max_results=5))
                for r in res:
                    resultados.append({"titulo": r.get("title",""), "cuerpo": r.get("body","")[:200], "fuente": "web"})
            if not resultados:
                return "No encontre noticias recientes.", []
            self._guardar(resultados, categoria)
            txt = f"Noticias ({categoria}):\n\n"
            for i, n in enumerate(resultados[:5], 1):
                txt += f"{i}. {n['titulo']}\n   {n['cuerpo'][:150]}\n   [{n['fuente']}]\n\n"
            return txt.strip(), [r["fuente"] for r in resultados[:3]]
        except Exception as e:
            return f"Error: {e}", []

    def _guardar(self, noticias, categoria):
        try:
            cache = json.load(open(NOTICIAS_FILE)) if NOTICIAS_FILE.exists() else {}
            cache[categoria] = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "noticias": noticias[:5]}
            json.dump(cache, open(NOTICIAS_FILE,'w'), ensure_ascii=False, indent=2)
        except Exception:
            pass

    def iniciar_monitor(self, intervalo_horas: int = 2):
        if self._monitor_activo:
            return
        self._monitor_activo = True
        def monitor():
            while self._monitor_activo:
                try:
                    self._buscar_noticias("crypto")
                    self._buscar_noticias("tecnologia")
                except Exception:
                    pass
                time.sleep(intervalo_horas * 3600)
        threading.Thread(target=monitor, daemon=True).start()
        log.info("Monitor noticias activo (CPU).")


def analizar_sentimiento_noticias(noticias: list, simbolo: str = "crypto") -> dict:
    """
    Clasifica las top 5 noticias de -10 a +10 usando llama3.2:3b.
    Ejecutar cada 30 minutos desde gestor_async, no en tiempo real.
    Devuelve: {"score": float, "resumen": str, "timestamp": int}
    """
    import time
    import requests
    import json as _json

    if not noticias:
        return {"score": 0, "resumen": "Sin noticias disponibles", "timestamp": int(time.time())}

    # Solo top 5 — no todas
    top5 = noticias[:5]
    titulos = "\n".join([f"- {n.get('titulo', '')}" for n in top5])

    prompt = f"""Analizá estas noticias de {simbolo} y dá un puntaje de sentimiento del mercado.
Escala: -10 (muy negativo) a +10 (muy positivo). Solo respondé con JSON.

Noticias:
{titulos}

Respondé SOLO con este JSON sin texto adicional:
{{"score": 7.5, "resumen": "descripcion breve en espanol"}}"""

    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 100}
        }, timeout=30)

        texto = r.json().get("response", "").strip()

        # Extraer JSON de la respuesta
        import re
        match = re.search(r'\{[^}]+\}', texto)
        if match:
            resultado = _json.loads(match.group())
            resultado["timestamp"] = int(time.time())
            return resultado

    except Exception as e:
        pass

    return {"score": 0, "resumen": "Error al analizar sentimiento", "timestamp": int(time.time())}
