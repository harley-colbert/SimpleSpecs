"""Application configuration settings."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

try:  # pragma: no cover - fallback for environments without pydantic-settings
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover
    from pydantic import BaseModel as BaseSettings  # type: ignore

from pydantic import Field


PdfEngine = Literal["native", "mineru", "auto"]


class Settings(BaseSettings):
    """Runtime settings loaded from env."""

    OPENROUTER_API_KEY: str | None = Field(default=None, env="OPENROUTER_API_KEY")
    LLAMACPP_URL: str = Field(default="http://localhost:8080", env="LLAMACPP_URL")
    DB_URL: str = Field(default="sqlite:///./simplespecs.db", env="DB_URL")
    ARTIFACTS_DIR: str = Field(default="artifacts", env="ARTIFACTS_DIR")
    ALLOW_ORIGINS: list[str] = Field(default_factory=lambda: ["*"], env="ALLOW_ORIGINS")
    MAX_FILE_MB: int = Field(default=50, env="MAX_FILE_MB")
    PDF_ENGINE: PdfEngine = Field(default="native", env="PDF_ENGINE")
    MINERU_ENABLED: bool = Field(default=False, env="MINERU_ENABLED")
    MINERU_MODEL_OPTS: dict[str, Any] = Field(default_factory=dict, env="MINERU_MODEL_OPTS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()
