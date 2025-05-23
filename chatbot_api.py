from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import numpy as np
import json, os, requests

# ---- Setup ----
app = FastAPI()

# Malli latautuu vain kerran
model = SentenceTransformer("all-MiniLM-L6-v2")

# Vektoriaineiston sijainti (muokkaa tarvittaessa WSL-poluksi esim. /mnt/c/...)
VECTORDIR = "/mnt/c/AI-botti/vektrodata/oamkjournal"

# CORS-asetukset (esim. jos käytät frontendista selaimessa)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---- Helper: Load latest vector file ----
def load_latest_vector_file():
    files = [f for f in os.listdir(VECTORDIR) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError("No vector files found in: " + VECTORDIR)
    latest = max(files)  # oletetaan, että tiedostonimissä on päivämäärät
    path = os.path.join(VECTORDIR, latest)
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# ---- Helper: Get top-k similar chunks ----
def get_top_chunks(query, data, top_k=5):
    q_vec = model.encode([query])
    data_embeddings = np.array([d["embedding"] for d in data])
    sims = cosine_similarity(q_vec, data_embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    return [data[i]["text"] for i in top_indices]

# ---- Ollama call ----
def query_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {str(e)}")

# ---- API: Ask ----
@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    question = body.get("question", "").strip()

    if not question:
        return {"error": "Tyhjä kysymys"}

    try:
        vector_data = load_latest_vector_file()
        top_chunks = get_top_chunks(question, vector_data, top_k=5)
        context = "\n---\n".join(top_chunks)

        prompt = f"""Käytä alla olevaa sisältöä vastataksesi kysymykseen. Vastaa aina **suomeksi**, älä käytä englannin kieltä.

Sisältö:
---
{context}
---

Kysymys: {question}
Vastaa suomeksi:"""

        answer = query_ollama(prompt)
        return {"answer": answer.strip()}

    except Exception as e:
        return {"error": str(e)}

# ---- Käynnistysohje komentoriviltä ----
# tarkista, että LLM pyörii eka sinun virtual environmentissa: ollama run llama3
# uvicorn chatbot_api:app --reload --port 8000
# varmista että Ollama on päällä: ollama run llama3
