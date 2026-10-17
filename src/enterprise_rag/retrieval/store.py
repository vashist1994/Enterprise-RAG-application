from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from enterprise_rag.config.settings import get_settings

def _get_vector_store(embeddings: Embeddings) -> PineconeVectorStore:
    settings = get_settings()
    return PineconeVectorStore(index_name=settings.pinecone_index_name,
                               embedding=embeddings,
                               pinecone_api_key=settings.pinecone_api_key,
                               namespace=settings.pinecone_namespace)

def build_and_save_index(chunks: list[Document], embeddings: Embeddings,
                         clear_existing: bool = True) -> None:
    if not chunks:
        raise ValueError("Cannot index an empty chunk list.")
    vector_store = _get_vector_store(embeddings)
    if clear_existing:
        vector_store.delete(delete_all=True)
    vector_store.add_documents(chunks)

def retrieve(query: str, k: int | None = None) -> list[Document]:
    if not query.strip():
        return []
    from enterprise_rag.models.embeddings import get_embeddings
    s = get_settings()
    return _get_vector_store(get_embeddings()).similarity_search(
        query, k=k or s.retrieval_k)
