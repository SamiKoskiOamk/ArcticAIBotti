from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

# FastAPI-käyttöliittymä
app = FastAPI()

# Pysyvä tietokanta
db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OllamaEmbeddings(model="llama3"),
    client_settings=Chroma.get_default_client_settings()
)

# Hakuagentti
qa_chain = RetrievalQA.from_chain_type(
    llm=Ollama(model="llama3"),
    retriever=db.as_retriever(),
    return_source_documents=False
)

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: Question):
    try:
        response = qa_chain.run(request.question)
        return {"answer": response}
    except Exception as e:
        return {"error": str(e)}
