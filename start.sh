#!/bin/bash

# Käynnistä Ollama taustalle
ollama serve &
echo "⏳ Odotetaan että Ollama käynnistyy..."
sleep 10

# Luo embeddingit
echo "🔧 Ajetaan embedder.py..."
python rag_vector/embedder.py || { echo "❌ Embedding epäonnistui"; exit 1; }

# Käynnistä FastAPI-palvelin
echo "🚀 Käynnistetään FastAPI..."
uvicorn rag_vector.app:app --host 0.0.0.0 --port 8000
