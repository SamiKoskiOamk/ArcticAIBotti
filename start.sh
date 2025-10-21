#!/bin/bash
# Tämä skripti käynnistää kaikki palvelussa olevat kontit
# - Ollama (LLM)
# - rag-vector (Retriever)

# Käynnistä Ollama taustalle
ollama serve &
echo "⏳ Odotetaan että Ollama käynnistyy..."
sleep 10

# Luo embeddingit
echo "🔧 Ajetaan embedder.py..."
python rag_vector/embedder.py || { echo "❌ Embedding epäonnistui"; exit 1; }
# embedder.py lukee aiemmin tuotetut .jsonl-tiedostot (ne, jotka vectorize.py teki)
# Se purkaa niistä tekstin ja embeddingit ja tallentaa ne ChromaDB-tietokantaan
# Tekee Aibotin “Retriever”-vaiheen tietovaraston käyttövalmiiksi

# Käynnistä FastAPI-palvelin
echo "🚀 Käynnistetään FastAPI..."
uvicorn rag_vector.app:app --host 0.0.0.0 --port 8000
# Saa käyttäjän kyselyn (/ask, /query tms.).
# Muuntaa kysymyksen embeddingiksi.
# Tekee haun ChromaDB:stä (retrieval).
# Lähettää haetun kontekstin Ollamalle (augmentation + generation).
# Palauttaa valmiin vastauksen.
