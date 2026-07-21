import os

LLM_MODEL = "qwen3:8b"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "pasar_modal"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
RETRIEVER_K = 10
