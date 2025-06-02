#!/bin/bash

# Poista vanha container, jos sellainen on olemassa
if [ "$(docker ps -a -q -f name=aaibot-rag)" ]; then
    echo "🧹 Poistetaan vanha container: aaibot-rag"
    docker rm -f aaibot-rag
fi

# Poista vanha image (valinnainen – ei aina tarpeen)
if [ "$(docker images -q aaibot-rag)" ]; then
    echo "🧼 Poistetaan vanha Docker image: aaibot-rag"
    docker rmi -f aaibot-rag
fi

echo "⚙️ Rakennetaan uusi Docker image ja käynnistetään containerit..."
docker compose up -d --build

echo "✅ Valmis. Aktiiviset containerit:"
docker ps
