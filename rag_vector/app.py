# rag_vector/app.py

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import requests

app = FastAPI()

# Alusta ChromaDB client oikeasta polusta
client = chromadb.PersistentClient(path="./VectorDB/chroma")
collection = client.get_or_create_collection(name="local-rag")

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(payload: QuestionRequest):
    question = payload.question

    # Hae top 3 samankaltaisinta dokumenttia kysymykseen
    try:
        results = collection.query(
            query_texts=[question],
            n_results=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe tietokannassa: {e}")

    documents = results.get("documents", [[]])[0]
    if not documents:
        return {"answer": "🤖 Ei vastausta."}

    context = "\n".join(documents)

    # Luo prompt vastausta varten
    prompt = f"Konteksti:\n{context}\n\nKysymys: {question}\nVastaus:"

    # Lähetä pyyntö Ollamalle
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return {"answer": data.get("response", "🤖 Ei vastausta.")}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama-virhe: {e}")


@app.get("/")
def index():
    return {"message": "RAG-palvelu toimii."}
