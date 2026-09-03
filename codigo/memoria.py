#!/usr/bin/env python3
"""
memoria.py — Sistema de memoria personal de ARIA.
Guarda lo que Alejandro le enseña directamente.

PROYECTO ARIA V8 — Fase 1: Memoria Relacional
Backend SQLite, con interfaz pública IDÉNTICA a la versión JSON original,
para que aria_core.py y los handlers no necesiten ningún cambio.

Flag de emergencia: si algo sale mal con SQLite, se puede volver al
backend JSON original sin tocar código, seteando la variable de entorno:
    export MEMORIA_SQL=false
    (por defecto, MEMORIA_SQL=true usa SQLite)

---
Historia detrás de este código: /historia/05_memoria_y_conocimiento.md
(el bug del "dónde vivo", diagnosticado tres veces antes de encontrar la
causa real, y la migración del backend JSON a SQLite). El método
_responder_pregunta_puntual() y la tabla PREGUNTAS_PUNTUALES de más abajo
son exactamente la solución final descripta ahí: búsqueda determinística
en base de datos para preguntas puntuales de memoria personal, sin pasar
por el LLM — ver también /tecnico/bugs_famosos.md, sección "El volcado de
memoria personal".

Sanitización para este repositorio: sin cambios funcionales. Se agregó
este bloque de referencia cruzada; el resto del archivo es idéntico al
código real en producción (no contiene rutas absolutas ni credenciales:
BASE_DIR se resuelve en tiempo de ejecución a partir del home del usuario
y de una variable de entorno opcional).
"""

import json
import logging
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

BASE_DIR = Path(os.getenv("ARIA_BASE_DIR", str(Path.home() / "asistente")))
MEM_FILE = BASE_DIR / "memoria_personal" / "conocimiento.json"   # backend viejo, se conserva como respaldo
MEM_DIR = BASE_DIR / "memoria_personal"
DB_FILE = BASE_DIR / "memoria_personal" / "memoria.db"           # backend nuevo

USAR_SQLITE = os.getenv("MEMORIA_SQL", "true").lower() == "true"

log = logging.getLogger(__name__)

PREFIJOS_APRENDER = [
    "aprendé esto:", "aprende esto:", "recordá esto:", "recorda esto:",
    "guardá esto:", "guarda esto:", "sabé que:", "sabe que:",
    "anotá esto:", "anota esto:",
]

PREFIJOS_OLVIDAR = [
    "olvidá que", "olvida que", "borrá que", "borra que",
]

PREFIJOS_CONSULTAR = [
    "qué sabés de mí", "que sabes de mi", "qué recordás de mí", "que recordas de mi",
    "qué sabés sobre mí", "que sabes sobre mi", "mostrá tu memoria", "mostra tu memoria",
]

# Frases que NO deben activar el comando de memoria aunque contengan palabras parecidas
EXCEPCIONES_MEMORIA = [
    "de mi familia", "de mi trabajo", "de mi proyecto", "de mi casa", "de mi vida",
    "sobre mi familia", "sobre mi trabajo", "sobre mi proyecto",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS memoria_datos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    dato          TEXT NOT NULL,
    categoria     TEXT NOT NULL DEFAULT 'general',
    fecha_creado  TEXT NOT NULL,
    vencimiento   TEXT,
    ttl_horas     INTEGER,
    activo        INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_memoria_categoria ON memoria_datos(categoria);
CREATE INDEX IF NOT EXISTS idx_memoria_vencimiento ON memoria_datos(vencimiento);
"""


class MemoriaPersonal:
    def __init__(self):
        MEM_DIR.mkdir(parents=True, exist_ok=True)
        if USAR_SQLITE:
            self._init_sqlite()
        else:
            self.datos = self._cargar_json()

    # ---------- Backend SQLite ----------

    def _init_sqlite(self):
        self._conn = sqlite3.connect(str(DB_FILE))
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def _fila_a_dict(self, fila) -> Dict:
        d = {
            "id": fila[0],
            "dato": fila[1],
            "categoria": fila[2],
            "fecha": fila[3],
        }
        if fila[4]:  # vencimiento
            d["vencimiento"] = fila[4]
            d["ttl_horas"] = fila[5]
        return d

    def _todos_activos_sqlite(self) -> List[Dict]:
        cur = self._conn.execute(
            "SELECT id, dato, categoria, fecha_creado, vencimiento, ttl_horas "
            "FROM memoria_datos WHERE activo = 1 ORDER BY id"
        )
        return [self._fila_a_dict(f) for f in cur.fetchall()]

    # ---------- Backend JSON (legado, solo si MEMORIA_SQL=false) ----------

    def _cargar_json(self) -> List[Dict]:
        if MEM_FILE.exists():
            try:
                with open(MEM_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _guardar_json(self):
        with open(MEM_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.datos, f, ensure_ascii=False, indent=2)

    # ---------- Interfaz pública (idéntica a la versión original) ----------

    def agregar(self, dato: str, categoria: str = "general") -> str:
        """Guarda un nuevo dato en la memoria."""
        dato_lower = dato.lower()
        if any(w in dato_lower for w in ['gusta', 'prefiero', 'prefiere', 'favorito']):
            categoria = "preferencias"
        elif any(w in dato_lower for w in ['trabajo', 'proyecto', 'empresa', 'negocio']):
            categoria = "trabajo"
        elif any(w in dato_lower for w in ['cumpleaños', 'naci', 'edad', 'años']):
            categoria = "personal"
        elif any(w in dato_lower for w in ['contra', 'pass', 'clave', 'token', 'api']):
            categoria = "privado"

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if USAR_SQLITE:
            self._conn.execute(
                "INSERT INTO memoria_datos (dato, categoria, fecha_creado) VALUES (?, ?, ?)",
                (dato.strip(), categoria, fecha),
            )
            self._conn.commit()
        else:
            entrada = {
                "id": len(self.datos) + 1,
                "dato": dato.strip(),
                "categoria": categoria,
                "fecha": fecha,
            }
            self.datos.append(entrada)
            self._guardar_json()

        log.info(f"Memoria guardada: [{categoria}] {dato}")
        return f"Entendido, lo voy a recordar: '{dato}'"

    def olvidar(self, fragmento: str) -> str:
        """Elimina entradas que contengan el fragmento (soft-delete en SQLite, borrado real en JSON)."""
        if USAR_SQLITE:
            cur = self._conn.execute(
                "SELECT id FROM memoria_datos WHERE activo = 1 AND dato LIKE ?",
                (f"%{fragmento}%",),
            )
            ids = [r[0] for r in cur.fetchall()]
            if ids:
                self._conn.executemany(
                    "UPDATE memoria_datos SET activo = 0 WHERE id = ?",
                    [(i,) for i in ids],
                )
                self._conn.commit()
            eliminados = len(ids)
        else:
            antes = len(self.datos)
            self.datos = [
                d for d in self.datos
                if fragmento.lower() not in d['dato'].lower()
            ]
            eliminados = antes - len(self.datos)
            self._guardar_json()

        if eliminados > 0:
            return f"Listo, olvide {eliminados} dato(s) relacionado(s) con '{fragmento}'"
        return f"No encontre nada relacionado con '{fragmento}' en mi memoria"

    def buscar_dato(self, terminos: Optional[List[str]] = None, categoria: Optional[str] = None) -> Optional[str]:
        """
        Busca datos que coincidan por palabra clave y/o categoria, de forma
        determinística (sin pasar por el LLM). Retorna el/los dato(s) encontrados,
        o None si no hay coincidencias (para que el llamador decida el fallback).
        """
        if USAR_SQLITE:
            query = "SELECT dato, categoria FROM memoria_datos WHERE activo = 1"
            params: List = []
            if categoria:
                query += " AND categoria = ?"
                params.append(categoria)
            if terminos:
                # Corrección (revisión Kimi): antes se armaba este tramo con
                # f-string. Los valores ya iban parametrizados con "?", pero
                # se prefiere no depender de f-strings ni para la estructura
                # de la consulta, aunque hoy no sea explotable.
                like_clauses = " OR ".join(["dato LIKE ?"] * len(terminos))
                query += " AND (" + like_clauses + ")"
                params.extend(f"%{t}%" for t in terminos)
            cur = self._conn.execute(query, params)
            filas = cur.fetchall()
        else:
            filas = [
                (d['dato'], d['categoria']) for d in self.datos
                if (not categoria or d['categoria'] == categoria)
                and (not terminos or any(t.lower() in d['dato'].lower() for t in terminos))
            ]

        if not filas:
            return None
        if len(filas) == 1:
            return filas[0][0]
        return "\n".join(f"- {f[0]}" for f in filas)

    # Preguntas puntuales que apuntan a UN dato especifico: se responden con
    # buscar_dato() (determinístico, sin LLM), no con el volcado completo.
    # Esta tabla es la solución final al bug del "dónde vivo" — ver
    # /historia/05_memoria_y_conocimiento.md y /tecnico/bugs_famosos.md.
    # Formato: (lista de frases disparadoras, terminos de busqueda, categoria)
    PREGUNTAS_PUNTUALES = [
        (["donde vivo"], ["vivo"], None),
        (["como me llamo"], ["me llamo"], None),
        (["cuantos hijos tengo", "quienes son mis hijos", "quienes son mis hijas"], ["hija"], None),
        (["quien es mi familia", "quienes son mi familia", "contame de mi familia"], None, "familia"),
        (["quien es mi senora", "quien es mi esposa"], ["señora", "esposa"], None),
    ]

    def _responder_pregunta_puntual(self, msg_lower: str) -> Optional[str]:
        """Si el mensaje matchea una pregunta puntual conocida, busca el dato
        exacto sin LLM. Retorna None si no matchea ninguna (para caer al
        volcado completo como fallback)."""
        for frases, terminos, categoria in self.PREGUNTAS_PUNTUALES:
            if any(f in msg_lower for f in frases):
                resultado = self.buscar_dato(terminos=terminos, categoria=categoria)
                if resultado:
                    return resultado
        return None

    def consultar_todo(self) -> str:
        """Retorna un resumen de todo lo que sabe."""
        datos = self._todos_activos_sqlite() if USAR_SQLITE else self.datos

        if not datos:
            return "Todavia no me has ensenado nada. Usa 'aprende esto: [dato]' para ensenarme."

        por_categoria = {}
        for d in datos:
            cat = d['categoria']
            if cat not in por_categoria:
                por_categoria[cat] = []
            por_categoria[cat].append(d['dato'])

        resumen = f"Tengo {len(datos)} dato(s) en mi memoria:\n\n"
        for cat, items in por_categoria.items():
            resumen += f"[{cat.upper()}]\n"
            for item in items:
                resumen += f"  - {item}\n"
            resumen += "\n"
        return resumen.strip()

    def obtener_contexto(self) -> str:
        """Retorna la memoria como contexto para el LLM (últimos 20 datos activos)."""
        datos = self._todos_activos_sqlite() if USAR_SQLITE else self.datos

        if not datos:
            return ""
        ctx = "MEMORIA PERSONAL DE ALEJANDRO:\n"
        for d in datos[-20:]:
            ctx += f"- [{d['categoria']}] {d['dato']}\n"
        return ctx

    def agregar_con_ttl(self, dato: str, horas: int = 24, categoria: str = "temporal") -> str:
        """Guarda un dato que se borra automaticamente despues de X horas."""
        from datetime import timedelta
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")
        vencimiento = (ahora + timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")

        if USAR_SQLITE:
            self._conn.execute(
                "INSERT INTO memoria_datos (dato, categoria, fecha_creado, vencimiento, ttl_horas) "
                "VALUES (?, ?, ?, ?, ?)",
                (dato.strip(), categoria, fecha, vencimiento, horas),
            )
            self._conn.commit()
        else:
            entrada = {
                "id": len(self.datos) + 1,
                "dato": dato.strip(),
                "categoria": categoria,
                "fecha": fecha,
                "vencimiento": vencimiento,
                "ttl_horas": horas,
            }
            self.datos.append(entrada)
            self._guardar_json()

        log.info(f"Dato temporal guardado, vence en {horas}h: {dato}")
        return f"Guardado por {horas} horas (vence: {vencimiento}): '{dato}'"

    def limpiar_expirados(self) -> int:
        """Elimina datos TTL vencidos. Retorna cuantos elimino."""
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if USAR_SQLITE:
            cur = self._conn.execute(
                "SELECT id FROM memoria_datos WHERE activo = 1 "
                "AND vencimiento IS NOT NULL AND vencimiento <= ?",
                (ahora,),
            )
            ids = [r[0] for r in cur.fetchall()]
            if ids:
                self._conn.executemany(
                    "UPDATE memoria_datos SET activo = 0 WHERE id = ?",
                    [(i,) for i in ids],
                )
                self._conn.commit()
                log.info(f"Eliminados {len(ids)} datos TTL expirados")
            return len(ids)
        else:
            antes = len(self.datos)
            self.datos = [
                d for d in self.datos
                if not d.get("vencimiento") or d["vencimiento"] > ahora
            ]
            eliminados = antes - len(self.datos)
            if eliminados > 0:
                self._guardar_json()
                log.info(f"Eliminados {eliminados} datos TTL expirados")
            return eliminados

    def exportar(self) -> str:
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        export_path = BASE_DIR / f"memoria_export_{fecha}.json"
        datos = self._todos_activos_sqlite() if USAR_SQLITE else self.datos
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return f"Memoria exportada a: {export_path} ({len(datos)} datos)"

    def importar(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.exists():
            return f"Archivo no encontrado: {filepath}"
        try:
            with open(path, encoding="utf-8") as f:
                nuevos = json.load(f)
        except Exception as e:
            return f"Error al importar: {e}"

        datos_actuales = self._todos_activos_sqlite() if USAR_SQLITE else self.datos
        existentes = {d["dato"] for d in datos_actuales}
        agregados = 0

        # Corrección (revisión Kimi): los INSERT de SQLite antes se hacían
        # uno por uno en el loop, sin transacción, con un solo commit() al
        # final. Si el import fallaba a mitad de camino, quedaban datos
        # parciales sin forma limpia de deshacerlos. "with self._conn:" abre
        # una transacción que hace commit si todo el bloque termina bien, o
        # rollback automático si algo lanza una excepción en el medio.
        if USAR_SQLITE:
            with self._conn:
                for d in nuevos:
                    if d["dato"] not in existentes:
                        fecha = d.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        self._conn.execute(
                            "INSERT INTO memoria_datos (dato, categoria, fecha_creado, vencimiento, ttl_horas) "
                            "VALUES (?, ?, ?, ?, ?)",
                            (d["dato"], d.get("categoria", "general"), fecha,
                             d.get("vencimiento"), d.get("ttl_horas")),
                        )
                        agregados += 1
        else:
            for d in nuevos:
                if d["dato"] not in existentes:
                    self.datos.append(d)
                    agregados += 1
            self._guardar_json()

        return f"Importados {agregados} datos nuevos (ignorados {len(nuevos) - agregados} duplicados)."

    def procesar_mensaje(self, mensaje: str) -> Optional[str]:
        """
        Detecta si el mensaje es un comando de memoria.
        Retorna la respuesta si es un comando, None si es pregunta normal.
        """
        msg_lower = mensaje.lower().strip()

        import re
        match_ttl = re.search(r'olvida(?:r)? en (\d+) hora', msg_lower)
        if match_ttl:
            horas = int(match_ttl.group(1))
            dato = mensaje
            for p in ["recorda que", "recordá que", "guarda que", "guardá que",
                      "recorda esto:", "recordá esto:", "aprende esto:", "aprendé esto:"]:
                dato = dato.lower().replace(p, "").strip()
            dato = re.sub(r',?\s*olvida(?:r)? en \d+ hora[s]?', "", dato).strip()
            if dato:
                return self.agregar_con_ttl(dato, horas=horas)

        for prefijo in PREFIJOS_APRENDER:
            if msg_lower.startswith(prefijo):
                dato = mensaje[len(prefijo):].strip()
                if dato:
                    return self.agregar(dato)
                return "Que queres que aprenda? Escribi: 'aprende esto: [el dato]'"

        for prefijo in PREFIJOS_OLVIDAR:
            if msg_lower.startswith(prefijo):
                fragmento = mensaje[len(prefijo):].strip()
                if fragmento:
                    return self.olvidar(fragmento)

        for prefijo in PREFIJOS_CONSULTAR:
            if prefijo in msg_lower:
                es_excepcion = any(exc in msg_lower for exc in EXCEPCIONES_MEMORIA)
                if not es_excepcion:
                    return self.consultar_todo()

        # Nota (revisión Kimi): había un segundo bloque acá que repetía el
        # mismo match_ttl de más arriba, con una lista de prefijos más
        # angosta. Se eliminó por redundante: el primer bloque (arriba en
        # esta función) ya cubre el mismo patrón con una lista de prefijos
        # más amplia y siempre corre primero; el segundo bloque solo era
        # alcanzable en un caso borde degenerado (mensaje sin contenido real
        # después de sacar el prefijo) y ahí terminaba guardando una entrada
        # casi vacía.

        for p in ["recorda que", "recordá que", "guarda que", "guardá que"]:
            if msg_lower.startswith(p):
                dato = mensaje[len(p):].strip()
                if dato:
                    return self.agregar(dato)

        if any(p in msg_lower for p in [
            "que sabes de mi", "que sabés de mí", "que sabes de mi familia", "contame de mi", "qué sabes de mí",
            "quien es mi familia", "quienes son mi familia", "quienes son mis hijos", "quienes son mis hijas",
            "quien es mi senora", "quien es mi esposa", "cuantos hijos tengo", "donde vivo", "como me llamo",
            "que sabes de mi vida", "que sabes sobre mi", "que recordas de mi", "que aprendiste de mi", "que sabe de mi",
        ]):
            eliminados = self.limpiar_expirados()
            if eliminados:
                pass

            # Primero intentar respuesta puntual y exacta (sin LLM). Si la
            # pregunta es genuinamente puntual y hay dato, responde solo eso.
            respuesta_puntual = self._responder_pregunta_puntual(msg_lower)
            if respuesta_puntual:
                return respuesta_puntual

            # Si no matcheo ninguna pregunta puntual (o no encontro el dato),
            # cae al volcado completo como venia funcionando.
            return self.consultar_todo()

        if any(w in msg_lower for w in ['exporta mi memoria', 'exportar memoria', 'hacer backup de memoria']):
            return self.exportar()

        if msg_lower.startswith('importa memoria desde'):
            filepath = mensaje[len('importa memoria desde'):].strip()
            return self.importar(filepath)

        return None


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    print(f"Backend activo: {'SQLite' if USAR_SQLITE else 'JSON (legado)'}")
    mem = MemoriaPersonal()

    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        resultado = mem.procesar_mensaje(cmd)
        if resultado:
            print(resultado)
        else:
            print("No es un comando de memoria.")
            print("Prueba: python memoria.py 'aprende esto: me gusta el cafe'")
    else:
        print("Uso:")
        print("  python memoria.py 'aprende esto: [dato]'")
        print("  python memoria.py 'que sabes de mi'")
        print("  python memoria.py 'olvida que [fragmento]'")
