"""Application settings."""

import os
import secrets
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    class Config:  # noqa: WPS431
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            return cls.json_loads(raw_val)  # type: ignore

    # base kwargs
    DEBUG: bool = False

    # database
    POSTGRES_DSN: str
    SQL_DEBUG: bool = False
    POSTGRES_PASSWORD: str = "postgres"  # Added for Docker compatibility

    # redis
    REDIS_DSN: str
    CONNECTION_POOL_SIZE: int = 10

    # healthcheck
    WORKER_TIMEOUT_SEC: float = 4
    
    # JWT Authentication
    SECRET_KEY: str = Field(
        default_factory=lambda: os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32),
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


def get_settings() -> AppSettings:
    """
    Get application settings.
    
    This function is used to get the application settings, allowing for
    environment-specific overrides and mocking in tests.
    
    Returns:
        AppSettings: Application settings
    """
    return AppSettings()


settings = get_settings()
