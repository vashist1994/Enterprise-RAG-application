from enterprise_rag.ingestion.pipeline import ingest_documents

if __name__ == "__main__":
    print(f"Successfully indexed {ingest_documents()} chunks.")
