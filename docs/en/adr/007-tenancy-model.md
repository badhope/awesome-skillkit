# ADR 007 — Single-tenant v1, multi-tenant v1.2

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

Many "AI skill" platforms pitch multi-tenant orgs from day one. We
are deliberately not.

## Decision

**v1** is single-tenant: one deployment = one organization. **v1.2**
will add an `organizations` table and a `memberships` join table for
multi-tenant deployments.

## Rationale

- Multi-tenant adds row-level security, an org switcher UI,
  per-org billing, and per-org rate limits. Each is a meaningful
  surface area to test.
- Most self-hosters deploy one instance for one team. Forcing
  multi-tenant data modeling on day one would slow that path.
- v1.2 can introduce the `organization_id` foreign key on every
  existing table without rewriting the public REST surface.

## Consequences

- The data model is **not** tenant-aware in v1. Adding
  `organization_id` in v1.2 is a forward-compatible migration.
- The auth model in v1.2 will gain an org claim in the JWT.
- Pricing, if/when added, will be per-deployment in v1 and per-org
  in v1.2.
