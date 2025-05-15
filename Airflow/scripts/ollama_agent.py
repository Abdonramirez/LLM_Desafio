import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langgraph.graph import StateGraph, END
import re
import os
from datetime import datetime, timedelta
from typing import TypedDict, List
from langchain_community.llms import Ollama

# Cargar el DataFrame
df = pd.read_csv("scripts/data/Articulos_limpios.csv").drop_duplicates()

# Crear documentos con metadatos
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Primero: ¿ya existe el vectorstore?
if os.path.exists("faiss_index"):
    print("🔁 Cargando vectorstore desde disco...")
    vectorstore = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

else:
    print("⚙️ Generando vectorstore desde documentos...")

    df = pd.read_csv("Articulos_LLM6.csv").drop_duplicates()

    # Crear documentos
    docs = [
        Document(
            page_content=row["contenido"],
            metadata={
                "titulo": row["titulo"],
                "url": row["url"],
                "precio": row.get("Precios", ""),
                "fecha_inicio": row.get("fecha_inicio", ""),
                "fecha_fin": row.get("fecha_fin", ""),
                "seccion": row["seccion"],
                "ciudad": row["ciudad"]
            }
        )
        for _, row in df.iterrows() if pd.notnull(row["contenido"])
    ]

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )

    chunked_docs = []
    for doc in docs:
        for chunk in splitter.split_text(doc.page_content):
            chunked_docs.append(Document(
                page_content=chunk,
                metadata=doc.metadata
            ))

    # Embeddings + FAISS
    vectorstore = FAISS.from_documents(chunked_docs, embedding_model)
    vectorstore.save_local("faiss_index")
    print("✅ Vectorstore guardado en disco.")

vectorstore = None

def load_vectorstore(force_reload=False):
    global vectorstore
    if vectorstore is None or force_reload:
        print("🔁 Cargando vectorstore desde disco...")
        vectorstore = FAISS.load_local(
            "faiss_index",
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            allow_dangerous_deserialization=True
        )
    return vectorstore

# 1. Configura tu modelo local con Ollama
llm = Ollama(model="mistral", base_url="http://ollama:11434")

class AgentState(TypedDict):
    query: str
    documents: List[Document]
    generation: str


def parse_fecha(fecha_str):
    """Intenta convertir un string como '15 de mayo' o 'domingo 27 de abril' en un objeto datetime.date"""
    try:
        fecha_str = re.sub(r'^\w+\s', '', fecha_str.strip())
        return datetime.strptime(fecha_str, "%d de %B").replace(year=datetime.now().year).date()
    except Exception:
        return None


def detectar_intencion_temporal(query):
    """Detecta si el usuario está preguntando por hoy, mañana, fin de semana, etc."""
    hoy = datetime.now().date()
    query = query.lower()

    if "hoy" in query:
        return lambda fecha_ini, fecha_fin: fecha_ini <= hoy <= fecha_fin
    elif "mañana" in query:
        manana = hoy + timedelta(days=1)
        return lambda fecha_ini, fecha_fin: fecha_ini <= manana <= fecha_fin
    elif "semana que viene" in query:
        prox_lunes = hoy + timedelta(days=(7 - hoy.weekday()))
        prox_domingo = prox_lunes + timedelta(days=6)
        return lambda fecha_ini, fecha_fin: fecha_ini <= prox_domingo and fecha_fin >= prox_lunes
    elif "fin de semana" in query:
        viernes = hoy + timedelta((4 - hoy.weekday()) % 7)
        domingo = viernes + timedelta(days=2)
        return lambda fecha_ini, fecha_fin: fecha_ini <= domingo and fecha_fin >= viernes
    else:
        return lambda fecha_ini, fecha_fin: True  # No aplica filtro temporal


def filtrar_por_fecha_y_seccion(docs, query):
    criterio_fecha = detectar_intencion_temporal(query)
    criterio_seccion = "ocio" if any(p in query.lower() for p in ["ocio", "plan", "evento", "actividad"]) else None

    docs_filtrados = []
    docs_sin_fecha = []

    for doc in docs:
        meta = doc.metadata
        seccion = meta.get("seccion", "").lower()
        fecha_ini_str = meta.get("fecha_inicio", "")
        fecha_fin_str = meta.get("fecha_fin", "")

        fecha_ini = parse_fecha(fecha_ini_str) if fecha_ini_str else None
        fecha_fin = parse_fecha(fecha_fin_str) if fecha_fin_str else fecha_ini

        if not fecha_ini and not fecha_fin:
            if criterio_seccion and seccion == criterio_seccion:
                docs_sin_fecha.append(doc)
            continue

        if fecha_ini and fecha_fin and criterio_fecha(fecha_ini, fecha_fin):
            if not criterio_seccion or seccion == criterio_seccion:
                docs_filtrados.append(doc)

    if len(docs_filtrados) < 5:
        docs_filtrados += docs_sin_fecha[:3]

    return docs_filtrados


# 3. Recuperación con MMR (ajustado para diversidad)
def retrieve(state):
    query = state["query"]
    docs = vectorstore.max_marginal_relevance_search(query, k=10, fetch_k=50)
    return {"documents": docs}

# 4. Generación usando contexto real
def generate(state):
    docs = filtrar_por_fecha_y_seccion(state["documents"], state["query"])
    query = state["query"]

    fecha_actual = datetime.now().strftime("%A, %d de %B de %Y")

    # Construir contexto claro y útil
    context = "\n\n".join(
        f"{doc.page_content}\nFuente: {doc.metadata.get('url', '')}"
        for doc in docs[:5]
    )

    # Prompt optimizado para Mistral:
    prompt = f"""
Fecha actual: {fecha_actual}

Responde de forma clara, breve y profesional a la pregunta del usuario utilizando solamente la información proporcionada en el contexto. 
Escribe una respuesta en forma de párrafo basada solo en el contexto anterior. Al final de la respuesta, agrega una lista de hasta 3 enlaces relevantes extraídos del contexto.
No inventes actividades, lugares ni enlaces. Si hay poca información, da una recomendación general y sugiere consultar los enlaces reales al final.

Contexto:
\"\"\"
{context}
\"\"\"

Pregunta:
{query}

Respuesta:
"""

    respuesta = llm.invoke(prompt)

    enlaces = {
        doc.metadata.get("url"): doc.metadata.get("titulo", "Actividad sin título")
        for doc in docs if doc.metadata.get("url")
    }
    enlaces = dict(list(enlaces.items())[:3])

    # Bloque de enlaces al final
    if enlaces:
        links_texto = (
            "\n\nPara más información sobre estas actividades, puedes consultar:\n" +
            "\n".join(f"- {titulo}\n  {url}" for url, titulo in enlaces.items())
        )
    else:
        links_texto = ""

    return {
        "generation": f"{respuesta.strip()}{links_texto}"
    }

graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_agent = graph.compile()
