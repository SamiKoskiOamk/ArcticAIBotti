#!/bin/bash

echo "🌐 Varmistetaan Docker-verkko..."
docker network inspect rag-network >/dev/null 2>&1 || docker network create rag-network

echo "🛠️ Poistetaan vanha Ollama-kontti (jos olemassa)..."
docker rm -f ollama-container 2>/dev/null || true

echo "🔨 Rakennetaan Ollama-kontin image..."
docker build -t ollama-container .

echo "🚀 Käynnistetään uusi Ollama-kontti verkossa 'rag-network'..."
docker run -d \
  --name ollama-container \
  --network rag-network \
  -e OLLAMA_HOST=0.0.0.0 \
  ollama-container

echo "⏳ Odotetaan hetki, että Ollama käynnistyy..."
sleep 5

echo "🔍 Tarkistetaan onko malli 'llama3' jo ladattu..."
if docker exec ollama-container ollama list | grep -q "llama3"; then
  echo "✅ Malli 'llama3' on jo ladattu."
else
  echo "⬇️ Ladataan malli 'llama3'..."
  docker exec ollama-container ollama pull llama3 || {
    echo "❌ Mallin lataus epäonnistui!"
    exit 1
  }
  echo "✅ Malli 'llama3' ladattu onnistuneesti."
fi

echo "✅ Ollama on nyt käynnissä ja malli valmis käytettäväksi."
