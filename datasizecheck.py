from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from collections import deque
import re

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if link is usable
def is_valid_link(href: str) -> bool:
    return (
        href and
        not href.startswith("#") and
        not href.startswith("mailto:") and
        not href.startswith("javascript:")
    )

# Check if link is internal (same domain or relative)
def is_internal_link(base_url: str, link: str) -> bool:
    if not link or not link.startswith(("http", "/")):
        return False
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc

@app.get("/check-url")
def check_url(url: str = Query(...)):
    try:
        response = requests.head(url, timeout=5)
        return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}


#data crawleri annetulle sivustolle. Katsotaan paljon on dataa ja tokeneita. Määrittele montako sivua haluat käydä läpi.
@app.get("/crawl-check-data")
def crawl_check_data(
    url: str = Query(..., description="Root URL to crawl"),
    max_pages: int = Query(500, description="Maximum number of pages to crawl"),
    content_limit: int = Query(200, description="Number of content pages to include")
):
    visited = set()
    to_visit = deque([url])
    all_text = ""
    content_pages = []  # tallennetaan vain sisällölliset sivut (blogit, artikkelit)

    try:
        while to_visit and len(content_pages) < content_limit and len(visited) < max_pages:
            current_url = to_visit.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                resp = requests.get(current_url, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Extract visible page text
                page_text = soup.get_text(separator=' ', strip=True)

                # Vain jos sivulla on riittävästi tekstiä (esim. yli 100 sanaa), pidetään "sisällöllisenä"
                word_count = len(page_text.split())
                if word_count > 100:
                    all_text += page_text + "\n"
                    content_pages.append(current_url)

                # Kerätään lisää linkkejä crawlattavaksi
                for tag in soup.find_all("a", href=True):
                    href = tag["href"]
                    if is_valid_link(href):
                        full_url = urljoin(current_url, href)
                        if is_internal_link(url, full_url) and full_url not in visited:
                            to_visit.append(full_url)

            except Exception:
                continue

        # Lasketaan tilastot
        tokens = len(re.findall(r"\w+", all_text))
        chars = len(all_text)
        chunk_size = 500
        chunk_count = (tokens + chunk_size - 1) // chunk_size
        embedding_dim = 384
        bytes_total = chunk_count * embedding_dim * 4
        mb_total = round(bytes_total / (1024 * 1024), 2)

        return {
            "pages_crawled": len(visited),
            "content_pages_used": len(content_pages),
            "chars": chars,
            "tokens": tokens,
            "estimated_chunks": chunk_count,
            "estimated_size_bytes": bytes_total,
            "estimated_size_mb": mb_total,
            "source_url": url,
            "structure": sorted(content_pages)  # vain sisällölliset sivut
        }

    except Exception as e:
        return {"error": str(e)}


    
    #palvelimen käynnistys: uvicorn datasizecheck:app --reload --port 8000
    #palvelin stop ctrl-c
    #pitää automatisoida jotenkin. Katso tähän sitten ohjeet erikseen, kun muuten toimii.

