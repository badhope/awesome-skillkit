All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-01

### Added

- Initial release of AI-SKILL — a self-hostable universal agent skill library platform
- Full-stack monorepo: FastAPI backend, Next.js 15 frontend, Python and TypeScript SDKs
- Mobile-first responsive design with Progressive Web App support
- English/Chinese internationalization (i18n) with runtime locale switching
- Qdrant vector search powered by Sentence-BERT embeddings
- Hybrid BM25 + dense vector search for maximum relevance
- Semantic versioning with complete skill change history
- Skill dependency management with version constraints and cycle detection
- User rating and review system (1-5 stars)
- Analytics dashboard with real-time usage statistics and trends
- REST API with auto-generated OpenAPI documentation (Swagger/ReDoc)
- JWT-based authentication with access and refresh token rotation
- Role-Based Access Control (RBAC) authorization
- Rate limiting and API abuse prevention
- OWASP security headers (HSTS, CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy)
- Structured JSON logging with log level configuration
- OpenTelemetry integration for distributed tracing
- Sentry error tracking and performance monitoring
- Python SDK with async support and type hints
- TypeScript SDK with full TypeScript definitions
- Docker Compose one-command deployment
- GitHub Actions CI/CD pipeline (lint, test, build, publish)
- Database migrations with Alembic
- Redis caching layer with LRU eviction
- PostgreSQL 16 with asyncpg driver for high-performance queries
- Celery task queue for background job processing
- S3-compatible storage backend support
- CLI management tool with Rich-based terminal UI
- Comprehensive unit and integration test suite
- Code quality tooling: ruff, mypy, ESLint, Prettier, pre-commit hooks
- Issue templates, PR template, CODEOWNERS, and Dependabot configuration
- Full open-source documentation set: LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG

### Notes

This release ships a fully working **empty library**. It is up to each operator to
seed their own skills or import from an external registry. The platform is
production-ready; the dataset is intentionally not bundled.

---

[1.0.0]: https://github.com/badhope/AI-SKILL/releases/tag/v1.0.0