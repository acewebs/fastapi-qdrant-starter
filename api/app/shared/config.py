from pydantic import field_validator
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "documents"
    EMBED_ENGINE: str = "auto"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "text-embedding-3-large"
    OPENAI_DIMENSIONS: int = 1024

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def embed_engine(self) -> str:
        engine = self.EMBED_ENGINE.lower()
        if engine != "auto":
            return engine
        return "openai" if self.OPENAI_API_KEY else "fastembed"

    @property
    def embedding_dimensions(self) -> int:
        return self.OPENAI_DIMENSIONS if self.embed_engine == "openai" else self.EMBEDDING_DIM

    @property
    def embedding_model(self) -> str:
        return self.OPENAI_MODEL if self.embed_engine == "openai" else self.EMBEDDING_MODEL

    model_config = {"env_file": ".env", "extra": "ignore"}
