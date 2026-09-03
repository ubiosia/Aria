#!/usr/bin/env python3
"""
auditar_decision.py

Fase 2 del cronograma general de mejoras (Sesion 105), ultimo item:
"auditor de decisiones". Comando de solo lectura que explica por que
ARIA respondio lo que respondio a una pregunta puntual, reconstruyendo
la evidencia real de aria_traces.db (traces + trace_events).

No reconstruye decisiones de arquitectura del proyecto (eso vive en
los manuales de sesion) -- explica el camino real que tomo una
respuesta especifica dentro del sistema: que handler/ruta la
respondio, que eventos de router/cache se registraron, y con que
confianza (si el medidor de confianza aplico a esa respuesta).

Uso: python3 auditar_decision.py "PREGUNTA EXACTA O PARCIAL"

---
Historia detrás de este código: mencionado en el Capítulo 7
(/historia/07_los_bugs_que_ensenaron_mas.md) como parte de la respuesta
de fondo del proyecto a los bugs de esa etapa -- no arregla un sintoma
puntual, sino que da una forma de auditar, despues del hecho, por que
el sistema tomo la decision que tomo. Ver también /tecnico/bugs_famosos.md
para los casos concretos que este tipo de herramienta ayuda a diagnosticar.

Sanitización para este repositorio: sin cambios funcionales. Se agregó
este bloque de referencia cruzada; el resto del archivo es idéntico al
código real en producción. No contiene rutas absolutas, credenciales ni
identificadores de máquina: la ruta a la base de datos se resuelve vía
aria_paths.BASE_DIR (módulo interno del proyecto, no incluido en este
repositorio) en tiempo de ejecución.
"""
import sys
import sqlite3
import json
from datetime import datetime

from aria_paths import BASE_DIR

RUTA_DB = BASE_DIR / "aria_traces.db"


def buscar_trace_mas_reciente(fragmento_pregunta):
    with sqlite3.connect(RUTA_DB) as conn:
        conn.row_factory = sqlite3.Row
        fila = conn.execute(
            "SELECT * FROM traces WHERE query LIKE ? ORDER BY ts_start DESC LIMIT 1",
            (f"%{fragmento_pregunta}%",),
        ).fetchone()
        return dict(fila) if fila else None


def obtener_eventos(trace_id):
    with sqlite3.connect(RUTA_DB) as conn:
        conn.row_factory = sqlite3.Row
        filas = conn.execute(
            "SELECT * FROM trace_events WHERE trace_id = ? ORDER BY ts ASC",
            (trace_id,),
        ).fetchall()
        return [dict(f) for f in filas]


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 auditar_decision.py \"PREGUNTA EXACTA O PARCIAL\"")
        sys.exit(1)

    fragmento = " ".join(sys.argv[1:])
    trace = buscar_trace_mas_reciente(fragmento)

    if not trace:
        print(f"No se encontro ninguna traza que coincida con: '{fragmento}'")
        return

    print(f"\n{'='*60}")
    print("  AUDITOR DE DECISIONES")
    print(f"{'='*60}\n")

    ts = datetime.fromtimestamp(trace["ts_start"]).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Pregunta real: {trace['query']}")
    print(f"Fecha: {ts}")
    print(f"Trace ID: {trace['trace_id']}")
    print(f"Estado: {trace['status']}")
    if trace.get("latency_ms"):
        print(f"Latencia total: {trace['latency_ms']:.0f} ms")

    print(f"\n--- Camino que tomo la decision ---")
    print(f"final_path: {trace.get('final_path', 'N/A')}")
    print(f"final_route: {trace.get('final_route', 'N/A')}")

    eventos = obtener_eventos(trace["trace_id"])
    if eventos:
        print(f"\n--- Eventos registrados durante el procesamiento ({len(eventos)}) ---")
        for ev in eventos:
            payload = json.loads(ev["payload"]) if ev["payload"] else {}
            print(f"  [{ev['layer']}] {payload}")
    else:
        print("\n--- Sin eventos adicionales registrados ---")

    print(f"\n--- Respuesta dada ---")
    respuesta = trace.get("response", "")
    print(f"  {respuesta[:300]}{'...' if len(respuesta) > 300 else ''}")

    if trace.get("error"):
        print(f"\n--- Error registrado ---")
        print(f"  {trace['error']}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
