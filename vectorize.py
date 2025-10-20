# vectorize.py
"""
FastAPI-palvelu, joka crawlaa annetusta URL:sta enintään 100 sivua (vain sisäiset linkit),
poimii näkyvän tekstin (>50 sanaa), pilkkoo sen ~500 sanan chunkkeihin, laskee embeddingit
mallilla sentence-transformers/all-MiniLM-L6-v2 ja tallentaa jokaisen chunkin JSONL-rivinä:

{
  "text": "...",
  "embedding": [...],
  "source_url": "https://example.com/page",
  "doc_index": 0,
  "chunk_index": 0,
  "timestamp": "YYYY-MM-DD-HHMMSS"
}

Tiedosto kirjoitetaan polkuun:
E:\\AI-botti\\vektordataJsonl\\<folder>\\<timestamp>.jsonl

Käynnistys (esim. kehityksessä):
cd ~/Intrabot 
uvicorn vectorize:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import os
import re
import json
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer
from datetime import datetime
from collections import deque
from typing import Dict, List

app = FastAPI()

# CORS salli yhteydet frontista
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asetukset
BASE_DIR = "E:\\AI-botti\\vektordataJsonl"
CHUNK_SIZE = 500  # sanoja/chunk
MODEL_NAME = "all-MiniLM-L6-v2"
MAX_PAGES = 100
MIN_WORDS_PER_PAGE = 50
REQUEST_TIMEOUT = 10  # sekuntia

model = SentenceTransformer(MODEL_NAME)

# Apufunktiot
def is_valid_link(href: str) -> bool:
    return href and not href.startswith(("#", "mailto:", "javascript:"))

def is_internal_link(base_url: str, link: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc

def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if not is_valid_link(href):
            continue
        full_url = urljoin(base_url, href)
        links.append(full_url)
    return links

# Varsinainen vektorointi-endpoint
@app.get("/vectorize")
def vectorize(url: str = Query(..., description="Lähtö-URL crawlausprosessille"),
              folder: str = Query(..., description="Alikansio BASE_DIR:n alle JSONL-tiedostolle")):
    try:
        visited = set()
        to_visit = deque([url])

        # Talletetaan sivut muodossa {"url": ..., "text": ..., "doc_index": ...}
        documents: List[Dict] = []
        doc_index = 0

        while to_visit and len(visited) < MAX_PAGES:
            current_url = to_visit.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                resp = requests.get(current_url, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200 or not resp.text:
                    continue

                text = page_text(resp.text)
                if len(text.split()) > MIN_WORDS_PER_PAGE:
                    documents.append({"url": current_url, "text": text, "doc_index": doc_index})
                    doc_index += 1

                # Lisää sisäiset linkit jonoon
                for full_url in extract_links(current_url, resp.text):
                    if is_internal_link(url, full_url) and full_url not in visited:
                        to_visit.append(full_url)

            except Exception:
                # Jatketaan hiljaisesti virheistä huolimatta yksittäisten sivujen osalta
                continue

        # Vektorointi ja tallennus
        run_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        out_folder = os.path.join(BASE_DIR, folder)
        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, f"{run_timestamp}.jsonl")

        total_chunks = 0
        with open(out_path, "w", encoding="utf-8") as f:
            for doc in documents:
                sentences = re.split(r"[.!?]\s+", doc["text"])
                chunk: List[str] = []
                word_count = 0
                chunk_index = 0

                for sentence in sentences:
                    if not sentence:
                        continue
                    words = sentence.split()
                    word_count += len(words)
                    chunk.append(sentence)
                    if word_count >= CHUNK_SIZE:
                        text_chunk = " ".join(chunk).strip()
                        if text_chunk:
                            embedding = model.encode(text_chunk).tolist()
                            f.write(json.dumps({
                                "text": text_chunk,
                                "embedding": embedding,
                                "source_url": doc["url"],
                                "doc_index": doc["doc_index"],
                                "chunk_index": chunk_index,
                                "timestamp": run_timestamp
                            }, ensure_ascii=False) + "\n")
                            chunk_index += 1
                            total_chunks += 1
                        chunk, word_count = [], 0

                # Jäljelle jäänyt loppupala viimeiseksi chunkiksi
                if chunk:
                    text_chunk = " ".join(chunk).strip()
                    if text_chunk:
                        embedding = model.encode(text_chunk).tolist()
                        f.write(json.dumps({
                            "text": text_chunk,
                            "embedding": embedding,
                            "source_url": doc["url"],
                            "doc_index": doc["doc_index"],
                            "chunk_index": chunk_index,
                            "timestamp": run_timestamp
                        }, ensure_ascii=False) + "\n")
                        chunk_index += 1
                        total_chunks += 1

        return {
            "pages": len(visited),           # kaikki vieraillut sivut (myös alle 50 sanan)
            "documents": len(documents),     # kelpuutetut sivut (> 50 sanaa)
            "chunks": total_chunks,          # luotujen chunkkien määrä
            "path": out_path
        }

    except Exception as e:
        return {"error": str(e)}


'''
Mitä tämä tekee?
1. Crawl
Lähtee annetusta url-osoitteesta ja käy läpi enintään 100 sivua saman domainin sisältä.
Hylkää ankkurit, mailto: ja javascript:-linkit.
Ottaa sivusta näkyvän tekstin (BeautifulSoup get_text), ja hyväksyy sivun jos siinä on > 50 sanaa.

2. Tekstin esikäsittely & paloittelu
Jakaa sivutekstin lauseiksi (regex [.!?]\s+).
Kerää lauseita ~500 sanaan asti → muodostaa chunkin.
Jäljelle jäävä loppu muodostaa viimeisen chunkin.

3. Vektorointi (embedding)
Käyttää mallia sentence-transformers/all-MiniLM-L6-v2 (384-ulotteinen embedding).
Laskee embeddingin jokaiselle chunkille: model.encode(text_chunk).

4. Tallennus
Kirjoittaa JSONL-tiedostoon rivin per chunk:
{"text": "<chunkin teksti>", "embedding": [0.123, -0.045, ...]}

Tallennuspolku:
E:\AI-botti\vektordata\<folder parametri web-sivulta>\ <timestamp>.jsonl
(timestamp muodossa YYYY-MM-DD-HHMMSS)


VectorDB (vektoritietokanta) on RAG-järjestelmän “muisti” — se tallentaa tekstien merkityssisällöt 
embedding-muodossa ja mahdollistaa niiden nopean semanttisen haun.
Esimerkkitietue VectorDB:ssä:
{
  "id": "chunk_00045",
  "embedding": [0.123, -0.045, 0.678, ...],
  "metadata": {
    "source_url": "https://www.oamk.fi/fi/hankkeet/tekoaly",
    "doc_index": 5,
    "chunk_index": 2,
    "timestamp": "2025-10-20-141532"
  },
  "text": "Oamk on mukana useissa tekoälyyn ja koneoppimiseen liittyvissä kehityshankkeissa, 
  joiden tavoitteena on edistää koulutusta ja alueellista innovaatiotoimintaa."
}
Tehokkuuden syyt:

Merkityspohjainen haku:
Hakee sisältöä merkityksen eikä pelkkien sanojen perusteella.
Esim. kysymykset “Oamkin tekoälyhankkeet” ja “AI-projektit Oamkissa” löytävät samat dokumentit.

Nopea lähimmän naapurin haku:
VectorDB:t (kuten ChromaDB, FAISS, Milvus) käyttävät tehokkaita ANN (Approximate Nearest Neighbor) -algoritmeja, 
jotka löytävät relevantit embeddingit miljoonien joukosta sekunneissa.

Joustava skaalaus:
Voi indeksoida tuhansia tai miljoonia tekstipaloja ilman, että mallia tarvitsee uudelleenkouluttaa.

Erottelu & metadata:
Jokaisella embeddingillä voi olla kontekstia — kuten lähde-URL, aikaleima, dokumenttityyppi 
— mikä tekee hakutuloksista tarkempia.


Embedding
Embedding on tapa kuvata tekstin (tai kuvan, äänen, tms.) merkitys numeerisesti — eli muuttaa sanat vektoriksi: pitkäksi numerosarjaksi, 
joka kertoo mitä teksti tarkoittaa, ei vain mitä sanoja siinä on.
“Oamk on ammattikorkeakoulu Oulussa.”
[0.14, -0.23, 0.05, 0.48, -0.11, 0.09, -0.30, 0.22, 0.01, 0.17, ...]
Embedding-mallin idea on, että merkitykseltään samankaltaiset tekstit sijoittuvat lähelle toisiaan tässä 
monidimensionaalisessa “vektoriavaruudessa”.

embeddingit mahdollistavat semanttisen haun — hakemisen merkityksen perusteella, ei vain sanojen.

'''

