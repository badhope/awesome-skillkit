# Environment variables

Every environment variable recognized by the backend, with its
default, type, and a short description.

## Application

| Variable       | Type    | Default       | Description                                          |
|----------------|---------|---------------|------------------------------------------------------|
| `APP_NAME`     | `str`   | `AI-SKILL`    | Display name; used in the OpenAPI title             |
| `APP_VERSION`  | `str`   | (from code)   | Display version; surfaced by `GET /health`          |
| `DEBUG`        | `bool`  | `false`       | `true` = permissive startup, verbose logging, etc.  |
| `API_PREFIX`   | `str`   | `/api/v1`     | Mount prefix for all API routes                     |
| `ENVIRONMENT`  | `str`   | `production`  | Free-form label for the deployment                  |

## Database

| Variable                 | Type   | Default                                              | Description |
|--------------------------|--------|------------------------------------------------------|-------------|
| `DATABASE_URL`           | `str`  | `postgresql+asyncpg://user:pass@localhost:5432/skill_db` | asyncpg DSN |
| `DATABASE_POOL_SIZE`     | `int`  | 20                                                   | Connection pool size |
| `DATABASE_MAX_OVERFLOW`  | `int`  | 10                                                   | Extra connections allowed under load |
| `DATABASE_POOL_TIMEOUT`  | `int`  | 30                                                   | Seconds to wait for a connection |
| `DATABASE_POOL_RECYCLE`  | `int`  | 3600                                                 | Seconds before a connection is recycled |

## Redis

| Variable         | Type   | Default                    | Description |
|------------------|--------|----------------------------|-------------|
| `REDIS_URL`      | `str`  | `redis://localhost:6379/0` | redis-py DSN |
| `REDIS_POOL_SIZE`| `int`  | 50                         | Max connections |

## Qdrant

| Variable         | Type   | Default                    | Description |
|------------------|--------|----------------------------|-------------|
| `QDRANT_URL`     | `str`  | `http://localhost:6333`    | Qdrant HTTP endpoint |
| `QDRANT_API_KEY` | `str?` | None                       | Optional API key for managed Qdrant Cloud |

## Authentication

| Variable                          | Type   | Default                | Description |
|-----------------------------------|--------|------------------------|-------------|
| `JWT_SECRET_KEY`                  | `str?` | None (auto in DEBUG)   | HS256 signing key. **Required** in production, ≥ 32 chars, not on the weak denylist. |
| `JWT_ALGORITHM`                   | `str`  | `HS256`                | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`     | `int`  | 30                     | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS`       | `int`  | 7                      | Refresh token lifetime |

## Admin bootstrap

| Variable           | Type   | Default                  | Description |
|--------------------|--------|--------------------------|-------------|
| `ADMIN_EMAIL`      | `str`  | `admin@ai-skill.local`   | Email of the seeded superuser |
| `ADMIN_USERNAME`   | `str`  | `admin`                  | Username of the seeded superuser |
| `ADMIN_PASSWORD`   | `str?` | None                     | Password of the seeded superuser. **Required** in production. |
| `ADMIN_FULL_NAME`  | `str`  | `System Administrator`   | Display name of the seeded superuser |

## CORS

| Variable                 | Type        | Default                  | Description |
|--------------------------|-------------|--------------------------|-------------|
| `BACKEND_CORS_ORIGINS`   | `list[str]` | `["http://localhost:3000"]` | Comma-separated allow-list of origins |

Wildcard is **not** supported because the API sets
`allow_credentials=true`.

## Storage

| Variable            | Type   | Default      | Description |
|---------------------|--------|--------------|-------------|
| `STORAGE_TYPE`      | `str`  | `local`      | `local` or `s3` |
| `S3_BUCKET`         | `str?` | None         | Required when `STORAGE_TYPE=s3` |
| `S3_ACCESS_KEY`     | `str?` | None         | S3 access key |
| `S3_SECRET_KEY`     | `str?` | None         | S3 secret key |
| `S3_REGION`         | `str`  | `us-east-1`  | S3 region |
| `S3_ENDPOINT_URL`   | `str?` | None         | For S3-compatible (MinIO, R2) — set the endpoint |

## Embedding

| Variable               | Type   | Default                                  | Description |
|------------------------|--------|------------------------------------------|-------------|
| `EMBEDDING_MODEL`      | `str`  | `sentence-transformers/all-mpnet-base-v2` | HuggingFace model id |
| `EMBEDDING_DIMENSION`  | `int`  | 768                                      | Output dimension (must match the model) |

## Logging

| Variable     | Type   | Default | Description |
|--------------|--------|---------|-------------|
| `LOG_LEVEL`  | `str`  | `INFO`  | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |
| `LOG_FORMAT` | `str`  | `json`  | `json` (prod) or `console` (dev) |

## Rate limiting

| Variable              | Type | Default | Description |
|-----------------------|------|---------|-------------|
| `RATE_LIMIT_DEFAULT`  | `int` | 100    | Requests per window per IP |
| `RATE_LIMIT_WINDOW`   | `int` | 60     | Window length, seconds |

## Sentry

| Variable                       | Type   | Default | Description |
|--------------------------------|--------|---------|-------------|
| `SENTRY_DSN`                   | `str?` | None    | Sentry DSN; empty = Sentry disabled |
| `SENTRY_TRACES_SAMPLE_RATE`    | `float`| 0.1     | Fraction of transactions to trace |
| `SENTRY_PROFILES_SAMPLE_RATE`  | `float`| 0.1     | Fraction of transactions to profile |

## Celery (optional worker)

| Variable                | Type   | Default                       | Description |
|-------------------------|--------|-------------------------------|-------------|
| `CELERY_BROKER_URL`     | `str`  | `redis://redis:6379/1`        | Celery broker |
| `CELERY_RESULT_BACKEND` | `str`  | `redis://redis:6379/2`        | Celery result backend |

## Where to go from here

- [Configuration (Getting started)](../getting-started/configuration.md) — quick recipes
- [Configuration reference](configuration.md) — the `Settings` class
