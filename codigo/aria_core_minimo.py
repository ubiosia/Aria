#!/usr/bin/env python3
"""
aria_core_minimo.py — versión DIDÁCTICA y mínima del orquestador de ARIA.
Fase 3, Punto 2 ("core mínimo ejecutable") del repositorio.

Esto NO es el aria_core.py real de producción. El real existe, pero
importa alrededor de 30 módulos internos del proyecto — 15 agentes de
dominio (agente_trading.py, agente_ia.py, agente_programacion.py, etc.),
un registro de skills, working memory, recuperación de estado, y más —
que no forman parte de este repositorio. Publicarlo tal cual rompería
en el primer import, sin cumplir el objetivo real de este archivo: que
alguien pueda clonar el repo, instalar `requirements.txt`, y ver algo
funcionando de punta a punta.

Lo que este archivo SÍ hace, corriendo de verdad, sin simular nada:

1. Usa el enrutador real y ya publicado de este mismo repositorio
   (config_dominios.detectar_dominio(), en esta misma carpeta) para
   decidir el dominio de una pregunta — la misma lógica que usa ARIA en
   producción, sin ninguna simplificación.
2. Busca contexto relevante en una colección local de ChromaDB para ese
   dominio (RAG real, no simulado) — ver /tecnico/decisiones.md, ADR-005.
3. Le pasa ese contexto (si lo encontró) más la pregunta a un modelo de
   Ollama corriendo en localhost, y devuelve la respuesta.
4. Si Ollama no está corriendo, o la colección de ChromaDB todavía no
   existe o está vacía, lo dice con un mensaje claro en vez de fallar —
   para que el enrutamiento (el punto 1) se pueda ver funcionando aunque
   la generación de respuesta (los puntos 2 y 3) todavía no tenga nada
   que usar en una instalación nueva, recién clonada.

Referencia de arquitectura: /tecnico/arquitectura.md (diagrama de flujo
de pregunta) y /tecnico/decisiones.md (ADR-005, ChromaDB).

Uso:
    python3 aria_core_minimo.py "tu pregunta acá"
    python3 aria_core_minimo.py    # pide la pregunta interactivamente
"""

import sys
from pathlib import Path

# Permite "from config_dominios import ..." sin depender de desde dónde
# se ejecute este script — config_dominios.py vive en esta misma carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_dominios import detectar_dominio

# Corrección (revisión Kimi, post-Fase 3): antes usaba Path.home() /
# "asistente" / "chroma_db_minimo", una ruta fija que no tiene relación
# con dónde se clona este repositorio. Ahora es relativa al propio
# archivo, así que funciona sin importar dónde se clonó — vive como
# carpeta hermana de esta (codigo/), en la raíz del repo.
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db_minimo"
MODELO_OLLAMA = "llama3.1:8b"  # modelo principal, ver tecnico/instalacion.md sección 4


def obtener_contexto_rag(dominio: str, pregunta: str, max_resultados: int = 3):
    """
    Busca contexto relevante en una colección local de ChromaDB para el
    dominio detectado. Devuelve (contexto, aviso): contexto es None si no
    hay nada útil, y aviso explica por qué (para mostrárselo a quien está
    probando el sistema, no para ocultar el problema).
    """
    try:
        import chromadb
    except ImportError:
        return None, "el paquete chromadb no está instalado (pip install -r requirements.txt)"

    cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))
    nombre_coleccion = f"dataset_{dominio}"

    try:
        coleccion = cliente.get_collection(nombre_coleccion)
    except Exception:
        return None, (
            f"todavía no existe la colección '{nombre_coleccion}' en "
            f"{CHROMA_DIR} — este core mínimo no incluye un script de "
            f"ingesta; creá la colección y cargale documentos antes de "
            f"esperar contexto real para el dominio '{dominio}'"
        )

    if coleccion.count() == 0:
        return None, f"la colección '{nombre_coleccion}' existe pero está vacía"

    resultado = coleccion.query(query_texts=[pregunta], n_results=max_resultados)
    documentos = resultado.get("documents", [[]])[0]
    if not documentos:
        return None, f"no se encontró ningún documento relevante en '{nombre_coleccion}' para esta pregunta"

    return "\n\n".join(documentos), None


def preguntar_a_ollama(prompt: str, modelo: str = MODELO_OLLAMA) -> str:
    """Le pasa el prompt a Ollama corriendo en localhost. Sin mocks: si
    Ollama no está disponible, se ve el error real, explicado."""
    try:
        import ollama
    except ImportError:
        return "El paquete 'ollama' no está instalado (pip install -r requirements.txt)."

    try:
        respuesta = ollama.generate(model=modelo, prompt=prompt)
        return respuesta.get("response", "").strip()
    except ConnectionError:
        return (
            f"No se pudo conectar con Ollama en localhost:11434. "
            f"Verificá que esté corriendo ('ollama serve') y que el modelo "
            f"'{modelo}' esté descargado ('ollama pull {modelo}') — ver "
            f"/tecnico/instalacion.md, secciones 3 y 4."
        )
    except Exception as e:
        return f"Ollama respondió con un error inesperado: {e}"


def responder(pregunta: str) -> str:
    """
    Punto de entrada único de este core mínimo. Equivalente reducido de
    ARIACore.responder() en el sistema real: detecta el dominio, busca
    contexto, genera una respuesta. Sin caché, sin memoria personal, sin
    los ~15 agentes de dominio del sistema completo — solo lo necesario
    para demostrar que el patrón enrutar → RAG → LLM corre de verdad.
    """
    if not pregunta.strip():
        return "Escribí algo primero."

    dominio = detectar_dominio(pregunta)
    contexto, aviso_rag = obtener_contexto_rag(dominio, pregunta)

    if contexto:
        prompt = (
            f"Contexto recuperado:\n{contexto}\n\n"
            f"Pregunta: {pregunta}\n"
            f"Respondé en español, usando el contexto de arriba si es relevante."
        )
    else:
        prompt = pregunta

    respuesta_llm = preguntar_a_ollama(prompt)

    partes = [f"[dominio detectado: {dominio}]"]
    if aviso_rag:
        partes.append(f"[RAG: {aviso_rag}]")
    partes.append(respuesta_llm)
    return "\n".join(partes)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pregunta_cli = " ".join(sys.argv[1:])
    else:
        pregunta_cli = input("Pregunta de prueba: ")
    print(responder(pregunta_cli))
