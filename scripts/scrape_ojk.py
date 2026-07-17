"""Script scraping artikel dari sikapiuangmu.ojk.go.id."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_loader import scrape_ojk, save_scraped

SCRAPE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scraped")
SCRAPE_FILE = os.path.join(SCRAPE_DIR, "articles.json")


def main():
    os.makedirs(SCRAPE_DIR, exist_ok=True)
    print("Scraping artikel dari sikapiuangmu.ojk.go.id...")
    docs = scrape_ojk(max_articles=20)
    if docs:
        save_scraped(docs, SCRAPE_FILE)
        print(f"Berhasil menyimpan {len(docs)} artikel ke {SCRAPE_FILE}")
    else:
        print("Tidak ada artikel berhasil di-scrape")


if __name__ == "__main__":
    main()
