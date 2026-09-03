#!/usr/bin/env python3
"""
config_dominios.py — Nucleo de configuracion centralizado para ARIA V7.

Unifica en un solo lugar las reglas de deteccion de dominio que antes
estaban dispersas en orquestador.py (PATRONES), agente_trading.py
(palabras_sabri) y aria_core.py (palabras_no_cache), evitando que
queden desincronizadas entre si (causa de 3 bugs distintos en Sesion 43).

Uso:
    from config_dominios import detectar_dominio
    dominio = detectar_dominio("segun sabri que es la zona ote")
    # -> "trading"

---
Historia detrás de este código: la lista fija de dominios/palabras clave
que este archivo reemplazó es, literalmente, el bug protagonista del
Capítulo 7 (/historia/07_los_bugs_que_ensenaron_mas.md) — "una regla de
negocio importante, viviendo en un solo lugar hardcodeado del código, que
nadie recuerda actualizar cuando el sistema crece". Este módulo es la
corrección de fondo: un único diccionario DOMINIOS, en un único archivo,
en vez de tres copias desincronizadas. Ver también /tecnico/bugs_famosos.md.

Sanitización para este repositorio: se reemplazaron, en la lista de
palabras clave del dominio "personal", los nombres reales de familiares
de Alejandro por marcadores genéricos ([NOMBRE_FAMILIAR_1], etc.) — esa
lista existe para que el router reconozca menciones a la familia del
usuario, y su contenido real no aporta nada a quien lea el código como
material de referencia. El nombre "Alejandro" se mantiene porque ya es
público en el resto de este repositorio. No se modificó ninguna otra
parte del archivo: las palabras clave de trading, tecnología, IA y
programación son términos genéricos del dominio, no datos personales.
"""

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Quita tildes y pasa a minusculas, para comparaciones consistentes."""
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


# Orden de evaluacion: el primer dominio que matchee gana
ORDEN = ["planificador", "aprendizaje", "vision", "noticias", "trading",
         "tecnologia", "ia", "programacion", "investigacion", "razonamiento",
         "memoria", "sistema", "personal"]

DOMINIOS = {
    "planificador": {
        "prioridad": 100,
        "palabras": ["planifica", "quiero lograr", "plan para", "crea un plan",
                     "pasos para", "como empiezo", "mis planes"],
    },
    "aprendizaje": {
        "prioridad": 95,
        "palabras": ["eso estuvo mal", "muy largo", "respuestas son muy",
                     "eres muy", "fuiste muy", "estuvo muy", "fue muy",
                     "muy corto", "demasiado largo", "en el futuro",
                     "para proximas veces", "siempre respondeme",
                     "toma nota de", "aprende de esto", "no me gusto",
                     "mejora eso", "corrige eso"],
    },
    "vision": {
        "prioridad": 90,
        "palabras": ["analiza esta imagen", "analiza este grafico", "que ves en",
                     "describe esta imagen", "lee este grafico", "analiza la captura"],
    },
    "noticias": {
        "prioridad": 85,
        "palabras": ["noticias", "novedades", "noticias de hoy", "que noticias",
                     "que hay", "que paso", "novedades de", "noticias crypto",
                     "noticias bitcoin", "noticias btc", "noticias ethereum",
                     "noticias eth", "noticias tecnologia"],
    },
    "trading": {
        "prioridad": 80,
        "palabras": ["btc", "bitcoin", "eth", "ethereum", "crypto", "cripto",
                     "cotizacion", "binance", "coinmarketcap", "tradingview",
                     "coinglass", "pionex", "bingx", "analiza", "analisis", "analisis tecnico", "impulso virgen", "trading",
                     "posicion", "alerta", "compre", "vendi", "stop loss",
                     "take profit", "rsi", "macd", "ema", "soporte", "resistencia",
                     "vela", "velas", "patron de vela", "patron de velas", "patron alcista", "patron bajista", "tendencia", "sube de", "baja de",
                     "forex", "estructura de mercado", "swing", "swings", "blockchain", "token", "ico", "pib", "inflacion", "politica monetaria", "tipo de cambio", "deuda publica",
                     "cfd", "cfds", "apalancamiento", "margen de garantia", "ingresarios", "villegas", "arango", "velez", "oliver velez",
                     "villahermosa", "psicologia del trader", "psicologia de trading", "psicologico", "psicologicos",
                     "avisame si", "alertame", "registra decision", "registra que",
                     "anota que", "guarda operacion", "cierra decision",
                     "historial de trading", "pnl", "gane", "perdi",
                     # Palabras clave de la metodologia de Sabri (antes en 3 lugares distintos)
                     "sabri", "ote", "zona ote", "fibonacci", "fvg", "fair value gap",
                     "order block", "liquidez", "smart money", "killzone", "killzones",
                     "estructura amd", "amd", "gestion de riesgo", "psicologia del trader",
                     "plan de trading", "confirmacion de entrada", "segun sabri",
                     "segun tus clases", "segun mis clases", "curso de sabri",
                     "equal high", "equal highs", "equal low", "equal lows",
                     "swing high", "swing highs", "swing low", "swing lows",
                          "alexander elder", "john murphy"],
        "usar_rag_sabri": True,
        "modelo_rag": "qwen2.5:7b",
        "excluir_cache": True,
    },
    "tecnologia": {
        "prioridad": 75,
        "palabras": ["python", "linux", "ubuntu", "docker", "git", "github",
                     "bash", "terminal", "codigo", "script", "programacion",
                     "libreria", "paquete", "dependencia", "fastapi", "uvicorn",
                     "gradio", "api", "servidor", "puerto", "proceso", "wsl",
                     "wsl2", "cuda", "nvidia", "vram", "gpu", "symlink", "driver",
                          "kubernetes", "vhdx",
                     "instalar", "instalacion", "configurar", "configuracion",
                     "arquitectura", "modulo", "clase", "funcion", "metodo",
                     "error de python", "error de linux", "como instalo", "como configuro",
                     "que sabes de tecnologia", "sabes de tecnologia",
                     "que sabes sobre tecnologia", "hablame de tecnologia"],
    },
    "ia": {
        "prioridad": 70,
        "palabras": ["inteligencia artificial", "machine learning", "deep learning",
                     "red neuronal", "llm", "modelo de lenguaje", "transformer",
                     "tokens", "contexto", "embedding", "embeddings", "ollama", "llama", "qwen",
                     "mistral", "gemma", "moondream", "nomic", "rag", "vectorstore",
                     "chromadb", "langchain", "reranking", "crossencoder",
                     "fine-tuning", "finetuning", "fine tuning", "lora", "entrenamiento", "dataset",
                     "inferencia", "whisper", "piper", "edge-tts", "tts", "stt",
                     "voz ia", "sintesis de voz", "agente ia", "agente de ia",
                     "como funciona la ia", "que es el rag", "quantization", "gguf",
                     "cupy", "temperatura del modelo", "system prompt",
                     "que sabes de ia", "que sabes de inteligencia artificial",
                     "sabes de ia", "que sabes sobre ia", "hablame de ia",
                     "hablame de inteligencia artificial"],
    },
    "programacion": {
        "prioridad": 72,
        "palabras": ["algoritmo", "algoritmos", "estructura de datos",
                     "estructuras de datos", "python", "javascript", "java",
                     "typescript", "c++", "sql", "base de datos", "bases de datos",
                     "sqlite", "mysql", "postgresql", "php", "flask", "vue",
                     "node", "nodejs", "node.js", "git", "pseudocodigo", "un pseudocodigo", "el pseudocodigo", "es pseudocodigo",
                     "diagrama de flujo", "funcion recursiva", "recursividad", "complejidad algoritmica",
                     "big o", "arbol binario", "lista enlazada", "pila", "cola",
                     "programacion orientada a objetos", "poo", "herencia",
                     "polimorfismo", "encapsulamiento", "patron de diseno",
                     "patrones de diseno", "domain driven design", "ddd", "patron nulo", "null object", "objeto nulo", "clean code", "codigo limpio",
                     "que sabes de programacion", "sabes de programacion",
                     "hablame de programacion", "libro de programacion"],
    },
    "investigacion": {
        "prioridad": 65,
        "palabras": ["http://", "https://", "busca", "buscar", "busqueda",
                     "investiga", "googlea", "youtube", "video", "transcripcion",
                     "analiza este video", "clase de trading", "documento", "pdf",
                     "archivo", "indexa", "ingesta", "noticias de", "articulo sobre",
                     "que dice"],
    },
    "memoria": {
        "prioridad": 55,
        "palabras": ["recorda", "recordame", "aprende", "olvida", "memoria", "sabes de mi",
                     "recordatorio", "recordatorios", "pendiente",
                     "exporta mi memoria", "importa memoria", "que sabes de mi",
                     "que recordas de mi", "que aprendiste de mi",
                     "que sabes sobre mi", "que sabe de mi", "quienes son mi familia",
                     "quien es mi familia", "contame de mi familia",
                     "quienes son mis hijos", "quienes son mis hijas",
                     "quien es mi senora", "quien es mi esposa",
                     "cuantos hijos tengo", "donde vivo", "como me llamo",
                     "que sabes de mi vida"],
    },
    "sistema": {
        "prioridad": 50,
        "palabras": ["estado del sistema", "estado de aria", "diagnostico",
                     "aria diagnostico", "como estas aria", "estado aria",
                     "cuanto es", "calculame", "que hora", "hora actual", "que dia es", "que dia es hoy",
                     "fecha de hoy", "exporta la conversacion", "exportar pdf",
                     "archivos recientes", "indexa documentos",
                     "al cuadrado", "la mitad de", "el doble de"],
    },
    "razonamiento": {
        "prioridad": 60,
        "palabras": ["razona", "analiza paso a paso", "explica paso a paso", "explica por que",
                     "que concluis", "pros y contras", "ventajas y desventajas",
                     "deberia", "conviene", "piensa", "reflexiona", "evalua", "decision", "cuantas me quedan", "cuanto me queda"],
    },
    "personal": {
        "prioridad": 10,
        # Nombres de familiares reemplazados por marcadores genéricos
        # para este repositorio público (ver nota de sanitización arriba).
        "palabras": ["resumen del dia", "resumen diario", "que hice hoy",
                     "modo jarvis", "modo trading", "modo creativo", "modo normal",
                     "como vas", "hola", "buenas", "buenos", "buenas noches",
                     "buenas tardes", "mi familia",
                     "[NOMBRE_FAMILIAR_1]", "[NOMBRE_FAMILIAR_2]", "[NOMBRE_FAMILIAR_3]",
                     "[NOMBRE_FAMILIAR_4]", "[NOMBRE_FAMILIAR_5]", "[NOMBRE_FAMILIAR_6]",
                     "[NOMBRE_FAMILIAR_7]", "[NOMBRE_FAMILIAR_8]",
                     "sobrinos", "nietos", "hermanas"],
    },
}


def _matchea(msg_normalizado: str, palabra: str) -> bool:
    """Compara con limite de palabra real, para evitar falsos positivos
    (ej. que 'ana' matchee dentro de 'analisis'). Usa lookaround en vez
    de \b para que funcione bien con palabras que terminan en simbolos
    no alfanumericos (ej. 'c++'), donde \b no aplica correctamente."""
    palabra_norm = normalizar(palabra)
    patron = r'(?<![a-z0-9])' + re.escape(palabra_norm) + r'(?![a-z0-9])'
    return bool(re.search(patron, msg_normalizado))


def detectar_dominio(pregunta: str, verbose: bool = False) -> str:
    """
    Detecta el dominio/agente correcto para una pregunta.
    Wrapper de compatibilidad: ver _detectar_dominio_interno() para la
    logica real y para saber si el resultado fue un match real o el
    fallback por defecto (necesario para la Sesion 55, correccion del
    bug de fallback personal pisado por el semantico).
    """
    dominio, _fue_fallback, _especificidad = _detectar_dominio_interno(pregunta, verbose=verbose)
    return dominio


def _detectar_dominio_interno(pregunta: str, verbose: bool = False):
    """
    Logica real de deteccion de dominio. Ver detectar_dominio() para
    el wrapper publico usado en el resto del codigo.

    Regla de desempate: las frases mas especificas (mas palabras)
    ganan a las palabras sueltas genericas, sin importar la prioridad
    del dominio. Por ejemplo "modo trading" (frase especifica, dominio
    personal) le gana a la palabra suelta "trading" (dominio trading),
    aunque trading tenga prioridad numerica mayor. Solo cuando dos
    matches tienen la MISMA especificidad (misma cantidad de palabras)
    se usa la prioridad numerica del dominio como desempate.

    Retorna (nombre_dominio, fue_fallback). fue_fallback=True cuando
    no hubo NINGUN keyword match y se devolvio 'personal' por defecto.
    Si verbose=True, imprime un log estructurado de la decision.
    """
    import time
    _inicio = time.time()
    msg = normalizar(pregunta)

    # Armamos una lista plana de todos los (dominio, palabra, prioridad)
    # y la ordenamos por especificidad (cant. de palabras) desc,
    # luego por prioridad del dominio desc.
    candidatos = []
    for nombre, config in DOMINIOS.items():
        prioridad = config.get("prioridad", 0)
        for palabra in config["palabras"]:
            especificidad = len(palabra.split())
            candidatos.append((especificidad, prioridad, nombre, palabra))

    candidatos.sort(key=lambda c: (-c[0], -c[1]))

    for especificidad, prioridad, nombre, palabra in candidatos:
        if _matchea(msg, palabra):
            # Fix Sesion 119: "buscar" (keyword de investigacion) disparaba
            # incluso cuando el usuario NEGABA explicitamente la busqueda
            # (ej. "sin buscar nada nuevo", "no busques", pregunta de
            # seguimiento pidiendo razonar sobre datos ya dados). Mismo
            # patron ya corregido hoy para "precio" y "calcula" en otros
            # archivos. Si hay negacion cerca, no cortar aca -- seguir
            # probando el siguiente candidato de la lista.
            if nombre == "investigacion" and palabra in ("busca", "buscar", "busqueda") and \
                    any(neg in msg for neg in ["sin buscar", "no busques", "no busca",
                                                 "sin necesidad de buscar", "no necesito que busques"]):
                continue
            _tiempo_ms = (time.time() - _inicio) * 1000
            if verbose:
                print(f"[ROUTE] {pregunta!r} -> dominio={nombre} "
                      f"palabra_match={palabra!r} especificidad={especificidad} "
                      f"prioridad={prioridad} tiempo={_tiempo_ms:.2f}ms")
            import logging
            logging.getLogger("config_dominios").info(
                f"[ROUTE] pregunta={pregunta!r} dominio={nombre} "
                f"palabra_match={palabra!r} especificidad={especificidad} "
                f"prioridad={prioridad} tiempo_ms={_tiempo_ms:.2f}"
            )
            return nombre, False, especificidad

    _tiempo_ms = (time.time() - _inicio) * 1000
    if verbose:
        print(f"[ROUTE] {pregunta!r} -> dominio=personal (fallback) tiempo={_tiempo_ms:.2f}ms")
    import logging
    logging.getLogger("config_dominios").info(
        f"[ROUTE] pregunta={pregunta!r} dominio=personal (fallback) tiempo_ms={_tiempo_ms:.2f}"
    )
    return "personal", True, 0


def es_pregunta_sabri(pregunta: str) -> bool:
    """
    Uso especifico para agente_trading.py: decide si ademas de ser
    categoria 'trading', la pregunta es especificamente de la
    metodologia de Sabri (para activar el RAG con qwen2.5:7b).
    """
    msg = normalizar(pregunta)
    palabras_sabri = [
        "sabri", "ote", "zona ote", "fibonacci", "fvg", "fair value gap",
        "order block", "liquidez", "smart money", "killzone", "killzones",
        "estructura amd", "amd", "gestion de riesgo", "psicologia del trader",
        "plan de trading", "confirmacion de entrada", "segun sabri",
        "segun tus clases", "segun mis clases", "curso de sabri",
        "equal high", "equal highs", "equal low", "equal lows",
        "swing high", "swing highs", "swing low", "swing lows",
    ]
    return any(_matchea(msg, p) for p in palabras_sabri)


def excluir_de_cache(pregunta: str) -> bool:
    """
    Uso especifico para aria_core.py: decide si la pregunta NO debe
    servirse desde cache (por ejemplo, preguntas de Sabri, cuyo
    contenido puede cambiar si se actualiza el RAG).
    """
    dominio = detectar_dominio(pregunta)
    if dominio == "trading" and es_pregunta_sabri(pregunta):
        return True
    if dominio in ("tecnologia", "ia", "programacion"):
        return True
    # Modulo 4: la rutina matutina/mercado en vivo cambia todos los dias,
    # nunca debe servirse desde cache exacto (blindaje adicional, aunque
    # el handler ya no escribe al cache por su cuenta).
    frases_rutina_matutina = [
        "dame el mercado de hoy", "resumen del mercado", "resumen matutino",
        "que paso overnight", "que paso con el mercado", "rutina matutina",
    ]
    if any(f in pregunta.lower() for f in frases_rutina_matutina):
        return True
    msg = normalizar(pregunta)
    otras_no_cache = [' y ', 'youtube', 'youtu.be', 'http']
    return any(p in msg for p in otras_no_cache)


if __name__ == "__main__":
    # Prueba rapida manual
    tests = [
        "segun sabri que es la zona ote",
        "hola como estas",
        "cual es el precio del btc",
    ]
    for t in tests:
        print(f"{t!r} -> {detectar_dominio(t)}")


def buscar_dominio_semantico(pregunta: str, umbral: float = 1.3):
    """
    Fallback semantico: cuando detectar_dominio() no encuentra ningun
    patron de palabra clave, busca la pregunta por similitud directamente
    en las colecciones curadas de ChromaDB. Si encuentra un buen match
    (distancia menor al umbral), devuelve el dominio correspondiente.
    Devuelve None si no hay match suficientemente bueno.
    """
    from chroma_client import get_chroma_client

    COLECCIONES_DOMINIO = {
        "dataset_qa_programacion_router": "programacion",
        "dataset_qa_ia": "ia",
        "dataset_qa_sabri": "trading",
        "dataset_qa_tecnologia": "tecnologia",
    }

    try:
        client = get_chroma_client()
    except Exception:
        return None

    mejor_dominio = None
    mejor_distancia = float("inf")

    for nombre_col, dominio in COLECCIONES_DOMINIO.items():
        try:
            coleccion = client.get_collection(nombre_col)
            resultado = coleccion.query(query_texts=[pregunta], n_results=1)
            distancias = resultado.get("distances", [[]])[0]
            if distancias and distancias[0] < mejor_distancia:
                mejor_distancia = distancias[0]
                mejor_dominio = dominio
        except Exception:
            continue

    if mejor_dominio and mejor_distancia < umbral:
        return mejor_dominio
    return None


from functools import lru_cache
import unicodedata

def _normalizar_para_cache(pregunta: str) -> str:
    """
    Normaliza el texto para que el cache reconozca preguntas
    equivalentes (mismas palabras, distinta escritura) como iguales:
    minusculas, sin tildes, sin signos de puntuacion en los bordes,
    sin espacios de mas.
    """
    texto = pregunta.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Quitar signos de interrogacion/exclamacion (apertura y cierre) y puntuacion final comun
    for signo in ['¿', '¡', '?', '!', '.', ',']:
        texto = texto.replace(signo, '')
    texto = ' '.join(texto.split())  # colapsa espacios multiples
    return texto

@lru_cache(maxsize=500)
def _buscar_dominio_semantico_con_distancia_cacheado(pregunta_normalizada: str):
    """
    Igual que buscar_dominio_semantico(), pero siempre devuelve
    (dominio, distancia) sin aplicar umbral - para que quien lo llame
    decida si confiar en el resultado comparandolo con otra fuente
    (ej. el resultado de detectar_dominio() por palabra clave).
    Devuelve (None, None) si no hay ninguna coleccion disponible.
    """
    from chroma_client import get_chroma_client

    COLECCIONES_DOMINIO = {
        "dataset_qa_programacion_router": "programacion",
        "dataset_qa_ia": "ia",
        "dataset_qa_sabri": "trading",
        "dataset_qa_tecnologia": "tecnologia",
    }

    try:
        client = get_chroma_client()
    except Exception:
        return None, None

    mejor_dominio = None
    mejor_distancia = float("inf")

    for nombre_col, dominio in COLECCIONES_DOMINIO.items():
        try:
            coleccion = client.get_collection(nombre_col)
            resultado = coleccion.query(query_texts=[pregunta_normalizada], n_results=1)
            distancias = resultado.get("distances", [[]])[0]
            if distancias and distancias[0] < mejor_distancia:
                mejor_distancia = distancias[0]
                mejor_dominio = dominio
        except Exception:
            continue

    return mejor_dominio, mejor_distancia


def buscar_dominio_semantico_con_distancia(pregunta: str):
    """
    Punto de entrada publico: normaliza la pregunta antes de consultar
    el cache, para que preguntas equivalentes (distinta escritura,
    mayusculas, tildes, espacios) reutilicen el mismo resultado cacheado.
    """
    pregunta_normalizada = _normalizar_para_cache(pregunta)
    return _buscar_dominio_semantico_con_distancia_cacheado(pregunta_normalizada)


@lru_cache(maxsize=500)
def _buscar_dominio_semantico_con_margen_cacheado(pregunta_normalizada: str):
    """
    Igual que _buscar_dominio_semantico_con_distancia_cacheado, pero
    ademas devuelve el margen entre el mejor y el segundo mejor
    dominio (margen = distancia_segundo - distancia_mejor). Un margen
    chico indica decision marginal (dos dominios casi empatados); un
    margen grande indica que el mejor domina con claridad.
    Devuelve (mejor_dominio, mejor_distancia, margen). margen es None
    si solo hay un dominio disponible con resultado.
    """
    from chroma_client import get_chroma_client

    COLECCIONES_DOMINIO = {
        "dataset_qa_programacion_router": "programacion",
        "dataset_qa_ia": "ia",
        "dataset_qa_sabri": "trading",
        "dataset_qa_tecnologia": "tecnologia",
    }

    try:
        client = get_chroma_client()
    except Exception:
        return None, None, None

    resultados = []
    for nombre_col, dominio in COLECCIONES_DOMINIO.items():
        try:
            coleccion = client.get_collection(nombre_col)
            resultado = coleccion.query(query_texts=[pregunta_normalizada], n_results=1)
            distancias = resultado.get("distances", [[]])[0]
            if distancias:
                resultados.append((distancias[0], dominio))
        except Exception:
            continue

    if not resultados:
        return None, None, None

    resultados.sort(key=lambda x: x[0])
    mejor_distancia, mejor_dominio = resultados[0]
    margen = resultados[1][0] - mejor_distancia if len(resultados) >= 2 else None

    return mejor_dominio, mejor_distancia, margen


def buscar_dominio_semantico_con_margen(pregunta: str):
    """Punto de entrada publico: normaliza antes de consultar el cache."""
    pregunta_normalizada = _normalizar_para_cache(pregunta)
    return _buscar_dominio_semantico_con_margen_cacheado(pregunta_normalizada)
