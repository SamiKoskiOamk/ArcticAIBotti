from pathlib import Path
import json
from langchain_core.documents import Document
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
import chromadb

print("🔧 embedder.py aloitettu")

vector_dir = "VectorDB/oamkjournal"
jsonl_path = Path(vector_dir) / "2025-05-13-095308.jsonl"

print(f"📂 Ladataan tiedosto: {jsonl_path}")
documents = []
try:
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
                content = obj.get("text", "")
                metadata = {
                    k: v for k, v in obj.items()
                    if k != "text" and isinstance(v, (str, int, float, bool, type(None)))
                }
                if not metadata:
                    metadata = {"source": "unknown"}
                documents.append(Document(page_content=content, metadata=metadata))
            except json.JSONDecodeError as e:
                print(f"⚠️ Virhe JSON-rivillä {i}: {e}")
except FileNotFoundError:
    print(f"❌ Tiedostoa ei löytynyt: {jsonl_path}")
    exit(1)

print(f"📄 Dokumentteja ladattu: {len(documents)}")

# Embedding-client
print("🧠 Luodaan embedding-client...")
embedding = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama-container:11434"
)
print("✅ Yhteys Ollama-palveluun kunnossa.")

# Luodaan embeddit
print("🔁 Lasketaan embeddingit...")
texts = [doc.page_content for doc in documents]
metadatas = [doc.metadata for doc in documents]

embeddings = embedding.embed_documents(texts)
print("✅ Embeddingit saatu.")

# Tallennus suoraan ChromaDB:hen
print("💾 Luodaan Chroma-tietokanta suoraan...")
client = chromadb.PersistentClient(path=vector_dir)
collection = client.get_or_create_collection(name="oamkjournal")

# Lisätään tiedot
collection.add(
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=[f"doc_{i}" for i in range(len(texts))]
)

print("✅ Vektoritallennus valmis.")
