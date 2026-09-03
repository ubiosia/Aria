"""
test_enrutador.py — tests de config_dominios.py, el enrutador real de ARIA.

Puro Python: sin Ollama, sin ChromaDB, sin red. Corre en segundos.

Cada test protege un caso real documentado en este repositorio, no un
caso genérico — misma disciplina de citar fuentes que el resto del
proyecto. Los resultados esperados de cada caso se confirmaron corriendo
detectar_dominio() en vivo antes de escribir el test, no se asumieron.

Uso:
    pytest tests/test_enrutador.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "codigo"))

from config_dominios import detectar_dominio, _detectar_dominio_interno


# ---------------------------------------------------------------------
# Un caso por dominio real (trading, tecnología, IA, programación,
# personal), más el fallback genérico.
# ---------------------------------------------------------------------

def test_dominio_trading_por_palabra_suelta():
    """"btc" es una palabra suelta del dominio trading (ver DOMINIOS en
    config_dominios.py). Caso base, sin ambigüedad."""
    assert detectar_dominio("cual es el precio del btc") == "trading"


def test_dominio_tecnologia():
    """"docker" es palabra clave de tecnologia. Caso base."""
    assert detectar_dominio("como instalo docker") == "tecnologia"


def test_dominio_ia():
    """"modelo de lenguaje" es frase clave de ia — la misma pregunta que
    usa ingesta_minima.py como ejemplo de prueba del RAG (Fase 3.1),
    verificada acá también para que un cambio futuro en config_dominios.py
    no rompa esa recomendación sin que un test lo note."""
    assert detectar_dominio("que es un modelo de lenguaje") == "ia"


def test_dominio_programacion():
    """"arbol binario" es frase clave de programacion."""
    assert detectar_dominio("que es un arbol binario") == "programacion"


def test_dominio_personal_saludo():
    """"hola" es palabra clave de personal — no es fallback, es un match
    real (ver test_fallback_no_se_activa_con_match_real más abajo)."""
    assert detectar_dominio("hola como estas") == "personal"


def test_fallback_generico_sin_ningun_keyword():
    """Una pregunta sin ningún keyword conocido cae al dominio "personal"
    por defecto (fallback) — no a un error ni a None."""
    assert detectar_dominio("xyz asdf qwerty sin ningun keyword conocido") == "personal"


# ---------------------------------------------------------------------
# Route shadowing por especificidad: "modo trading" (frase específica,
# dominio personal) le gana a la palabra suelta "trading" (dominio
# trading), aunque trading tenga prioridad numérica mayor — ver el
# docstring de _detectar_dominio_interno() en config_dominios.py, y el
# patrón general de "route shadowing" documentado en
# /tecnico/bugs_famosos.md (el bug del precio del oro, mismo nombre de
# patrón aunque en otro archivo del sistema real).
# ---------------------------------------------------------------------

def test_especificidad_modo_trading_gana_a_trading_suelto():
    """"modo trading" (2 palabras, dominio personal) debe ganarle a
    "trading" (1 palabra, dominio trading) por la regla de especificidad
    — si esto alguna vez devuelve "trading", la regla de desempate se
    rompió."""
    assert detectar_dominio("modo trading") == "personal"


def test_trading_metodologia_sabri_sigue_siendo_trading():
    """Control: una pregunta de trading real (sin la frase "modo X") sigue
    yendo a trading — confirma que la corrección de especificidad de
    arriba no sobre-corrigió el caso normal."""
    assert detectar_dominio("segun sabri que es la zona ote") == "trading"


# ---------------------------------------------------------------------
# Negaciones de investigación (Fix Sesión 119, ver el comentario de
# config_dominios.py sobre este mismo fix): "buscar" no debe disparar el
# dominio investigacion cuando el usuario niega explícitamente la
# búsqueda.
# ---------------------------------------------------------------------

def test_negacion_sin_buscar_no_activa_investigacion():
    """Regresión Sesión 119: "sin buscar nada nuevo" no debe rutear a
    investigacion. Cae a personal (ningún otro keyword matchea)."""
    assert detectar_dominio("sin buscar nada nuevo, que opinas") == "personal"


def test_negacion_no_busques_no_activa_investigacion():
    """Regresión Sesión 119: "no busques" es la otra frase de negación
    citada explícitamente en el comentario del fix."""
    assert detectar_dominio("no busques mas, con lo que tenemos alcanza") == "personal"


def test_busca_sin_negacion_si_activa_investigacion():
    """Control: sin ninguna negación cerca, "busca" sigue activando
    investigacion normalmente — confirma que el fix de negación de
    Sesión 119 no rompió el caso positivo."""
    assert detectar_dominio("busca informacion sobre el tema") == "investigacion"


# ---------------------------------------------------------------------
# Dominio memoria: las preguntas puntuales de memoria personal (mismo
# patrón que memoria.py, PREGUNTAS_PUNTUALES, en /codigo/memoria.py)
# deben rutear al dominio memoria, no a personal ni a ningún otro.
# ---------------------------------------------------------------------

def test_memoria_donde_vivo():
    """"donde vivo" es una de las PREGUNTAS_PUNTUALES de memoria.py — acá
    se confirma que el enrutador la manda al dominio memoria, condición
    necesaria para que memoria.py llegue a responderla."""
    assert detectar_dominio("donde vivo") == "memoria"


def test_memoria_que_sabes_de_mi():
    """Otra frase disparadora real de memoria.py (PREFIJOS_CONSULTAR)."""
    assert detectar_dominio("que sabes de mi") == "memoria"


# ---------------------------------------------------------------------
# Flag fue_fallback (Sesión 55: "correccion del bug de fallback personal
# pisado por el semantico" — ver el docstring de detectar_dominio()).
# _detectar_dominio_interno() es la función interna que expone esta
# distinción; detectar_dominio() es el wrapper público que la oculta.
# ---------------------------------------------------------------------

def test_fallback_flag_true_sin_match_real():
    """Sin ningún keyword match, fue_fallback debe ser True — así es como
    el resto del sistema distingue "no encontré nada, uso personal por
    default" de "personal fue un match real", que es justo lo que la
    Sesión 55 corrigió."""
    _dominio, fue_fallback, _esp = _detectar_dominio_interno(
        "xyz asdf qwerty sin ningun keyword conocido"
    )
    assert fue_fallback is True


def test_fallback_flag_false_con_match_real():
    """Con un keyword real de personal ("hola"), fue_fallback debe ser
    False — es un match real, no un default. Si esto alguna vez da True,
    el bug de la Sesión 55 volvió."""
    _dominio, fue_fallback, _esp = _detectar_dominio_interno("hola como estas")
    assert fue_fallback is False
