"""
test_memoria.py — tests de memoria.py, el sistema de memoria personal real
de ARIA (ver codigo/memoria.py).

Puro Python + SQLite (stdlib). Sin red, sin Ollama, sin ChromaDB. Corre en
segundos, misma disciplina que tests/test_enrutador.py: cada test cita qué
caso real protege.

Aislamiento: memoria.py calcula BASE_DIR/MEM_DIR/DB_FILE/MEM_FILE/
USAR_SQLITE como constantes de módulo en el momento del import, a partir
de variables de entorno (ARIA_BASE_DIR, MEMORIA_SQL). Para no tocar nunca
la memoria real del usuario ni depender del orden de ejecución de los
tests, cada test usa un fixture que redirige esas constantes de módulo a
una carpeta temporal (tmp_path de pytest) con monkeypatch.setattr() antes
de instanciar MemoriaPersonal() — no se mockea ninguna lógica de negocio,
solo la ubicación de los archivos.

Uso:
    pytest tests/test_memoria.py -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "codigo"))

import memoria as memoria_modulo  # noqa: E402  (import despues del sys.path.insert, necesario)


def _redirigir_a_tmp(monkeypatch, tmp_path, usar_sqlite: bool):
    """Apunta las constantes de módulo de memoria.py a tmp_path, con el
    backend indicado. Nunca toca ~/asistente ni ninguna carpeta real."""
    mem_dir = tmp_path / "memoria_personal"
    monkeypatch.setattr(memoria_modulo, "BASE_DIR", tmp_path)
    monkeypatch.setattr(memoria_modulo, "MEM_DIR", mem_dir)
    monkeypatch.setattr(memoria_modulo, "DB_FILE", mem_dir / "memoria.db")
    monkeypatch.setattr(memoria_modulo, "MEM_FILE", mem_dir / "conocimiento.json")
    monkeypatch.setattr(memoria_modulo, "USAR_SQLITE", usar_sqlite)


@pytest.fixture
def memoria_sqlite(tmp_path, monkeypatch):
    """MemoriaPersonal real, backend SQLite (el que usa ARIA por defecto,
    MEMORIA_SQL=true), aislada en una carpeta temporal."""
    _redirigir_a_tmp(monkeypatch, tmp_path, usar_sqlite=True)
    return memoria_modulo.MemoriaPersonal()


@pytest.fixture
def memoria_json(tmp_path, monkeypatch):
    """MemoriaPersonal real, backend JSON legado (MEMORIA_SQL=false, el
    flag de emergencia documentado en el docstring de memoria.py)."""
    _redirigir_a_tmp(monkeypatch, tmp_path, usar_sqlite=False)
    return memoria_modulo.MemoriaPersonal()


# ---------------------------------------------------------------------
# Agregar un dato y recuperarlo (caso base, backend SQLite).
# ---------------------------------------------------------------------

def test_agregar_y_recuperar_con_buscar_dato(memoria_sqlite):
    """Un dato agregado con agregar() tiene que aparecer al buscarlo por
    termino con buscar_dato() — el flujo mas basico de todo el sistema."""
    memoria_sqlite.agregar("el cielo es celeste")
    resultado = memoria_sqlite.buscar_dato(terminos=["celeste"])
    assert resultado == "el cielo es celeste"


def test_agregar_aparece_en_consultar_todo(memoria_sqlite):
    """Ademas de buscar_dato(), el dato agregado tiene que aparecer en el
    volcado completo de consultar_todo() — confirma que agregar() persiste
    de verdad, no solo en memoria de proceso."""
    memoria_sqlite.agregar("el cielo es celeste")
    resumen = memoria_sqlite.consultar_todo()
    assert "el cielo es celeste" in resumen


# ---------------------------------------------------------------------
# Olvidar: soft-delete en SQLite. El dato no debe aparecer en busquedas
# activas, pero la fila sigue existiendo en la tabla con activo=0 — es
# la diferencia explicita que documenta el docstring de olvidar() en
# memoria.py ("soft-delete en SQLite, borrado real en JSON").
# ---------------------------------------------------------------------

def test_olvidar_no_aparece_en_busquedas_activas(memoria_sqlite):
    """Despues de olvidar(), buscar_dato() no debe encontrar el dato —
    aunque el borrado sea "soft" a nivel de base de datos, el
    comportamiento visible tiene que ser el de un dato ausente."""
    memoria_sqlite.agregar("dato temporal para borrar")
    respuesta = memoria_sqlite.olvidar("temporal")
    assert "olvide 1" in respuesta.lower()
    assert memoria_sqlite.buscar_dato(terminos=["temporal"]) is None


def test_olvidar_es_soft_delete_no_borrado_real(memoria_sqlite):
    """Verificacion directa contra SQLite (no solo contra la interfaz
    publica): la fila sigue en memoria_datos, marcada activo=0 — no se
    borro la fila. Si esto alguna vez encuentra 0 filas, olvidar() paso a
    ser un DELETE real, lo cual contradice el docstring del metodo."""
    memoria_sqlite.agregar("dato temporal para borrar")
    memoria_sqlite.olvidar("temporal")
    fila = memoria_sqlite._conn.execute(
        "SELECT activo FROM memoria_datos WHERE dato LIKE ?", ("%temporal%",)
    ).fetchone()
    assert fila is not None, "la fila no deberia haberse borrado de verdad"
    assert fila[0] == 0


# ---------------------------------------------------------------------
# buscar_dato(): un caso exitoso, un caso sin resultados.
# ---------------------------------------------------------------------

def test_buscar_dato_exitoso(memoria_sqlite):
    """Caso base ya cubierto arriba, repetido aqui con un dato distinto
    para dejar el contraste explicito con el caso sin resultados de
    abajo."""
    memoria_sqlite.agregar("me gusta el cafe")
    assert memoria_sqlite.buscar_dato(terminos=["cafe"]) == "me gusta el cafe"


def test_buscar_dato_sin_resultados_devuelve_none(memoria_sqlite):
    """Sin ningun dato que matchee el termino, buscar_dato() tiene que
    devolver None explicito — no una lista vacia, no una excepcion — para
    que el llamador (_responder_pregunta_puntual, procesar_mensaje) pueda
    decidir el fallback (ver docstring de buscar_dato() en memoria.py)."""
    memoria_sqlite.agregar("me gusta el cafe")
    assert memoria_sqlite.buscar_dato(terminos=["termino_que_no_existe"]) is None


# ---------------------------------------------------------------------
# _responder_pregunta_puntual(): el fix del bug "donde vivo" (Capitulo 5,
# ver /historia/05_memoria_y_conocimiento.md y /tecnico/bugs_famosos.md,
# "El volcado de memoria personal"). Antes del fix, cualquier pregunta de
# memoria devolvia el volcado completo (consultar_todo()); despues del
# fix, las preguntas puntuales de PREGUNTAS_PUNTUALES devuelven solo el
# dato exacto.
# ---------------------------------------------------------------------

def test_pregunta_puntual_donde_vivo_responde_solo_ese_dato(memoria_sqlite):
    """Regresion del bug real: con datos de "vivo" y otro dato no
    relacionado en memoria, _responder_pregunta_puntual("donde vivo")
    tiene que devolver solo el dato de "vivo", no el volcado completo con
    el resto de la memoria mezclado."""
    memoria_sqlite.agregar("vivo en Buenos Aires")
    memoria_sqlite.agregar("me gusta el mate")

    respuesta = memoria_sqlite._responder_pregunta_puntual("donde vivo")

    assert respuesta == "vivo en Buenos Aires"
    assert "Tengo" not in respuesta  # "Tengo N dato(s) en mi memoria" es el encabezado del volcado completo
    assert "mate" not in respuesta


def test_procesar_mensaje_donde_vivo_no_vuelca_todo(memoria_sqlite):
    """Mismo caso que arriba pero a traves de la interfaz publica real
    (procesar_mensaje, la que usan los handlers) en vez del metodo interno
    — confirma que el fix esta conectado de punta a punta, no solo que el
    metodo interno funciona aislado."""
    memoria_sqlite.agregar("vivo en Buenos Aires")
    memoria_sqlite.agregar("me gusta el mate")

    respuesta = memoria_sqlite.procesar_mensaje("donde vivo")

    assert respuesta == "vivo en Buenos Aires"
    assert "Tengo" not in respuesta


def test_pregunta_puntual_sin_dato_cae_a_volcado_completo(memoria_sqlite):
    """Control: si la pregunta es puntual pero no hay ningun dato de
    "vivo" guardado, _responder_pregunta_puntual() devuelve None (ver su
    docstring: "para caer al volcado completo como fallback") — confirma
    que el caso de arriba no funciona por casualidad."""
    memoria_sqlite.agregar("me gusta el mate")
    assert memoria_sqlite._responder_pregunta_puntual("donde vivo") is None


# ---------------------------------------------------------------------
# Fallback JSON: con MEMORIA_SQL desactivado (backend alternativo, el
# flag de emergencia documentado en memoria.py), el caso basico de
# agregar/buscar tiene que funcionar igual que con SQLite.
# ---------------------------------------------------------------------

def test_backend_json_agregar_y_buscar(memoria_json):
    """Mismo caso base que test_agregar_y_recuperar_con_buscar_dato pero
    con USAR_SQLITE=False — confirma que la interfaz publica es
    identica entre los dos backends, tal como documenta el docstring de
    memoria.py ("interfaz publica IDENTICA a la version JSON original")."""
    memoria_json.agregar("dato guardado en json")
    assert memoria_json.buscar_dato(terminos=["json"]) == "dato guardado en json"


def test_backend_json_persiste_en_disco(memoria_json):
    """Ademas de funcionar en memoria de proceso, el backend JSON tiene
    que escribir el archivo real en disco (MEM_FILE) — si esto fallara,
    el dato se perderia al reiniciar el proceso."""
    memoria_json.agregar("dato guardado en json")
    assert memoria_modulo.MEM_FILE.exists()


# ---------------------------------------------------------------------
# importar(): la transaccion (correccion Kimi, Fase 3.1/"with self._conn:")
# — una importacion que falla a mitad de camino no debe dejar datos
# parciales. Se prueba forzando una excepcion real (un registro sin la
# clave "dato", que memoria.py accede de forma directa con d["dato"]) a
# mitad de una lista con un registro valido antes.
# ---------------------------------------------------------------------

def test_importar_transaccion_no_deja_datos_parciales(memoria_sqlite, tmp_path):
    """Si importar() falla procesando el segundo registro de la lista (le
    falta la clave "dato"), el primer registro -- valido -- tampoco debe
    quedar guardado: la transaccion tiene que hacer rollback completo, no
    guardar lo que llegó a procesar antes del error."""
    import json

    archivo_import = tmp_path / "import_con_error.json"
    archivo_import.write_text(
        json.dumps([
            {"dato": "dato de import valido", "categoria": "general"},
            {"categoria": "registro sin clave dato, deberia romper el import"},
        ]),
        encoding="utf-8",
    )

    with pytest.raises(KeyError):
        memoria_sqlite.importar(str(archivo_import))

    assert memoria_sqlite.buscar_dato(terminos=["import valido"]) is None
    assert memoria_sqlite._todos_activos_sqlite() == []


def test_importar_caso_exitoso_sin_duplicados(memoria_sqlite, tmp_path):
    """Control positivo: un import sin errores agrega los datos nuevos e
    ignora el que ya existia — confirma que el test de arriba no pasa
    porque importar() esta roto en general, sino especificamente por la
    transaccion ante un error."""
    import json

    memoria_sqlite.agregar("dato que ya existia")

    archivo_import = tmp_path / "import_ok.json"
    archivo_import.write_text(
        json.dumps([
            {"dato": "dato que ya existia", "categoria": "general"},
            {"dato": "dato nuevo de import", "categoria": "general"},
        ]),
        encoding="utf-8",
    )

    respuesta = memoria_sqlite.importar(str(archivo_import))

    assert "Importados 1 datos nuevos" in respuesta
    assert memoria_sqlite.buscar_dato(terminos=["dato nuevo de import"]) == "dato nuevo de import"
