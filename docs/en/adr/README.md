# AI-SKILL — Architecture Decision Records

This folder contains Architecture Decision Records (ADRs).

Each ADR is a short, immutable document that captures **one**
significant technical decision: the context, the considered options,
the decision, and the consequences.

## Index

| #   | Title                                | Status     |
|-----|--------------------------------------|------------|
| 001 | [Pydantic v2 + ClassVar Depends](001-pydantic-v2-and-classvar-depends.md) | Accepted |
| 002 | [Qdrant for vector search](002-qdrant-vector-search.md)                 | Accepted |
| 003 | [JWT (HS256) over RS256](003-jwt-hs256.md)                              | Accepted |
| 004 | [JSONB for skills.content and compositions.items](004-jsonb-flexible-content.md) | Accepted |
| 005 | [Poetry for backend, npm for frontend](005-polyglob-packaging.md)      | Accepted |
| 006 | [Next.js 15 App Router](006-nextjs-app-router.md)                      | Accepted |
| 007 | [Single-tenant v1, multi-tenant v1.2](007-tenancy-model.md)            | Accepted |
| 008 | [Failure-fast secret validation](008-fail-fast-secrets.md)            | Accepted |
| 009 | [OWASP security headers middleware](009-owasp-headers.md)              | Accepted |
| 010 | [Pre-commit hooks + conventional commits](010-pre-commit-and-commits.md) | Accepted |

## Format

We use the [MADR](https://adr.github.io/madr/) template, lightly
adapted. Each ADR is a single Markdown file in this directory with a
sequential number prefix. **ADRs are append-only** — once accepted,
the file is never edited. If a decision is later reversed, write a
new ADR that supersedes it.

## Why

ADRs help us:

- Onboard new contributors faster
- Remember why we picked something two years later
- Avoid re-litigating settled decisions in PRs
