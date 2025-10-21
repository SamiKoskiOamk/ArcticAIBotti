# app.py — Aibotti RAG (LCEL, LangChain 0.2+), Ollama + Chroma
import os
from typing import List, Dict, Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings


# --- Konffit ympäristöstä (voit yliajaa docker-compose.yml:ssä) ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-container:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
PERSIST_DIR = os.getenv("PERSIST_DIR", "/app/VectorDB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "aibotti")
TOP_K = int(os.getenv("TOP_K", "4"))

app = FastAPI(title="Aibotti RAG API")

# --- CORS sallivaksi (säädä tarvittaessa tiukemmaksi) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- LLM + Embeddings + Vectorstore + Retriever ---
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_HOST, temperature=0.2)

# TÄRKEÄÄ: käytä samaa embedding-mallia kuin embedder.py (esim. nomic-embed-text)
emb = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_HOST)

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIR,
    embedding_function=emb,  # ilman tätä /ask ei voi embeddata kyselyä
)
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

# --- Prompt + ketju (LCEL) ---
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Olet avulias suomenkielinen avustaja. Vastaa ytimekkäästi hyödyntäen kontekstia. "
     "Jos vastaus ei löydy kontekstista, sano lyhyesti ettet tiedä."),
    ("human",
     "Kysymys: {input}\n\nKonteksti:\n{context}")
])

def _format_docs(docs: List[Any]) -> str:
    return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)

# {'context': retriever(query)->format, 'input': alkuperäinen query} -> prompt -> llm -> string
chain = (
    {"context": retriever | _format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def _sources_for(query: str):
    # 0.2+: hae dokumentit retriever.invoke(query)
    docs = retriever.invoke(query)  # <- TÄMÄ
    out = []
    for d in docs:
        md = getattr(d, "metadata", {}) or {}
        src = md.get("source") or md.get("source_url") or md.get("url")
        out.append({
            "source": src,
            "doc_index": md.get("doc_index"),
            "chunk_index": md.get("chunk_index"),
            "score": md.get("score"),
        })
    return out

# --- Endpointit ---
@app.get("/health")
def health():
    count = None
    try:
        # diag-käyttöön; voi puuttua joistain drivereista
        count = vectorstore._collection.count()  # nosec
    except Exception:
        pass
    return {
        "status": "ok",
        "ollama_host": OLLAMA_HOST,
        "model": OLLAMA_MODEL,
        "persist_dir": PERSIST_DIR,
        "collection": COLLECTION_NAME,
        "doc_count": count,
        "top_k": TOP_K,
    }

@app.get("/ask")
def ask(query: str = Query(..., description="Käyttäjän kysymys")):
    try:
        answer = chain.invoke(query)
        sources = _sources_for(query)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        return {"error": str(e)}