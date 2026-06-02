# ADR 010 — Pre-commit hooks + conventional commits

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

We want a consistent code style and a parseable commit history
without making every contributor install five tools by hand.

## Decision

- **Pre-commit** runs the linters and formatters on every commit.
- **Conventional Commits** are enforced in the `commit-msg` hook
  so the changelog can be generated automatically in a later
  release.
- A `Makefile` exposes the same commands (`make lint`, `make
  typecheck`, `make test`, `make secrets-scan`) for use outside
  the pre-commit context.

## Consequences

- A `make first-run` target installs everything in one shot.
- The CI workflow still re-runs the linters as a safety net.
- A bot (or a contributor with `release-please` in the future) can
  produce a CHANGELOG diff purely from the commit log.
