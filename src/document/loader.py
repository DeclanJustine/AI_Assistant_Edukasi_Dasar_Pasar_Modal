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
