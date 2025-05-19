from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scripts.ollama_agent import rag_agent, load_vectorstore
import uvicorn

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"message": "API del agente RAG funcionando."}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        result = rag_agent.invoke({"query": request.prompt})
        return {"response": result["generation"]}  # ✅ Solo devolvemos la respuesta generada
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente: {str(e)}")

@app.post("/reload_vectorstore")
def reload_vectorstore():
    try:
        print("🔄 Recargando vectorstore...")
        load_vectorstore(force_reload=True)
        return {"message": "Vectorstore recargado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recargar vectorstore: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
