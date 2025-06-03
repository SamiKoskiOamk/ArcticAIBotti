from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔄 Dynaaminen kielituki – ei pakoteta kieltä, vaan ohjeistetaan seuraavasti:
DYNAMIC_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Käyttäjän kysymys on alla. Vastaa samalla kielellä kuin kysymys. Käytä alla olevaa kontekstia vastauksesi tukena.

Konteksti:
{context}

Kysymys:
{question}

Vastaus:
"""
)

embedding = OllamaEmbeddings(model="llama3", base_url="http://ollama-container:11434")
db = Chroma(persist_directory="VectorDB/oamkjournal", embedding_function=embedding)

qa = RetrievalQA.from_chain_type(
    llm=ChatOllama(model="llama3", base_url="http://ollama-container:11434"),
    retriever=db.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": DYNAMIC_PROMPT}
)

@app.get("/ask")
def ask(q: str):
    try:
        answer = qa.run(q)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virhe: {str(e)}")
