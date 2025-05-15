
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scripts.ollama_agent import rag_agent

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

# ENDPOINT
@app.post("/chat")
def chat(query: ChatInput):
    try:
        state = {"query": query.question}
        result = rag_agent.invoke(state)
        return {"response": result["generation"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
