# AI-SKILL — Deployment Guide

This guide walks you from `git clone` to a production URL. Pick the
path that matches your context:

1. [Local development](#1-local-development-with-docker-compose)
2. [Manual / bare-metal](#2-manual-installation-bare-metal)
3. [Single-VPS production](#3-single-vps-production-with-nginx)
4. [Managed / cloud](#4-managed-cloud-deployment)
5. [Upgrades and rollbacks](#5-upgrades-and-rollbacks)
6. [Backups](#6-backups)
7. [Hardening checklist](#7-production-hardening-checklist)

---

## 1. Local development (with Docker Compose)

This is the fastest way to run the full stack. Assumes Docker Engine
24+ and Compose v2.

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

# 1. Copy and edit the env file
cp .env.example .env
# Generate the three required secrets
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env

# 2. Build and start
docker compose up -d --build

# 3. Watch the logs
docker compose logs -f

# 4. Open the app
open http://localhost:3000
```

Default ports:

| Service    | Port  | URL                         |
|------------|-------|-----------------------------|
| Frontend   | 3000  | <http://localhost:3000>     |
| Backend    | 8000  | <http://localhost:8000>     |
| Swagger UI | 8000  | <http://localhost:8000/docs>|
| ReDoc      | 8000  | <http://localhost:8000/redoc> |
| Postgres   | 5432  | `localhost:5432`            |
| Redis      | 6379  | `localhost:6379`            |
| Qdrant     | 6333  | <http://localhost:6333/dashboard> |

When the backend first starts, it runs the Alembic migrations and
seeds the initial categories. Create your first superuser with:

```bash
docker compose exec backend python -m app.scripts.create_admin
```

Then restart the backend so the new admin can log in:

```bash
docker compose restart backend
```

---

## 2. Manual installation (bare metal)

Use this when you cannot run Docker (e.g. restricted environments).

### 2.1 Prerequisites

| Tool         | Version    |
|--------------|------------|
| Python       | 3.12+      |
| Poetry       | 1.8+       |
| Node.js      | 20+        |
| PostgreSQL   | 16+        |
| Redis        | 7+         |
| Qdrant       | 1.9+       |
| Caddy / Nginx| latest     |

### 2.2 Backend

```bash
cd backend
cp .env.example .env
# Edit .env with real values
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2.3 Frontend

```bash
cd frontend
cp .env.example .env.local
# Set VITE_API_BASE_URL=https://api.your-domain.com/api/v1
npm install
npm run build
npm start
```

---

## 3. Single-VPS production (with Nginx)

This is the smallest "real" production setup: one $5/mo VPS running
the stack behind a reverse proxy with automatic TLS.

### 3.1 Provision the host

```bash
# Ubuntu 22.04+ recommended
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin ufw
sudo usermod -aG docker $USER
# Log out and back in
```

Open the firewall:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3.2 Clone and configure

```bash
sudo mkdir -p /opt/skill-system && sudo chown $USER:$USER /opt/skill-system
cd /opt/skill-system
git clone https://github.com/badhope/AI-SKILL.git .
cp .env.example .env
$EDITOR .env   # see secrets generation below
```

### 3.3 Generate the secrets

```bash
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

### 3.4 Put Nginx in front

`/etc/nginx/sites-available/skill-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### 3.5 TLS with Caddy (alternative)

If you prefer automatic TLS, swap Nginx for Caddy:

```caddy
your-domain.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /*    frontend:3000
}
```

### 3.6 Boot the stack

```bash
docker compose up -d
docker compose exec backend python -m app.scripts.create_admin
```

### 3.7 Verify

```bash
curl -fI https://your-domain.com/health
```

---

## 4. Managed cloud deployment

### 4.1 Vercel (frontend)

```bash
cd frontend
vercel link
vercel env add VITE_API_BASE_URL production
# Paste: https://api.your-domain.com/api/v1
vercel --prod
```

### 4.2 Fly.io (backend)

```bash
cd backend
fly launch --no-deploy
fly secrets set \
  JWT_SECRET_KEY=$(openssl rand -hex 32) \
  ADMIN_PASSWORD=$(openssl rand -base64 18) \
  DATABASE_URL=postgres://... \
  REDIS_URL=redis://... \
  QDRANT_URL=https://...
fly deploy
```

### 4.3 Render

Use the `render.yaml` blueprint:

```yaml
services:
  - type: web
    name: skill-backend
    env: docker
    rootDir: backend
    envVars:
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ADMIN_PASSWORD
        generateValue: true
```

### 4.4 Reference architecture (AWS / GCP / Azure)

```
                    ┌─────────────────────┐
                    │  CloudFront / CDN   │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
   │ Frontend │         │  Backend    │        │  Workers    │
   │  (S3 /   │         │  (ECS /     │        │  (ECS /     │
   │ CloudFront)        │  Cloud Run) │        │  Cloud Run) │
   └──────────┘         └──────┬──────┘        └──────┬──────┘
                               │                      │
        ┌──────────────────────┼──────────────────────┤
        │                      │                      │
   ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
   │ Postgres │         │   Redis     │        │   Qdrant    │
   │ (RDS)    │         │ (ElastiCache)        │  (managed)  │
   └──────────┘         └─────────────┘        └─────────────┘
```

---

## 5. Upgrades and rollbacks

### 5.1 Routine upgrade

```bash
cd /opt/skill-system
git pull --ff-only
docker compose pull
docker compose up -d --remove-orphans
docker compose exec backend poetry run alembic upgrade head
docker compose exec backend python scripts/health_check.py
```

### 5.2 Roll back to the previous version

```bash
git log --oneline -n 5   # find the last good commit
git checkout <good-sha>
docker compose up -d --build
docker compose exec backend poetry run alembic downgrade -1
```

### 5.3 Database-only rollback

```bash
docker compose exec backend poetry run alembic downgrade -1
```

> ⚠️ Some migrations are destructive. Always snapshot your database
> before downgrading in production.

---

## 6. Backups

### 6.1 Postgres

```bash
# Snapshot
docker compose exec -T postgres pg_dump -U skill_user skill_db | \
    gzip > "backup-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"

# Restore
gunzip -c backup-20260601T000000Z.sql.gz | \
    docker compose exec -T postgres psql -U skill_user skill_db
```

Automate with cron:

```cron
# /etc/cron.d/skill-system-backup
0 3 * * * cd /opt/skill-system && \
  ./scripts/backup.sh >> /var/log/skill-backup.log 2>&1
```

### 6.2 Qdrant

Qdrant has a built-in snapshot API:

```bash
curl -X POST 'http://localhost:6333/collections/skills/snapshots'
# Snapshots appear in the qdrant container's /qdrant/snapshots directory
```

### 6.3 Object storage

If you use S3, enable bucket versioning and lifecycle policies. The
`scripts/backup.sh` template includes an S3 sync step.

---

## 7. Production hardening checklist

Run through this list before opening your deployment to the public.

- [ ] All env vars in `.env` set; **no defaults** in production
- [ ] `JWT_SECRET_KEY` is ≥ 32 chars and **not** on the weak denylist
- [ ] `ADMIN_PASSWORD` is ≥ 12 chars and unique
- [ ] `POSTGRES_PASSWORD` is strong and not the example value
- [ ] TLS configured; HSTS header observed (`curl -I https://…`)
- [ ] `BACKEND_CORS_ORIGINS` lists only the real frontend origin(s)
- [ ] Database is **not** exposed on the public network
- [ ] Qdrant is **not** exposed on the public network
- [ ] Redis is **not** exposed on the public network
- [ ] `DEBUG=false`
- [ ] Sentry DSN configured
- [ ] Backups running and tested (restore drill)
- [ ] `pre-commit` installed locally; CI green
- [ ] Branch protection on `main` (require PR + 1 review + CI green)
- [ ] Dependabot alerts enabled
- [ ] `git log --oneline` shows no hardcoded secrets

See [SECURITY.md](../SECURITY.md) for the full policy and
disclosure process.
