# ADR 005 — Poetry for backend, npm for frontend

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

We need a package manager and dependency-locking strategy. The
backend is Python, the frontend and TypeScript SDK are JavaScript.

## Decision

- **Python (backend + Python SDK)** → Poetry 1.8+
- **JavaScript / TypeScript (frontend + TypeScript SDK)** → npm 10+
  with `package-lock.json` committed

## Rationale

- Poetry: deterministic lockfile (`poetry.lock`), clear
  `pyproject.toml`, single command to install and run.
- npm: ships with Node 20+, ubiquitous in CI, lockfile is widely
  understood, no extra tool to install.

## Alternatives considered

| Option            | Why not                                     |
|-------------------|---------------------------------------------|
| pip + requirements.txt | Lacks deterministic transitive resolution |
| uv                | Excellent but still maturing in 2026; we may revisit |
| pnpm / yarn       | Both work fine; we picked npm for least friction |

## Consequences

- CI uses `poetry install --no-interaction` and `npm ci`.
- Contributors need Poetry and npm installed; both are documented in
  [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
- `pyproject.toml` includes `[tool.ruff]` and `[tool.mypy]` config
  so a single file is enough for linting, type-checking, and
  packaging.
