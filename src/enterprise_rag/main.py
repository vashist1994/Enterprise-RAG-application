from fastapi import FastAPI
from enterprise_rag.api.routes import router
from enterprise_rag.config.settings import get_settings
from enterprise_rag.observability.logging import configure_logging

configure_logging()
settings = get_settings()
app = FastAPI(title="Enterprise RAG API", version="0.1.0",
              description="RAG service orchestrated by LangGraph.")
app.include_router(router, prefix=settings.api_prefix, tags=["RAG"])

@app.get("/health", tags=["Operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
