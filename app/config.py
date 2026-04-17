"""Application settings (12-factor via environment)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TCL Ticket API"
    debug: bool = False

    database_url: str = Field(
        default="mysql+asyncmy://app:app@localhost:3306/TestDB",
        description="SQLAlchemy async URL for MySQL (asyncmy driver).",
    )

    jwt_secret_key: str = Field(default="change-me-in-production-use-openssl-rand-hex-32")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Demo user for JWT issuance (replace with IdP / user store in production)
    demo_username: str = "demo"
    demo_password: str = "demo"

    enable_auth: bool = Field(
        default=True,
        description="When False, ticket routes skip JWT (local/dev only).",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = False

    rate_limit_default: str = "60/minute"
    rate_limit_burst: str = "120/minute"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors(cls, v: str | list[str]) -> list[str]:
        """Env may be JSON (pydantic-settings) or a comma-separated string."""
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return ["*"]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
