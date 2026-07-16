from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, all overridable via environment variables.

    Every field has a default that works with zero external services beyond
    Postgres, so the service boots and is fully testable without any API key.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://cortex:cortex@localhost:5432/cortex"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_enabled: bool = True

    chunk_size_chars: int = 1000
    chunk_overlap_chars: int = 150

    retrieval_top_k: int = 20
    rerank_top_k: int = 5

    # Optional: when unset, generation falls back to extractive mode automatically.
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_model_openai: str = "gpt-4o-mini"
    llm_model_anthropic: str = "claude-sonnet-5"

    log_level: str = "INFO"
    correlation_id_header: str = "X-Correlation-Id"

    @property
    def generation_mode(self) -> str:
        if self.anthropic_api_key:
            return "anthropic"
        if self.openai_api_key:
            return "openai"
        return "extractive"


@lru_cache
def get_settings() -> Settings:
    return Settings()
