---
name: seed-test-data
name_zh: 种子测试数据
description: 'Seed local Langfuse test data with one command: large/branching observation'
description_zh: 生成和管理测试数据，用于开发和测试环境。
category: dev-tools
tags:
  - ai
  - backend
  - cli
  - database
  - docker
source: null
license: UNKNOWN
author: unknown
version: '0.1.0'
needs_review: false
slug: seed-test-data
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
---
# When to use

Use this skill when you need guidance on seed test data.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Seed Test Data

One-shot deterministic test data for local Langfuse. The CLI handles env
loading, preflight checks, ClickHouse/Postgres writes, readback verification,
and prints UI deep links plus a machine-readable JSON summary (last stdout
line).

## If anything fails, run doctor first

```bash
pnpm run seed -- doctor
```

Prints PASS/WARN/FAIL per dependency (Postgres, migrations, project,
ClickHouse, v4 dev tables, Redis, MinIO, web app) with the exact fix command
for every failure. Do not debug Docker/ClickHouse manually before running
this.

## Need → command

| I need... | Command |
| --- | --- |
| A very complex observation tree (v3) | `pnpm run seed -- trace-tree --observations 5000 --depth 12 --breadth 500` |
| The same tree readable in the v4 events UI | add `--v4` (writes `events_full`; `events_core` fills via MV) |
| A super tough session (v3 legacy session view) | `pnpm run seed -- long-session --traces 300 --observations-per-trace 8` |
| Many traces for list/filter performance | `pnpm run seed -- many-traces --count 100000 --days 14` |
| Huge/malformed/unicode payloads | `pnpm run seed -- trace-tree --payload-bytes 1000000 --payload-style malformed` (styles: json, text, malformed, unicode) |
| See all scenarios and flags | `pnpm run seed -- list --json` |
| Predict without writing | add `--dry-run` |

## Contract

- Last stdout line is a JSON summary: `traceIds`, `sessionIds`, `counts`,
  `verified` (ClickHouse readback), `links` (UI deep links). Use `--json` to
  suppress progress logs. Non-zero exit = data did not land; the error
  includes a `fix:` line.
- Deterministic: same `--seed` (default 42) and flags → same ids (ids never
  contain dates), with timestamps anchored to the current UTC day. Re-running
  within the same day overwrites in place; a later-day re-run updates the
  same ids with re-anchored timestamps (the previous day's rows persist
  under their old dates until then). Independent copies come only from
  `--id-prefix`.
- Default project is the seeded `7a88fb47-b4e2-43b8-a06c-a5ce950dc53a`
  (login `demo@langfuse.com` / `password`); override with `--project`.
- Open the printed `links` in the browser to verify visually. The v4
  events-backed UI is the per-user "Fast (Preview)" sidebar toggle, or
  `LANGFUSE_MIGRATION_V4_WRITE_MODE=events_only` server-side.

## Extending

Add a scenario in `packages/shared/scripts/seeder/scenarios/`: a plain
function using the deterministic `Rng` (never `Math.random`), register it in
`scenarios/index.ts`, and update the table in
`packages/shared/scripts/seeder/AGENTS.md` and this skill. Scenario names,
flags, and JSON keys are additive-only contracts. Design rationale:
`packages/shared/scripts/seeder/README.md`.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.

