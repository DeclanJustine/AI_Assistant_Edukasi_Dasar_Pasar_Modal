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

**CLI (Terminal):**
```bash
python cli.py
```

**Web UI (Next.js + FastAPI):**
```bash
# Terminal 1 - API
python -m uvicorn api.main:app --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Struktur Proyek

```
├── cli.py                   # Terminal client
├── config.py                # Konfigurasi (model, chunk size, dll)
├── api/
│   └── main.py              # FastAPI server
├── scripts/
│   └── build_index.py       # Bangun vector store dari PDF
├── src/
│   ├── rag/
│   │   ├── chain.py         # RAG pipeline utama
│   │   ├── prompts.py       # Prompt untuk LLM
│   │   ├── store.py         # Interface ChromaDB
│   │   └── history.py       # Manajemen chat history per session
│   ├── document/
│   │   ├── loader.py        # Load PDF
│   │   └── splitter.py      # Chunking dokumen
│   └── kuesioner/
│       ├── data.py          # Load data kuesioner
│       └── extract.py       # Ekstrak PDF kuesioner
├── frontend/                # Next.js web UI
├── data/
│   ├── raw/                 # PDF sumber
│   └── kuesioner.json   # Data kuesioner (hasil ekstrak)
├── chroma_db/               # Vector store (auto-generated, jangan di-commit)
└── requirements.txt
```

### Catatan Penting

- File `.env` dan folder `chroma_db/` sudah di-*gitignore* — tidak perlu diatur ulang
- Model embedding (`paraphrase-multilingual-MiniLM-L12-v2`) akan ter-download otomatis saat `build_index.py` pertama kali dijalankan
- Default retriever: similarity search dengan k=6
- Semua proses berjalan lokal — tidak perlu koneksi internet setelah Ollama dan embedding model ter-download
