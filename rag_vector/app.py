from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA


embedding = OllamaEmbeddings(model="llama3", base_url="http://ollama:11434")
db = Chroma(persist_directory="VectorDB/oamkjournal", embedding_function=embedding)

qa = RetrievalQA.from_chain_type(llm=ChatOllama(model="llama3", base_url="http://ollama:11434"),
                                 retriever=db.as_retriever())

app = FastAPI()

@app.get("/ask")
def ask(q: str):
    return qa.run(q)
