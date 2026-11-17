from app.shared.config import BaseAppSettings


class Settings(BaseAppSettings):
    APP_NAME: str = "Vector Knowledge Base API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_KEY: str | None = None
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
