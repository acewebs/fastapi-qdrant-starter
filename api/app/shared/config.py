from pydantic import field_validator
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"
    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "documents"
    EMBED_ENGINE: str = "fastembed"
    EMBED_ENGINE_KEY: str | None = None
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}
