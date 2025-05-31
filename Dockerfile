# Dockerfile: RAG + ChromaDB + Ollama + FastAPI

FROM python:3.10-slim

#turhat warningit piiloon
ENV TF_CPP_MIN_LOG_LEVEL=2

# Asenna systeemitasolla tarvittavat paketit
RUN apt-get update && apt-get install -y \
    curl git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Luo työhakemisto
WORKDIR /app

# Kopioi riippuvuustiedosto ja asenna kirjastot
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip list

# Kopioi sovelluskoodi
COPY rag_vector/ ./rag_vector/
COPY VectorDB/ ./VectorDB/

# Luo vektorikanta buildin aikana (embeddingit ja indeksi)
CMD ["bash", "-c", "python rag_vector/embedder.py && uvicorn rag_vector.app:app --host 0.0.0.0 --port 8000"]

# Altista portti FastAPI:lle
EXPOSE 8000

# Kaynnista FastAPI-palvelin
CMD ["uvicorn", "rag_vector.app:app", "--host", "0.0.0.0", "--port", "8000"]
