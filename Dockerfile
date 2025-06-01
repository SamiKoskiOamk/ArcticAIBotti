# Käytä virallista Python-imagea
FROM python:3.10-slim

# Asenna järjestelmäriippuvuudet
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Asenna Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Luo työskentelyhakemisto
WORKDIR /app

# Kopioi sovelluksen tiedostot
COPY . /app

# Asenna Python-riippuvuudet
RUN pip install --upgrade pip && pip install -r requirements.txt

# Aseta default komento: käynnistä Ollama, odota, lataa malli, upota ja käynnistä FastAPI
CMD ollama serve & \
    sleep 10 && \
    ollama pull llama3 && \
    python rag_vector/embedder.py && \
    uvicorn rag_vector.app:app --host 0.0.0.0 --port 8000
