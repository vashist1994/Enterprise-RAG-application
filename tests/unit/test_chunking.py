import pytest
from langchain_core.documents import Document
from enterprise_rag.ingestion.chunking import split_documents

def test_chunking_retains_metadata():
    docs = [Document(page_content="enterprise RAG " * 100, metadata={"source": "x.txt"})]
    chunks = split_documents(docs, 100, 10)
    assert len(chunks) > 1
    assert all(c.metadata["source"] == "x.txt" for c in chunks)

def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        split_documents([Document(page_content="abc")], 10, 10)
