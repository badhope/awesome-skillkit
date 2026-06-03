# ADR 008 — Failure-fast secret validation

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

In the past we shipped `.env.example` with placeholder values like
`JWT_SECRET_KEY=change-this-in-production`. Operators frequently
copy-pasted the file and ran the stack with the placeholder — the
system booted, but the entire auth layer was trivially forgeable.

## Decision

The application **refuses to start** in production mode if any of
the following is missing, too short, or on a known-weak denylist:

- `JWT_SECRET_KEY` (must be ≥ 32 chars)
- `ADMIN_PASSWORD` (used by the seed module; must be ≥ 12 chars)
- `POSTGRES_PASSWORD` (used by docker-compose; no default fallback)

Validation is implemented in a `@model_validator` on the `Settings`
class. The compose file uses `${VAR:?...}` so a missing variable
fails the container at startup.

## Consequences

- New operators hit a clear error message and a `openssl rand` hint
  on first boot. This is the desired friction.
- Tests use `DEBUG=true` to opt into a permissive mode (random
  ephemeral JWT key) so the test suite is hermetic.
- A small `secrets-scan` Make target guards against accidentally
  reintroducing a hardcoded credential.
