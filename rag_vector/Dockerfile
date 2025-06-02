FROM python:3.10-slim

WORKDIR /app

ENV OLLAMA_BASE_URL=http://ollama-container:11434

# Peruspaketit
RUN apt-get update && apt-get install -y curl jq && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Koodi ja data
COPY app.py .
COPY embedder.py .
COPY VectorDB/ ./VectorDB/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
