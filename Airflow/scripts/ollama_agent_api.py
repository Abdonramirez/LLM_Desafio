from fastapi import FastAPI, HTTPException
from scripts.ollama_agent import rag_agent, load_vectorstore
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API del agente RAG funcionando."}

@app.post("/chat")
def chat(prompt: str):
    try:
        return {"response": rag_agent.invoke(prompt)["answer"]}
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
