from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama_agent import rag_agent

import sqlite3
from datetime import datetime

# Inicializar base de datos
DB_PATH = "conversaciones.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# FASTAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELO ENTRADA
class ChatInput(BaseModel):
    question: str
    email: str

@app.post("/chat")
def chat(query: ChatInput):
    try:
        # Asegúrate de que ChatInput tenga `email` y `question`
        state = {"query": query.question}
        result = rag_agent.invoke(state)
        respuesta = result["generation"]

        # Guardar en base de datos
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversaciones (email, pregunta, respuesta) VALUES (?, ?, ?)",
                (query.email, query.question, respuesta)
            )
            conn.commit()

        return {"response": respuesta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/historial/{email}")
def historial(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pregunta, respuesta, timestamp FROM conversaciones WHERE email = ? ORDER BY timestamp ASC",
            (email,)
        )
        rows = cursor.fetchall()

    return {
        "email": email,
        "historial": [
            {"pregunta": r[0], "respuesta": r[1], "timestamp": r[2]} for r in rows
        ]
    }
