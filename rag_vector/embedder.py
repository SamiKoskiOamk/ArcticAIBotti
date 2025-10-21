from pathlib import Path
import json
from langchain_core.documents import Document
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
import chromadb

print("🔧 embedder.py aloitettu")

base_dir = Path("/mnt/e/AI-botti/vektordataJsonl")
jsonl_files = list(base_dir.rglob("*.jsonl"))

if not jsonl_files:
    print("❌ Yhtään .jsonl-tiedostoa ei löytynyt hakemistosta VectorDB/")
    exit(1)

for jsonl_path in jsonl_files:
    print(f"\n📂 Käsitellään tiedosto: {jsonl_path}")
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
        continue

    print(f"📄 Dokumentteja ladattu: {len(documents)}")
    if not documents:
        continue

    # Embedding-client
    print("🧠 Luodaan embedding-client...")
    embedding = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://ollama-container:11434"
    )
    print("✅ Yhteys Ollama-palveluun kunnossa.")

    # Lasketaan embeddingit
    print("🔁 Lasketaan embeddingit...")
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    embeddings = embedding.embed_documents(texts)
    print("✅ Embeddingit saatu.")

    # Tallennetaan ChromaDB:hen – käytetään tiedoston hakemistoa tietokannan polkuna
    target_dir = jsonl_path.parent
    print(f"💾 Tallennetaan tietokantaan: {target_dir}")
    client = chromadb.PersistentClient(path=str(target_dir))
    collection_name = target_dir.name  # esim. "oamkjournal"

    collection = client.get_or_create_collection(name=collection_name)
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=[f"doc_{i}" for i in range(len(texts))]
    )

    print(f"✅ Tiedosto {jsonl_path.name} käsitelty ja tallennettu.")

print("\n🎉 Kaikki .jsonl-tiedostot käsitelty.")
