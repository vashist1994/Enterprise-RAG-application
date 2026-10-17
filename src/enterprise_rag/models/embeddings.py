from langchain_google_genai import GoogleGenerativeAIEmbeddings
from enterprise_rag.config.settings import get_settings

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    s = get_settings()
    return GoogleGenerativeAIEmbeddings(model=s.google_embedding_model,
                                        google_api_key=s.google_api_key)
