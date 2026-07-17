from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import EMBEDDING_MODEL, CHROMA_DIR, COLLECTION_NAME, RETRIEVER_K


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_vectorstore(persist_dir: str = CHROMA_DIR) -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
    )


def add_documents(chunks, persist_dir: str = CHROMA_DIR):
    vs = get_vectorstore(persist_dir)
    vs.add_documents(chunks)
    return vs


def get_retriever(persist_dir: str = CHROMA_DIR):
    return get_vectorstore(persist_dir).as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6},
    )
