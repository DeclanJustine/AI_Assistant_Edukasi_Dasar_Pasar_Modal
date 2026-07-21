import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag.chain import build_rag_chain
from src.rag.history import clear_session
from src.kuesioner.data import load_kuesioner




app = FastAPI(title="Asisten Pasar Modal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ResetRequest(BaseModel):
    session_id: str


@app.on_event("startup")
async def startup():
    global rag
    rag = build_rag_chain()


@app.get("/api/kuesioner")
def get_kuesioner():
    return load_kuesioner()


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not rag:
        raise HTTPException(503, "Model belum siap")

    result = rag["chain"].invoke(
        {"input": req.message},
        config={"configurable": {"session_id": req.session_id}},
    )

    answer = result["answer"]
    contexts = result.get("context", [])

    sources = [
        {"content": doc.page_content[:300], "source": doc.metadata.get("source", "Unknown")}
        for doc in contexts
    ]

    return {"answer": answer, "sources": sources}


@app.post("/api/reset")
def reset_session(req: ResetRequest):
    clear_session(req.session_id)
    return {"status": "ok"}
