from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pathlib

# Kaikki .jsonl-tiedostot VectorDB-hakemistosta ja alihakemistoista
jsonl_files = list(pathlib.Path("VectorDB").rglob("*.jsonl"))

# Ladataan dokumentit
documents = []
for file_path in jsonl_files:
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".content",
        text_content=False,
        metadata_func=lambda x, _: {"source": x.get("source", "unknown")},
    )
    documents.extend(loader.load())

# Jaetaan paloihin
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(documents)

# Luodaan Chroma-tietokanta
db = Chroma.from_documents(
    docs,
    embedding=OllamaEmbeddings(model="llama3"),
    persist_directory="./chroma_db",
    client_settings=Chroma.get_default_client_settings()  # uusi tapa
)

db.persist()
