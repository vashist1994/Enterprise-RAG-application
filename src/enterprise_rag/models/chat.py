from langchain_google_genai import ChatGoogleGenerativeAI
from enterprise_rag.config.settings import get_settings

def get_chat_model() -> ChatGoogleGenerativeAI:
    s = get_settings()
    return ChatGoogleGenerativeAI(model=s.google_chat_model, google_api_key=s.google_api_key,
                                  temperature=0, timeout=30, max_retries=2)
