#!/bin/bash

# Asetukset
MODELS=("nomic-embed-text" "llama3")
OLLAMA_CONTAINER="ollama-container"

echo "🌐 Varmistetaan Docker-verkko..."
docker network inspect rag-network >/dev/null 2>&1 || docker network create rag-network

echo "🧹 Poistetaan vanha kontti ja image..."
docker rm -f rag-vector 2>/dev/null
docker rmi -f rag-vector 2>/dev/null

echo "🔨 Rakennetaan uusi image ilman BuildKit..."
DOCKER_BUILDKIT=0 docker build -t rag-vector . || {
    echo "❌ Build epäonnistui."
    exit 1
}

echo "🚀 Käynnistetään uusi rag-vector-kontti verkossa 'rag-network'..."
docker run -d \
    --name rag-vector \
    --network rag-network \
    -e OLLAMA_BASE_URL=http://ollama-container:11434 \
    -p 8000:8000 \
    -v "$(pwd)/VectorDB:/app/VectorDB" \
    rag-vector

echo "⏳ Odotetaan 5 sekuntia palvelimen käynnistymistä..."
sleep 5

# 🔍 Tarkista onko Ollama-kontti käynnissä
if ! docker ps --format '{{.Names}}' | grep -q "$OLLAMA_CONTAINER"; then
    echo "❌ Ollama-kontti '$OLLAMA_CONTAINER' ei ole käynnissä!"
    exit 1
fi

# 🧠 Tarkistetaan mallien saatavuus
for MODEL in "${MODELS[@]}"; do
  echo "📦 Tarkistetaan onko malli '$MODEL' jo ladattu Ollama-konttiin..."
  docker exec "$OLLAMA_CONTAINER" ollama show "$MODEL" >/dev/null 2>&1
  if [ $? -ne 0 ]; then
      echo "⬇️ Ladataan malli '$MODEL' Ollama-konttiin..."
      docker exec "$OLLAMA_CONTAINER" ollama pull "$MODEL"
  else
      echo "✅ Malli '$MODEL' on jo ladattu."
  fi
done

# 🔁 Aja embedder.py kontissa
echo "🧠 Ajetaan embedder.py kontissa..."
docker exec rag-vector python embedder.py || echo "❌ embedder.py ajo epäonnistui."
