"""Build/rebuild vector store dari PDF dan artikel web."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DIR
from src.document_loader import load_pdfs
from src.text_splitter import split_documents
from src.vector_store import add_documents


def main():
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
    scraped_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scraped", "articles.json")

    print("=== Building Vector Store ===\n")

    all_docs = []

    print("1. Memuat PDF...")
    if os.path.exists(pdf_dir) and os.listdir(pdf_dir):
        pdfs = load_pdfs(pdf_dir)
        print(f"   Ditemukan {len(pdfs)} halaman PDF")
        all_docs.extend(pdfs)
    else:
        print("   Tidak ada PDF ditemukan")

    # print("\n2. Scraping artikel OJK...")
    # web_docs = scrape_ojk(max_articles=10)
    # if web_docs:
    #     print(f"   Berhasil scrape {len(web_docs)} artikel")
    #     save_scraped(web_docs, scraped_path)
    #     all_docs.extend(web_docs)
    # else:
    #     print("   Memuat artikel yang sudah di-scrape...")
    #     all_docs.extend(load_scraped(scraped_path))

    if not all_docs:
        print("\nTidak ada dokumen ditemukan!")
        return

    print(f"\nTotal dokumen: {len(all_docs)}")

    print("\n3. Splitting dokumen...")
    chunks = split_documents(all_docs)
    print(f"   Total chunks: {len(chunks)}")

    print("\n4. Membuat embedding dan menyimpan ke ChromaDB...")
    add_documents(chunks)
    print(f"   Tersimpan di: {CHROMA_DIR}")

    print("\n=== Selesai! ===")


if __name__ == "__main__":
    main()
