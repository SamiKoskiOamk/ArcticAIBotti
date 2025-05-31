# rag_vector/embedder.py

import os
import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Luo ChromaDB client pysyvään kansioon
client = chromadb.PersistentClient(path="./VectorDB/chroma")
collection = client.get_or_create_collection(name="local-rag")

# Lataa SentenceTransformer embedder
print("🔄 Ladataan SentenceTransformer-malli...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Malli ladattu.")

# Lue kaikki jsonl-tiedostot kansiosta ja alikansioista
total_docs = 0
for root, dirs, files in os.walk("./VectorDB"):
    for file in files:
        if file.endswith(".jsonl"):
            full_path = os.path.join(root, file)
            print(f"📄 Käsitellään tiedosto: {full_path}")
            with open(full_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    try:
                        obj = json.loads(line)
                        content = obj.get("text") or obj.get("content")
                        if content:
                            embedding = model.encode(content).tolist()
                            collection.add(
                                documents=[content],
                                embeddings=[embedding],
                                ids=[f"{file}_{i}"]
                            )
                            total_docs += 1
                    except json.JSONDecodeError:
                        print(f"⚠️ Virhe JSON-rivissä tiedostossa: {full_path}")

print(f"✅ Embedding valmis. Indeksoituja dokumentteja: {total_docs}")
