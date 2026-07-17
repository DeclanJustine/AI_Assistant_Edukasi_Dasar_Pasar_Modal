# AI Assistant Edukasi Pasar Modal

Asisten berbasis **Retrieval-Augmented Generation (RAG)** untuk menjawab pertanyaan seputar Pasar Modal Indonesia, menggunakan buku **"Buku 3 - Pasar Modal"** sebagai sumber pengetahuan.

### Fitur

- Tanya jawab interaktif via **Streamlit** (Web UI) atau **CLI**
- History-aware: bisa menanyakan follow-up tanpa kehilangan konteks
- Verifikasi jawaban otomatis (post-generation hallucination check)
- Normalisasi input Bahasa Indonesia (ejaan baku/tidak baku, misal "reksadana" → "reksa dana")
- Sumber tunggal: 1 PDF (268 halaman, 1073 chunk setelah diproses)

### Prasyarat

- Python 3.10+
- Docker (untuk menjalankan Ollama)
- RAM 8GB+ (LLM ~4.7GB + model embedding ~470MB)

### 1. Clone & Setup

```bash
git clone https://github.com/DeclanJustine/AI_Assistant_Edukasi_Dasar_Pasar_Modal.git
cd AI_Assistant_Edukasi_Dasar_Pasar_Modal
python -m venv .venv

# Linux / Mac
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Setup Ollama (via Docker)

```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec -it ollama ollama pull qwen3:8b
```

Pastikan Ollama berjalan: `curl http://localhost:11434`

### 3. Siapkan PDF

Letakkan file PDF di `data/raw/` (sudah ada `Buku 3 - Pasar Modal.pdf` secara default).

### 4. Bangun Vector Index

```bash
python scripts/build_index.py
```

Proses: membaca PDF → chunking (chunk_size=500, overlap=100) → embedding (paraphrase-multilingual-MiniLM-L12-v2) → simpan ke ChromaDB di folder `chroma_db/`.

### 5. Jalankan

**Streamlit (Web UI):**
```bash
streamlit run app/main.py
```

**CLI (Terminal):**
```bash
python cli.py
```

### Struktur Proyek

```
├── app/main.py              # Streamlit web UI
├── cli.py                   # Terminal client
├── config.py                # Konfigurasi (model, chunk size, dll)
├── scripts/
│   ├── build_index.py       # Bangun vector store dari PDF
│   └── scrape_ojk.py        # (opsional) scrape artikel OJK
├── src/
│   ├── document_loader.py   # Load PDF
│   ├── text_splitter.py     # Chunking dokumen
│   ├── vector_store.py      # Interface ChromaDB
│   ├── rag_chain.py         # RAG pipeline utama
│   ├── prompt_templates.py  # Prompt untuk LLM
│   ├── history.py           # Manajemen chat history per session
│   └── embeddings.py        # Inisialisasi embedding model
├── data/
│   └── raw/                 # PDF sumber
├── chroma_db/               # Vector store (auto-generated, jangan di-commit)
└── requirements.txt
```

### Catatan Penting

- File `.env` dan folder `chroma_db/` sudah di-*gitignore* — tidak perlu diatur ulang
- Model embedding (`paraphrase-multilingual-MiniLM-L12-v2`) akan ter-download otomatis saat `build_index.py` pertama kali dijalankan
- Default retriever: similarity search dengan k=6
- Semua proses berjalan lokal — tidak perlu koneksi internet setelah Ollama dan embedding model ter-download
