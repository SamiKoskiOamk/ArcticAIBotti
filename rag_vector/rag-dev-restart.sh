#!/bin/bash

echo "🧹 Poistetaan vanha rag-vector-kontti..."
docker rm -f rag-vector 2>/dev/null

echo "🚀 Käynnistetään uusi rag-vector-kontti olemassa olevasta imagesta..."
docker run -d \
  --name rag-vector \
  --network rag-network \
  -e OLLAMA_BASE_URL=http://ollama-container:11434 \
  -p 8000:8000 \
  rag-vector

echo "⏳ Odotetaan 2 sekuntia palvelimen käynnistymistä..."
sleep 2

echo "✅ Käynnistetty. Testaa osoitteessa http://localhost:8000/ask?q=testi"
