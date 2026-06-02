# Installation

AI-SKILL is a self-hostable monorepo. Pick the path that matches your
context.

## Prerequisites

| Tool         | Version    | Why                                      |
|--------------|------------|------------------------------------------|
| Python       | 3.12+      | Backend runtime                          |
| Poetry       | 1.8+       | Backend dependency manager               |
| Node.js      | 20+        | Frontend + TypeScript SDK build          |
| npm          | 10+        | Frontend + TypeScript SDK install         |
| Docker       | 24+        | Container runtime                        |
| Docker Compose | 2.x      | Multi-container orchestration            |
| Git          | 2.40+      | Source control                           |
| OpenSSL      | 1.1+       | Secret generation                        |

The backend also uses these system services (provided by Docker Compose
in the default setup):

| Service    | Version |
|------------|---------|
| PostgreSQL | 16      |
| Redis      | 7       |
| Qdrant     | 1.9+    |

## Install via Docker (recommended)

This is the fastest path. It boots the whole stack in a single
command and is suitable for both development and single-VPS
production.

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

cp .env.example .env
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env

docker compose up -d --build

# Watch the logs
docker compose logs -f
```

Open <http://localhost:3000> in a browser.

## Install without Docker

Use this when you cannot run Docker (e.g. locked-down corporate
environments).

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env — set real DATABASE_URL, JWT_SECRET_KEY, ADMIN_PASSWORD
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
# Env vars exposed to the browser MUST be prefixed with NEXT_PUBLIC_.
# The value is the backend root (no /api/v1 suffix) because the
# Next.js rewrite in next.config.ts appends /api/* for you.
cp .env.example .env.local
echo 'NEXT_PUBLIC_API_URL="http://localhost:8000"' >> .env.local
echo 'NEXT_PUBLIC_APP_NAME="AI-SKILL"'                >> .env.local
npm install
npm run build
npm start
```

### State services

You will need to provide your own PostgreSQL, Redis, and Qdrant.
The simplest free options:

- **PostgreSQL** — `brew install postgresql@16` (macOS) /
  `apt install postgresql-16` (Ubuntu)
- **Redis** — `brew install redis` / `apt install redis`
- **Qdrant** — `docker run -p 6333:6333 qdrant/qdrant:v1.9.0`

## Verify the install

```bash
# Backend health
curl -sf http://localhost:8000/health

# Frontend renders
curl -sfI http://localhost:3000

# API docs (only when DEBUG=true on the backend)
open http://localhost:8000/docs
```

## Create the first admin

```bash
docker compose exec backend python -m app.scripts.create_admin
```

Follow the prompts. After the script exits, log in to the frontend
with the credentials you provided.

## Next steps

- [Quick start](quickstart.md) — your first skill in 5 minutes
- [Configuration](configuration.md) — every env var documented
- [Deployment](../deployment.md) — production topologies
