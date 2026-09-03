#!/usr/bin/env python3
"""
ingesta_minima.py — crea una colección de ChromaDB con documentos de
ejemplo, para que el core mínimo (aria_core_minimo.py) tenga contexto
real que recuperar en la primera prueba, en vez del mensaje de fallback
"todavía no existe la colección" (ver aria_core_minimo.py y el README de
esta carpeta).

Qué hace: crea (o actualiza) la colección "dataset_ia" en la misma
carpeta de ChromaDB que usa aria_core_minimo.py (../chroma_db_minimo,
relativa a este archivo — ver Fase 3.1, corrección de Kimi sobre
CHROMA_DIR), con 3 documentos de texto genéricos sobre LLMs, RAG y
ChromaDB. Se eligió el dominio "ia" porque config_dominios.py rutea ahí
preguntas como "que es un modelo de lenguaje" — se verificó contra el
enrutador real antes de escribir este script, no se asumió.

Los documentos están identificados como material de ejemplo en su
propio contenido ("Este es un documento de ejemplo para probar el RAG
de ARIA") — no son fragmentos reales de la biblioteca de ARIA ni de
ningún manual de sesión de este proyecto.

Uso (después de instalar requirements-core.txt, ver /arrancar_aria.sh):
    python3 codigo/ingesta_minima.py

Después de correrlo, probá:
    ./arrancar_aria.sh "que es un modelo de lenguaje"
    ./arrancar_aria.sh "que es RAG"
    ./arrancar_aria.sh "que es chromadb"

Nota sobre la primera corrida: ChromaDB descarga un modelo de embeddings
por defecto (ONNX, unos MB) la primera vez que se usa — necesita salida
a internet esa primera vez. Es un comportamiento estándar de la
librería, no algo específico de este script (ver la nota de
verificación funcional en el README de esta carpeta).

Correr este script más de una vez no duplica documentos (usa upsert
con ids fijos).
"""

import sys
from pathlib import Path

CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db_minimo"
NOMBRE_COLECCION = "dataset_ia"

DOCUMENTOS_DE_EJEMPLO = [
    "Este es un documento de ejemplo para probar el RAG de ARIA. "
    "Un modelo de lenguaje (LLM) es un sistema entrenado con grandes "
    "cantidades de texto para predecir la palabra o el fragmento que "
    "sigue en una secuencia, lo que le permite generar texto coherente "
    "en respuesta a una instrucción o pregunta.",

    "Este es un documento de ejemplo para probar el RAG de ARIA. "
    "RAG (Retrieval-Augmented Generation, generación aumentada por "
    "recuperación) combina una búsqueda de información relevante en "
    "una base de datos con la generación de una respuesta por un "
    "modelo de lenguaje, para que la respuesta se base en contenido "
    "concreto y verificable en vez de solo en lo que el modelo "
    "aprendió durante su entrenamiento.",

    "Este es un documento de ejemplo para probar el RAG de ARIA. "
    "ChromaDB es una base de datos vectorial de código abierto: guarda "
    "textos junto con su representación numérica (embedding), y "
    "permite buscar los textos más parecidos semánticamente a una "
    "consulta dada, no solo por coincidencia exacta de palabras.",
]

IDS = [f"ejemplo_ia_{i + 1}" for i in range(len(DOCUMENTOS_DE_EJEMPLO))]

# Metadata simple por documento (mejora sugerida por Kimi, Fase 3.2): no
# hace falta para que el RAG funcione, pero sirve como referencia de cómo
# se usa metadata en ChromaDB — cada documento queda marcado con su
# fuente (para no confundirlo nunca con contenido real de la biblioteca
# de ARIA) y su dominio.
METADATAS = [{"fuente": "ejemplo", "dominio": "ia"} for _ in DOCUMENTOS_DE_EJEMPLO]


def main():
    try:
        import chromadb
    except ImportError:
        print("El paquete chromadb no está instalado (pip install -r requirements-core.txt).")
        sys.exit(1)

    print(f"Creando/actualizando la colección '{NOMBRE_COLECCION}' en {CHROMA_DIR}...")
    cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))
    coleccion = cliente.get_or_create_collection(NOMBRE_COLECCION)

    try:
        coleccion.upsert(documents=DOCUMENTOS_DE_EJEMPLO, ids=IDS, metadatas=METADATAS)
    except Exception as e:
        print(
            "No se pudo generar el embedding de los documentos de ejemplo "
            f"({e}).\nLa primera vez que se usa, ChromaDB necesita "
            "descargar su modelo de embeddings por defecto (unos MB) — "
            "verificá que tengas salida a internet y reintentá."
        )
        sys.exit(1)

    print(f"Listo: {coleccion.count()} documento(s) de ejemplo en '{NOMBRE_COLECCION}'.")
    print('Probá ahora: ./arrancar_aria.sh "que es un modelo de lenguaje"')


if __name__ == "__main__":
    main()
