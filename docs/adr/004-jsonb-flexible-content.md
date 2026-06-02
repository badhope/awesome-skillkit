# ADR 004 — JSONB for skills.content and compositions.items

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

Skills have a free-form `content` field (markdown, code, references,
parameters). Compositions describe an ordered list of skills with
parameters. Both are user-authored and have an evolving shape.

## Decision

Store both as **Postgres JSONB** and validate the shape with
Pydantic v2 on read and write.

## Alternatives considered

| Option          | Why not                                          |
|-----------------|--------------------------------------------------|
| Fully relational | Too rigid; needs a migration for every field    |
| MongoDB         | Adds a second database; loses ACID with Postgres |
| Text blob       | Cannot index; cannot query                       |

## Consequences

- New skill fields are added in Pydantic without a database
  migration.
- We get GIN indexing on JSONB for cheap "where the JSON contains X"
  queries.
- Pydantic v2 stays the single source of truth for the schema.
- Trade-off: any code that bypasses Pydantic (raw SQL, ad-hoc
  reports) needs to re-implement validation.
