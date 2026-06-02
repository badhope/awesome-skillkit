import secrets
from typing import List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "AI-SKILL"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/skill_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 50

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None

    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    SENTRY_DSN: Optional[str] = None

    STORAGE_TYPE: str = "local"
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DIMENSION: int = 768

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60

    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    @model_validator(mode="after")
    def enforce_jwt_secret_in_production(self) -> "Settings":
        """
        Production must explicitly set JWT_SECRET_KEY. In DEBUG mode we
        transparently generate a strong random key and log a warning so the
        developer can copy it into .env. The key is generated at process start
        and lives only in memory; restarts will produce a new key which is fine
        for dev (forces re-login) and prevents the shipped default
        "your-super-secret-key-change-in-production" from ever being used.
        """
        if self.JWT_SECRET_KEY is None or len(self.JWT_SECRET_KEY.strip()) == 0:
            if self.DEBUG:
                self.JWT_SECRET_KEY = secrets.token_urlsafe(48)
                import logging
                logging.getLogger(__name__).warning(
                    "JWT_SECRET_KEY is not set; generated an ephemeral random key for this "
                    "DEBUG session. All tokens will be invalidated on restart. Set "
                    "JWT_SECRET_KEY in your .env (e.g. `openssl rand -hex 32`) for stable dev."
                )
            else:
                raise ValueError(
                    "JWT_SECRET_KEY environment variable is required in production. "
                    "Generate one with `openssl rand -hex 32` and set it before starting the service."
                )

        weak = {
            "your-super-secret-key-change-in-production",
            "change-this-in-production",
            "change-this-to-a-random-secret-in-production",
            "secret",
            "changeme",
            "password",
            "admin",
        }
        if not self.DEBUG and self.JWT_SECRET_KEY.lower() in weak:
            raise ValueError(
                "JWT_SECRET_KEY is set to a known-weak default. "
                "Generate a strong key with `openssl rand -hex 32`."
            )

        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long. "
                "Generate one with `openssl rand -hex 32`."
            )

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
