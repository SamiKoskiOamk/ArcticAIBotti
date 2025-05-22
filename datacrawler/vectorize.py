'''
Crawlaa annetulta URL-osoitteelta enintään 100 sivua
Poimii tekstin ja pilkkoo sen lauseiksi → yhdistää chunkiksi (500 sanaa)
Laskee embeddingit mallilla all-MiniLM-L6-v2
Tallentaa ne tiedostoon C:\AI-botti\vektrodata\<alikansio>\<timestamp>.jsonl
'''

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests, os, re, json
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer
from datetime import datetime
from collections import deque

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
BASE_DIR = "C:\\AI-botti\\vektrodata"
CHUNK_SIZE = 500
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

# Apufunktiot

def is_valid_link(href: str) -> bool:
    return href and not href.startswith(("#", "mailto:", "javascript:"))

def is_internal_link(base_url: str, link: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc

# Varsinainen vektorointi-endpoint
@app.get("/vectorize")
def vectorize(url: str = Query(...), folder: str = Query(...)):
    try:
        visited = set()
        to_visit = deque([url])
        documents = []
        max_pages = 100

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                resp = requests.get(current_url, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                if len(text.split()) > 50:
                    documents.append(text)

                for tag in soup.find_all("a", href=True):
                    href = tag['href']
                    if is_valid_link(href):
                        full_url = urljoin(current_url, href)
                        if is_internal_link(url, full_url) and full_url not in visited:
                            to_visit.append(full_url)

            except Exception:
                continue

        # Vektorointi ja tallennus
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        out_folder = os.path.join(BASE_DIR, folder)
        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, f"{timestamp}.jsonl")

        with open(out_path, "w", encoding="utf-8") as f:
            for doc in documents:
                sentences = re.split(r'[.!?]\s+', doc)
                chunks = []
                chunk = []
                word_count = 0

                for sentence in sentences:
                    words = sentence.split()
                    word_count += len(words)
                    chunk.append(sentence)
                    if word_count >= CHUNK_SIZE:
                        text_chunk = " ".join(chunk)
                        embedding = model.encode(text_chunk).tolist()
                        f.write(json.dumps({"text": text_chunk, "embedding": embedding}) + "\n")
                        chunk, word_count = [], 0

                if chunk:
                    text_chunk = " ".join(chunk)
                    embedding = model.encode(text_chunk).tolist()
                    f.write(json.dumps({"text": text_chunk, "embedding": embedding}) + "\n")

        return {"pages": len(visited), "chunks": len(documents), "path": out_path}

    except Exception as e:
        return {"error": str(e)}


# Tämä pitää automatisoida sitten, kun bäkkärillä, mutta toistaiseksi näin.. Joku docker tjms.
# käynnistä service: 
# uvicorn vectorize:app --reload --port 8000
