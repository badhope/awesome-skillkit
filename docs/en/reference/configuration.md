# Configuration reference

The backend's configuration is a single Pydantic v2 `Settings` class
in `backend/app/core/config.py`. It is loaded from environment
variables (with a `.env` file as fallback) at process start.

## Class

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    ...
```

All fields are upper-case by convention. `case_sensitive=True` means
the env var must match the field name exactly.

## Sections

| Section     | Fields                                              |
|-------------|-----------------------------------------------------|
| Application | `APP_NAME`, `APP_VERSION`, `DEBUG`, `API_PREFIX`    |
| Database    | `DATABASE_URL`, `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`, `DATABASE_POOL_TIMEOUT`, `DATABASE_POOL_RECYCLE` |
| Redis       | `REDIS_URL`, `REDIS_POOL_SIZE`                      |
| Qdrant      | `QDRANT_URL`, `QDRANT_API_KEY`                      |
| Auth        | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` |
| CORS        | `BACKEND_CORS_ORIGINS`                              |
| Storage     | `STORAGE_TYPE`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_REGION`, `S3_ENDPOINT_URL` |
| Embedding   | `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION`            |
| Logging     | `LOG_LEVEL`, `LOG_FORMAT`                           |
| Rate limit  | `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_WINDOW`           |
| Sentry      | `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILES_SAMPLE_RATE` |
| Admin       | `ADMIN_EMAIL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_FULL_NAME` |

## Validators

### `BACKEND_CORS_ORIGINS`

Accepts either a list (when set in Python) or a comma-separated
string (when set as an env var).

```bash
# Comma-separated
BACKEND_CORS_ORIGINS=https://app.example.com,https://staging.example.com
```

### `enforce_jwt_secret_in_production`

A `@model_validator(mode="after")` that:

- In production: refuses to start if `JWT_SECRET_KEY` is missing,
  shorter than 32 chars, or matches a known-weak default
- In debug: generates an ephemeral random key and logs a warning

See [ADR 008](../adr/008-fail-fast-secrets.md) for the rationale.

## Loading

The settings are loaded once and cached:

```python
from app.core.config import get_settings, settings

# Anywhere in the code:
db_url = settings.DATABASE_URL

# Or, in a FastAPI dependency:
def my_route(settings: Settings = Depends(get_settings)):
    ...
```

The cache is `functools.lru_cache`, so a test that mutates env vars
needs to call `get_settings.cache_clear()` before re-reading.

## Where to go from here

- [Environment variables](environment.md) — every variable, every
  default, every constraint
- [Configuration (Getting started)](../getting-started/configuration.md)
- [Source](https://github.com/badhope/AI-SKILL/blob/main/backend/app/core/config.py)
