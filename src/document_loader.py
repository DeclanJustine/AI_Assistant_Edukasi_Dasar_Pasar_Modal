import os
import json
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_core.documents import Document


def load_pdfs(directory: str) -> list[Document]:
    loader = DirectoryLoader(
        directory,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    return loader.load()


def scrape_ojk(max_articles: int = 20) -> list[Document]:
    url = "https://sikapiuangmu.ojk.go.id/"
    headers = {"User-Agent": "Mozilla/5.0"}
    docs = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/Article/" in href or "/article/" in href:
                full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                if full_url not in links:
                    links.append(full_url)

        for link in links[:max_articles]:
            try:
                art_resp = requests.get(link, headers=headers, timeout=15)
                art_resp.raise_for_status()
                art_soup = BeautifulSoup(art_resp.text, "html.parser")

                title_tag = art_soup.find("h1") or art_soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                body = art_soup.find("article") or art_soup.find("div", class_="content") or art_soup.find("main")
                text = body.get_text(separator="\n", strip=True) if body else ""

                if len(text) > 100:
                    docs.append(Document(
                        page_content=text,
                        metadata={"source": link, "title": title, "type": "web"},
                    ))
            except Exception:
                continue
    except Exception as e:
        print(f"Gagal scrape OJK: {e}")

    return docs


def save_scraped(docs: list[Document], path: str):
    data = [{"page_content": d.page_content, "metadata": d.metadata} for d in docs]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_scraped(path: str) -> list[Document]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in data]
