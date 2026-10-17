from enterprise_rag.retrieval import store

def test_vector_store_uses_namespace_from_settings(monkeypatch):
    settings = type("Settings", (), {
        "pinecone_index_name": "test-index",
        "pinecone_api_key": "test-key",
        "pinecone_namespace": "configured-namespace",
    })()
    monkeypatch.setattr(store, "get_settings", lambda: settings)
    monkeypatch.setattr(store, "PineconeVectorStore", lambda **kwargs: kwargs)

    result = store._get_vector_store(embeddings=object())

    assert result["namespace"] == "configured-namespace"
    assert result["index_name"] == "test-index"