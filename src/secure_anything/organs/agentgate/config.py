"""Runtime settings, loaded from environment (see .env.example).

Secrets live here and are never logged. `Settings` is process-wide and cached.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .policy import DEFAULT_POLICY_PATH


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # GitHub App
    github_webhook_secret: str = Field(default="", alias="GITHUB_WEBHOOK_SECRET")
    github_app_id: str = Field(default="", alias="GITHUB_APP_ID")
    github_app_private_key_path: str = Field(default="", alias="GITHUB_APP_PRIVATE_KEY_PATH")
    github_app_installation_id: str = Field(default="", alias="GITHUB_APP_INSTALLATION_ID")
    github_api_base: str = Field(default="https://api.github.com", alias="GITHUB_API_BASE")

    @property
    def github_app_ready(self) -> bool:
        return bool(
            self.github_app_id
            and self.github_app_private_key_path
            and self.github_app_installation_id
        )

    # Datastore
    database_url: str = Field(default="sqlite:///./agentgate.db", alias="DATABASE_URL")

    # Queue
    queue_backend: str = Field(default="memory", alias="QUEUE_BACKEND")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # LLM risk review (optional)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_model: str = Field(default="claude-opus-4-8", alias="LLM_MODEL")

    # Policy
    policy_path: str = Field(
        default=str(DEFAULT_POLICY_PATH), alias="POLICY_PATH"
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def llm_review_enabled(self) -> bool:
        return bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
