from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: str = Field(min_length=1)
    google_chat_model: str = "gemini-3.8-flash"
    google_embedding_model: str = "gemini-embedding-2-flash"
    pinecone_api_key: str = Field(min_length=1)
    pinecone_index_name: str = "enterprise-rag"
    pinecone_namespace: str = "enterprise-rag"
    app_env: str = "local"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    documents_dir: Path = Path("data/documents/uploads")
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    retrieval_k: int = Field(default=5, gt=0)
    max_question_length: int = Field(default=10000, gt=0)
    max_upload_size_mb: int = Field(default=20, gt=0)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def validate_chunking(self) -> None:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_chunking()
    return settings
