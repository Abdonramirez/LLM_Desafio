import pandas as pd
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

df = pd.read_csv("Agente/Articulos_LLM6.csv")
df = df.drop_duplicates()

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
    for _, row in df.iterrows()
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "]
)

# Crear los Document chunked
chunked_docs = []

for _, row in df.iterrows():
    texto = row["contenido"]
    if pd.isnull(texto):
        continue
    chunks = splitter.split_text(texto)
    for i, chunk in enumerate(chunks):
        chunked_docs.append(Document(
            page_content=chunk,
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
        )

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Vectorstore
vectorstore = FAISS.from_documents(chunked_docs, embedding_model)

vectorstore.save_local("faiss_index")
