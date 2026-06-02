# AI-SKILL — Roadmap

This document tracks the project direction. It is a living list —
items move between sections as the project evolves.

Last updated: 2026-06-02

---

## Released

- [x] Self-hostable FastAPI backend with OpenAPI-generated docs
- [x] Next.js 15 mobile-first frontend with English / Chinese i18n
- [x] JWT auth, RBAC, rate-limit, audit log, security headers
- [x] Qdrant hybrid vector search (BM25 + dense + re-rank)
- [x] Alembic migrations, idempotent seed for categories and tags
- [x] Python and TypeScript SDKs
- [x] Docker Compose single-command deployment
- [x] CI/CD: lint, test, build, publish Docker images
- [x] Full OSS documentation set: LICENSE, CONTRIBUTING, SECURITY,
      CODE_OF_CONDUCT, CHANGELOG, architecture, deployment,
      troubleshooting, development

---

## In progress — 1.1 (target Q3 2026)

- [ ] **Public skill registry** — a community-curated catalog of skills
      that anyone can pull from. Decoupled from the platform itself.
- [ ] **GraphQL endpoint** alongside REST
- [ ] **Per-tenant API keys** in addition to user JWTs
- [ ] **WebSocket** push for live analytics
- [ ] **Composition visual editor** in the frontend
- [ ] **Skill rating breakdown** (clarity, performance, portability)
- [ ] **CLI tool for skill authors** — `ai-skill init` / `validate` /
      `publish`

---

## Planned — 1.2 (target Q4 2026)

- [ ] Multi-language i18n (Spanish, French, Japanese, Korean)
- [ ] Skill packs (download/upload `.zip` of skills + metadata)
- [ ] Version diffing UI
- [ ] OAuth providers (Google, GitHub) in addition to email/password
- [ ] Pluggable storage backends (S3, R2, GCS, MinIO)
- [ ] Pluggable vector backends (pgvector, Milvus, Weaviate)
- [ ] Per-organization billing (Stripe)
- [ ] Audit log retention + GDPR erasure tooling

---

## Under consideration — 2.0+

- [ ] Skill execution sandbox (run untrusted skills in WASM)
- [ ] Marketplace / paid skills
- [ ] Skill recommendation engine (collaborative filtering)
- [ ] Native mobile apps (iOS, Android)
- [ ] Slack / Discord / Teams bots
- [ ] VSCode extension

---

## Non-goals

These are things we are **explicitly not** building:

- **A generic CMS** — there are better tools (Strapi, Directus, Sanity).
- **A general LLM chat product** — AI-SKILL is a skill catalog, not a chat UI.
- **A workflow engine** — compositions describe dependencies, not execution
  semantics. We point at the existing ecosystem (Temporal, Prefect, Airflow).
- **A web scraper** — skills are authored, not scraped.

---

## How to influence the roadmap

1. Open a [Feature Request](../../issues/new?template=feature_request.md).
2. Or start a thread in [Discussions / Ideas](../../discussions/categories/ideas).
3. Or send a PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).
