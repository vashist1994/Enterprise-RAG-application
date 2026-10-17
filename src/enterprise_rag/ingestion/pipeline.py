from uuid import uuid4
from enterprise_rag.config.settings import get_settings
from enterprise_rag.ingestion.chunking import split_documents
from enterprise_rag.ingestion.loaders import load_documents
from langchain_community.document_loaders import PyPDFLoader
from enterprise_rag.models.embeddings import get_embeddings
from enterprise_rag.retrieval.store import build_and_save_index
from enterprise_rag.observability.logging import get_logger

logger = get_logger(__name__)

def ingest_documents() -> int:
    settings = get_settings()
    documents = load_documents(settings.documents_dir)
    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    build_and_save_index(chunks, get_embeddings())
    logger.info("ingestion_completed", documents=len(documents), chunks=len(chunks))
    return len(chunks)

def ingest_uploaded_pdf(content: bytes, filename: str) -> tuple[int, int]:
    settings = get_settings()
    upload_dir = settings.documents_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}.pdf"
    path.write_bytes(content)
    try:
        documents = PyPDFLoader(str(path)).load()
        if not documents:
            raise ValueError("The PDF contains no readable pages.")
        for document in documents:
            document.metadata["source"] = filename
            document.metadata["file_name"] = filename
        chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
        build_and_save_index(chunks, get_embeddings(), clear_existing=True)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return len(documents), len(chunks)
