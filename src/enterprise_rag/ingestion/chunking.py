from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents: list[Document], chunk_size: int,
                    chunk_overlap: int) -> list[Document]:
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Require chunk_size > chunk_overlap >= 0.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                               chunk_overlap=chunk_overlap,
                                               add_start_index=True)
    return splitter.split_documents(documents)
