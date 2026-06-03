# Configuration

AI-SKILL is configured entirely through environment variables. There
is **no** `config.yaml` and **no** admin UI for global settings.

## Where settings come from

Settings are loaded by Pydantic v2 in this order of precedence:

1. Real environment variables (highest)
2. A `.env` file in the working directory
3. Sensible defaults baked into the code (lowest — and *not used* for
   security-sensitive values)

## How the file is loaded

```bash
# 1. Copy the example
cp .env.example .env

# 2. Generate the three secrets the app refuses to ship defaults for
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

## Fail-fast secret validation

In production (`DEBUG=false`), the backend **refuses to start** if:

- `JWT_SECRET_KEY` is missing, shorter than 32 characters, or
  matches a known-weak default
- `ADMIN_PASSWORD` is missing (the seed module skips admin creation
  in that case)
- `POSTGRES_PASSWORD` is missing (the docker-compose service uses
  `${VAR:?...}` so the container fails to start)

In debug mode (`DEBUG=true`), the backend generates an **ephemeral
random** `JWT_SECRET_KEY` per process and logs a warning. This keeps
local development frictionless without weakening production.

## Environment reference

The full reference is in [Environment variables](../reference/environment.md).
A quick overview:

| Variable          | Purpose                                | Required in prod? |
|-------------------|----------------------------------------|-------------------|
| `JWT_SECRET_KEY`  | HS256 signing key                      | Yes               |
| `ADMIN_PASSWORD`  | First superuser password               | Yes (for seed)    |
| `POSTGRES_PASSWORD` | Postgres superuser password           | Yes               |
| `DATABASE_URL`    | asyncpg DSN                            | Yes               |
| `REDIS_URL`       | redis-py connection string             | Yes               |
| `QDRANT_URL`      | Qdrant HTTP endpoint                   | Yes               |
| `BACKEND_CORS_ORIGINS` | Comma-separated allow-list         | Yes               |
| `DEBUG`           | true = permissive / false = strict     | No (default false)|
| `SENTRY_DSN`      | Sentry error monitoring                | No                |
| `STORAGE_TYPE`    | `local` or `s3`                        | No (default local)|
| `EMBEDDING_MODEL` | HuggingFace model id                   | No (default `sentence-transformers/all-mpnet-base-v2`) |
| `EMBEDDING_DIMENSION` | Vector dimension                  | No (default 768)  |
| `LOG_LEVEL`       | `DEBUG` / `INFO` / `WARNING` / …       | No (default INFO) |
| `LOG_FORMAT`      | `json` / `console`                     | No (default json) |
| `RATE_LIMIT_DEFAULT` | Requests per window per IP          | No (default 100)  |
| `RATE_LIMIT_WINDOW`  | Window length, seconds              | No (default 60)   |

## Multi-environment workflow

The recommended pattern is one `.env` per environment, kept out of
source control:

```bash
# Local development
.env

# Staging
.env.staging

# Production
.env.production
```

Copy the right one into place before starting the stack:

```bash
cp .env.production .env
docker compose up -d
```

For production, prefer your secret manager (HashiCorp Vault, AWS
Secrets Manager, Doppler, Infisical) and inject values at
container-start time.

## Per-secret quick recipes

```bash
# JWT secret (256 bits)
openssl rand -hex 32

# Long random password
openssl rand -base64 18

# UUID (for category_id, etc.)
python3 -c "import uuid; print(uuid.uuid4())"
```

## Where to go from here

- [Environment reference](../reference/environment.md) — every
  variable, every default, every constraint
- [Configuration reference](../reference/configuration.md) — the
  underlying `Settings` class
