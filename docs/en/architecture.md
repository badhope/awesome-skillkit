# AI-SKILL — Architecture

This document describes the runtime architecture, data flow, and
deployment topology of AI-SKILL. It is intended for operators and
contributors who need to understand the system before extending it.

For a high-level overview, see [the diagram in the home page](index.md#architecture).
For deployment specifics, see [docs/deployment.md](deployment.md).

---

## 1. Layered View

AI-SKILL is organized into five well-defined layers. Each layer has a
single, narrow responsibility and communicates with the next layer
through a typed contract.

```
┌──────────────────────────────────────────────────────────────────┐
│  L1  Client                                                      │
│      Browser (PWA) · Mobile Browser · Python SDK · TS SDK         │
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTPS · JSON / form-data
┌──────────────────────────────▼───────────────────────────────────┐
│  L2  Edge                                                        │
│      Nginx / Caddy / Traefik  (TLS termination, rate-limit, gzip)│
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTP
┌──────────────────────────────▼───────────────────────────────────┐
│  L3  Application                                                 │
│      Frontend  ── Next.js 15 (App Router, SSR + RSC)             │
│      Backend   ── FastAPI 0.115  (async, OpenAPI-generated)      │
└──────────────────────────────┬───────────────────────────────────┘
                               │  asyncpg / qdrant-client / redis-py
┌──────────────────────────────▼───────────────────────────────────┐
│  L4  Stateful services                                           │
│      PostgreSQL 16  · Redis 7  · Qdrant 1.9+  · Object storage   │
└──────────────────────────────┬───────────────────────────────────┘
                               │  Alembic migrations
┌──────────────────────────────▼───────────────────────────────────┐
│  L5  Operations                                                  │
│      Docker Compose  · GitHub Actions  · Sentry  · OTel          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Module Map

```
backend/app/
├── main.py                  # FastAPI app factory, middleware wiring, lifespan
├── api/v1/                  # HTTP routers, one per resource
│   ├── auth.py              # /register · /login · /refresh · /logout · /me · /me/password
│   ├── users.py             # /users · /users/{username} · /users/{username}/skills
│   ├── skills.py            # CRUD + /search (vector) + /featured + /popular + /trending
│   │                        # + /{slug}/versions · /dependencies · /similar · /rate · /use
│   ├── categories.py        # Flat list + /tree (nested) + CRUD
│   ├── tags.py              # Tag CRUD + /popular
│   ├── compositions.py      # Composition CRUD + /{slug}/items
│   └── analytics.py         # /dashboard · /skills/usage · /skills/popular
│                            # · /categories/distribution · /tags/trending
│
├── core/                    # Cross-cutting concerns
│   ├── config.py            # pydantic-settings, secret validation
│   ├── security.py          # bcrypt · JWT encode/decode · password policy
│   ├── deps.py              # FastAPI dependencies (auth, db, redis)
│   ├── logging.py           # structlog configuration
│   ├── pagination.py        # Generic Page[T] + PaginationParams
│   ├── audit.py             # Append-only audit log
│   └── seed.py              # Idempotent categories + admin bootstrap
│
├── models/                  # SQLAlchemy 2.0 ORM models
│   └── skill.py             # User · Skill · Category · Tag · SkillVersion
│                            # SkillDependency · SkillRating · SkillUsageLog
│                            # SkillComposition · SkillCompositionItem
│
├── schemas/                 # Pydantic v2 request / response models
├── services/                # Domain logic (no HTTP coupling)
│   ├── vector_search.py     # Qdrant wrapper, hybrid BM25 + dense scoring
│   ├── skill_composer.py    # Build a composition DAG
│   ├── skill_validator.py   # Static checks (cycles, missing deps)
│   ├── cache.py             # Redis helpers
│   ├── analytics.py         # Event collection + aggregation
│   ├── notification.py      # Webhook fan-out
│   └── import_export.py     # Skill pack (.zip) round-trip
│
├── middleware/              # Starlette middleware
│   ├── security_headers.py  # OWASP-recommended headers
│   ├── rate_limit.py        # Per-IP token bucket
│   └── error_handler.py     # Maps exceptions to JSON responses
│
├── scripts/                 # One-off CLI tools
│   └── create_admin.py      # Bootstrap a superuser
│
├── cli/                     # In-process Typer app
└──db/session.py            # async engine, session factory
```

### 2.1 Request Lifecycle

A typical authenticated request follows this path:

```
client
  └─► Nginx   (TLS, gzip, X-Forwarded-For)
       └─► FastAPI
            ├─► ErrorHandlerMiddleware       (uncaught exceptions → JSON)
            ├─► SecurityHeadersMiddleware   (adds HSTS, CSP, X-Frame-…)
            ├─► RateLimitMiddleware          (per-IP token bucket)
            ├─► CORSMiddleware               (preflight handling)
            └─► Router
                 ├─► Depends(get_db)          (async session)
                 ├─► Depends(get_current_user) (JWT decode → User)
                 ├─► Depends(pagination)      (Page[T] construction)
                 └─► Service layer
                      └─► Postgres / Redis / Qdrant
```

### 2.2 Authentication Flow

```
register     POST /auth/register
             validate password strength, bcrypt-hash, persist User,
             return UserResponse (no tokens — clients call /login
             immediately after)

login        POST /auth/login        (form: username + password)
             verify bcrypt, issue access (30 min) + refresh (7 d)

refresh      POST /auth/refresh      (form: refresh_token)
             verify refresh, rotate, return new pair

logout       POST /auth/logout       (requires valid access token)
             record a logout audit event via the audit log
```

---

## 3. Data Model

| Table                       | Key columns                                                                | Indexes                          |
|-----------------------------|----------------------------------------------------------------------------|----------------------------------|
| `users`                     | `id` · `email` (UQ) · `username` (UQ) · `hashed_password` · `is_active`    | `email` · `username` · `created_at` |
| `skills`                    | `id` · `slug` (UQ) · `name` · `content` (JSONB) · `category_id` · `is_public` | `slug` · `category_id` · `author_id` · `is_featured` · `status` · `complexity` |
| `skill_versions`            | `id` · `skill_id` · `version` · `content` (JSONB) · `changelog`           | `(skill_id, version)` (UQ)       |
| `categories`                | `id` · `slug` (UQ) · `name` · `parent_id` · `sort_order`                  | `slug` · `parent_id`             |
| `tags`                      | `id` · `name` (UQ) · `color` · `description` · `usage_count`             | `name`                           |
| `skill_tag_association`     | `skill_id` · `tag_id`                                                      | `skill_id` · `tag_id`            |
| `skill_dependencies`        | `skill_id` · `depends_on_skill_id` · `version_constraint`                 | `(skill_id, depends_on_skill_id)` (UQ) |
| `skill_ratings`             | `skill_id` · `user_id` · `rating` (1-5) · `comment`                        | `(skill_id, user_id)` (UQ)       |
| `skill_usage_logs`          | `skill_id` · `user_id` · `action` · `ip_address`                          | `skill_id` · `user_id` · `created_at` |
| `skill_compositions`        | `id` · `slug` (UQ) · `name` · `owner_id` · `is_public`                    | `slug` · `owner_id`              |
| `skill_composition_items`   | `composition_id` · `skill_id` · `sort_order` · `notes`                    | `(composition_id, skill_id)` (UQ) |

### 3.1 JSONB columns

- `skills.content` — the skill body (markdown, code, references)
- `skill_compositions` is composed of `skill_composition_items` rows
  (no separate JSONB `items` column on the composition itself)
- Audit events flow through the `app.core.audit.log_event` helper,
  which currently ships them to the structured log (no separate
  `analytics_events` table is persisted at the moment — see
  [ADR 004](adr/004-jsonb-flexible-content.md) for the
  reasoning).

---

## 4. Search Architecture

AI-SKILL uses a **hybrid retriever** for skill search:

1. **BM25 (lexical)** — full-text index on `name`, `description`, `content`
2. **Dense (semantic)** — `sentence-transformers/all-mpnet-base-v2` (768d)
   vectors stored in Qdrant
3. **Re-ranking** — results from both are merged and re-scored by
   weighted RRF (Reciprocal Rank Fusion), with adjustments for
   `is_featured`, `rating_avg`, and freshness.

```
search request
   │
   ├─► BM25 top-k           ┐
   │                        ├─► RRF fusion ─► re-rank ─► final top-N
   └─► Qdrant top-k         ┘
```

The model can be swapped at deploy time by changing the
`EMBEDDING_MODEL` env var. The Qdrant collection is auto-created on
backend startup if it does not exist.

---

## 5. Frontend Architecture

```
frontend/src/
├── app/                    # Next.js 15 App Router
│   ├── layout.tsx          # Root layout: providers, fonts, i18n, theme
│   ├── page.tsx            # Landing
│   ├── skills/             # /skills, /skills/[slug]
│   ├── categories/         # /categories, /categories/[slug]
│   ├── compositions/       # /compositions, /compositions/[slug]
│   ├── search/             # /search (debounced query)
│   ├── dashboard/          # /dashboard (authed analytics)
│   ├── auth/               # /auth/login, /auth/register
│   ├── error.tsx           # 5xx boundary
│   ├── not-found.tsx       # 404 page
│   └── loading.tsx         # Suspense skeleton
│
├── components/             # Domain + UI primitives
│   ├── ui/                 # shadcn/ui style primitives (Button, Card, …)
│   ├── Navbar.tsx          # Top bar
│   ├── Footer.tsx
│   ├── SearchBar.tsx
│   ├── SkillCard.tsx
│   ├── OfflineBanner.tsx
│   └── …
│
├── hooks/                  # Encapsulated state
│   ├── useAuth.ts
│   ├── useSkills.ts        # TanStack Query
│   ├── useSearch.ts
│   ├── useOnlineStatus.ts
│   └── …
│
└── lib/
    ├── api.ts              # Axios instance + interceptors
    ├── auth.ts             # Token storage
    ├── i18n/               # English / Chinese
    └── fonts.ts            # Self-hosted Inter + Noto Sans SC
```

State is split into three buckets:

| Bucket         | Tool                              | Example                     |
|----------------|-----------------------------------|-----------------------------|
| Server state   | TanStack Query                    | `useSkills()` (skills list) |
| Local state    | React hooks                       | `useLocalStorage('theme')`  |
| Global UI      | React Context                     | `useI18n()`                 |

---

## 6. SDK Architecture

Both SDKs are thin, fully-typed clients over the same REST surface.

### 6.1 Python SDK

```
sdk/python/skill_sdk/
├── client.py        # SkillClient (httpx.AsyncClient under the hood)
├── types.py         # Skill, Category, Tag, …  (pydantic models)
└── exceptions.py    # SkillError hierarchy
```

### 6.2 TypeScript SDK

```
sdk/typescript/src/
├── client.ts        # SkillClient (fetch under the hood)
├── types.ts         # Generated-style hand-written types
├── errors.ts        # SkillError hierarchy
└── index.ts
```

Both clients expose **the same method names** so consumers can swap
languages without code changes.

---

## 7. Deployment Topology

### 7.1 Single host (Docker Compose)

A single `docker compose up -d` brings up: postgres, redis, qdrant,
backend, frontend, and (optional) celery worker + beat.

### 7.2 Production (managed)

A typical production deployment:

- **Frontend** → Vercel / Cloudflare Pages / Nginx static export
- **Backend** → Fly.io / Render / ECS / GKE
- **Postgres** → RDS / Supabase / Neon
- **Redis** → Upstash / ElastiCache
- **Qdrant** → Qdrant Cloud (managed) or self-hosted
- **Object storage** → S3 / R2 / GCS
- **Observability** → Sentry + OpenTelemetry collector

See [docs/deployment.md](deployment.md) for step-by-step recipes.

---

## 8. Security Model

- **Authentication**: JWT (HS256), 30-min access + 7-day refresh.
  (Driven by `ACCESS_TOKEN_EXPIRE_MINUTES` and
  `REFRESH_TOKEN_EXPIRE_DAYS` in `Settings` — change there to
  override.)
- **Authorization**: RBAC — `is_superuser` for now; role table planned for v1.1.
- **Transport**: TLS at the edge; HSTS enforced in production.
- **Input**: Pydantic v2 strict mode on all endpoints.
- **Output**: OWASP security headers via `SecurityHeadersMiddleware`.
- **Secrets**: 12-factor; secrets MUST be supplied via env; the app
  refuses to start in production with a missing or weak `JWT_SECRET_KEY`.
- **Rate limiting**: per-IP token bucket (Redis-backed).
- **Audit**: every authentication and modification event lands in
  `analytics_events` with an event_type prefix of `audit.`.
- **CORS**: explicit allow-list (no wildcards when credentials are sent).

---

## 9. Observability

- **Logs**: structured JSON via `structlog` to stdout, scraped by
  Fluent Bit / Vector.
- **Metrics**: OpenTelemetry `OTLP` exporter to your collector.
- **Traces**: OTel auto-instrumentation for FastAPI and SQLAlchemy.
- **Errors**: Sentry SDK (DSN via `SENTRY_DSN`).
- **Health check**: `GET /health` returns 200 with `{status,
  app_name, version}` as long as the process is up. The Alembic
  migration version and Qdrant collection existence are NOT
  checked by `/health`; they are checked by
  `scripts/health_check.py` and by the backend's `lifespan`
  startup probe (which fails-fast if Postgres is unreachable).

---

## 10. Versioning

This project follows [Semantic Versioning 2.0](https://semver.org/).

- **Major** — breaking schema or auth change
- **Minor** — new feature, new endpoint
- **Patch** — bugfix, dependency upgrade, doc fix

Tags follow `vMAJOR.MINOR.PATCH`. Docker images are tagged with the
git ref, the version, and `latest` for the default branch.
