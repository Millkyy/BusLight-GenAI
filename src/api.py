from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .agent import answer, retriever, sources
from .config import OLLAMA_MODEL, RETRIEVAL_THRESHOLD

app=FastAPI(title="BusLight Assist API",version="1.0.0",description="Assistente local com RAG e agente especializado; não expõe previsões em tempo real sem ferramenta operacional.")

@app.get("/")
def root():
    """Página inicial simples com links para os recursos da API."""
    return {
        "service": "BusLight Assist API",
        "status": "ok",
        "message": "API local disponível. Abra /docs para testar os endpoints.",
        "docs": "/docs",
        "health": "/health",
        "sources": "/sources",
        "assist": "/assist (POST)",
    }
class AssistRequest(BaseModel):
    question: str = Field(min_length=3,max_length=1000)
    mode: str = Field(default="agent",pattern="^(base|rag|agent)$")
@app.get("/health")
def health():
    return {"status":"ok","model":OLLAMA_MODEL,"knowledge_chunks":len(retriever.chunks),"threshold":RETRIEVAL_THRESHOLD,"mode_default":"agent"}
@app.get("/sources")
def list_sources():
    return list(sources.values())
@app.post("/assist")
def assist(req:AssistRequest):
    try: return answer(req.question,req.mode)
    except Exception as exc: raise HTTPException(status_code=503,detail=str(exc))
