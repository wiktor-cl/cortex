from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "ingestion"

    uploads_dir: str = "/data/uploads"

    ai_service_url: str = "http://localhost:8001"
    gateway_internal_url: str = "http://localhost:8080"
    internal_api_key: str = "change-me-internal-key"

    max_retries: int = 3
    retry_backoff_seconds: list[int] = [10, 30, 60]

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
