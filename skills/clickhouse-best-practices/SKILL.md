---
name: ClickHouse Best Practices
name_zh: ClickHouse 最佳实践
description: 'You''re reviewing or designing something that touches'
description_zh: '28 条 ClickHouse schema / query / insert 规则 —— 回答任何 ClickHouse 问题前都要查的清单。规则过滤、权衡判断、反模式标记。'
category: dev-tools
tags:
  - ai
  - cli
  - database
  - documentation
  - evaluation
source: null
license: Apache-2.0
author: 'ClickHouse Inc + Langfuse (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: clickhouse-best-practices
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

You're reviewing or designing something that touches
**ClickHouse** — a CREATE TABLE, an ALTER TABLE migration, a
slow SELECT, a data ingestion pipeline. The general database
intuition is misleading here: ClickHouse is columnar, has
sparse primary indexes, and the merge-tree engine does not
behave like B-tree storage. Hand-waving from Postgres or
MySQL experience is a fast way to ship a bad schema.

This skill is a **review checklist of 28 rules** organised by
priority. Before answering any ClickHouse question, load the
relevant rule files, walk the checklist, and cite the rules
in your response.

**Don't use this skill for** PostgreSQL, MySQL, SQLite, or
DuckDB tuning (the merge-tree rules do not apply). And don't
use it for OLTP workloads — ClickHouse is columnar and not
the right tool for row-level updates.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `review_type` | yes | `schema` / `query` / `insert` / `debug-slow-query`. |
| `target_action` | yes | The thing under review. |
| `rules_root` | no | Path to `rules/` dir. Override for project-specific rule overrides. |

# Output

Plain-text review report:

```
## Rules Checked
- schema-pk-plan-before-creation — Compliant
- schema-pk-cardinality-order — Violation found
- schema-types-avoid-nullable — Compliant
...

## Findings

### Violations
- **schema-pk-cardinality-order**: ORDER BY lists high-cardinality
  column `user_id` before low-cardinality `event_name`.
  - Current: `ORDER BY (user_id, event_name)`
  - Required: `ORDER BY (event_name, user_id)` — low-to-high
    cardinality, AND `event_name` is the more selective filter
  - Fix: see `rules/schema-pk-cardinality-order.md`

### Compliant
- schema-pk-plan-before-creation: ORDER BY was specified at
  table creation, no later ALTER

## Recommendations
1. Reorder ORDER BY to (event_name, user_id) — highest impact
2. ...
```

# Prompt

```prompt
You are reviewing a ClickHouse change. Walk the rule checklist
in order; cite the rule id in every finding.

1. Pick the review type.

   schema       — CREATE TABLE / ALTER TABLE / data type
                  selection
   query        — SELECT, JOIN, slow query triage
   insert       — data ingestion, batch sizing, mutation
                  patterns
   debug        — slow query log analysis

2. Load the rule files in priority order for that review
   type. Do NOT skim. Each rule is short. Read the rule's
   anti-pattern example, then check the target against it.

   Schema review order (CRITICAL first):
     1. schema-pk-plan-before-creation
     2. schema-pk-cardinality-order
     3. schema-pk-prioritize-filters
     4. schema-pk-filter-on-orderby
     5. schema-types-native-types
     6. schema-types-minimize-bitwidth
     7. schema-types-lowcardinality
     8. schema-types-avoid-nullable
     9. schema-partition-low-cardinality
    10. schema-partition-lifecycle

   Query review order (CRITICAL first):
     1. query-join-choose-algorithm
     2. query-join-filter-before
     3. query-join-use-any
     4. query-index-skipping-indices
     5. schema-pk-filter-on-orderby

   Insert review order (CRITICAL first):
     1. insert-batch-size
     2. insert-mutation-avoid-update
     3. insert-mutation-avoid-delete
     4. insert-async-small-batches
     5. insert-optimize-avoid-final

3. For each rule, mark Compliant OR Violation found.

   - Compliant: one short note on why.
   - Violation: cite rule id, give current behaviour,
     required behaviour, and a fix.

4. Order findings by severity, then by rule priority.

   CRITICAL > HIGH > MEDIUM.

5. End with a "Recommendations" block: a prioritised list of
   changes the author should make. Each line cites the rule
   id and the impact.

6. Cite your source. Every finding names a rule id. If a
   finding falls outside the 28 rules, label it "general
   ClickHouse guidance" and link the official docs.

7. Do not invent rules. If a finding is opinion, say so.
   "I would" / "you might consider" — not "rule-X says".
```

# When NOT to use

- **The target is PostgreSQL / MySQL / SQLite / DuckDB.**
  Merge-tree rules do not apply. Use the engine-specific
  skill.
- **You skip the rule files and go straight to a hunch.**
  The 28 rules encode validated ClickHouse-specific
  guidance. General database intuition is misleading
  (sparse indexes, columnar reads, merge-tree
  semantics). Cite the rules, or don't review.
- **You treat the rules as a final answer.** Rules are
  baselines, not laws. Some are explicit trade-offs
  (e.g. partition count is bounded, but not always).
  When the trade-off is in play, name it.
- **You say "rule X says" without reading rule X.**
  Read the rule file. Each rule has an anti-pattern
  example, a correct example, and a trade-off note.
  Citing the rule from memory leads to misapplication.
- **You skip the project-specific rule overrides.** Some
  projects maintain an additional `rules/` overlay
  (e.g. "never use `FINAL` on the events table"). Those
  project overrides are not optional.
- **You commit to a recommendation without knowing the
  table size, query frequency, and SLO.** A rule that
  applies to a 100M-row table may be over-engineering
  for a 1M-row table. State the assumption.
- **You review a slow query without looking at the
  actual `system.query_log`.** "Slow" needs evidence.
  Read the log, get the wall time, the read rows, the
  read bytes, then apply the rules.

# Example

**Input:**

```yaml
review_type: schema
target_action: |
  CREATE TABLE events_local (
    id UUID DEFAULT generateUUIDv4(),
    user_id String,
    event_name LowCardinality(String),
    ts DateTime64(3),
    payload String
  ) ENGINE = MergeTree()
  PARTITION BY toYYYYMM(ts)
  ORDER BY (user_id)
  TTL ts + INTERVAL 90 DAY;
```

**Output:**

```
## Rules Checked
- schema-pk-plan-before-creation — Compliant
- schema-pk-cardinality-order     — Violation found
- schema-pk-prioritize-filters    — Violation found
- schema-pk-filter-on-orderby     — Compliant (filters
  typically use event_name, see below)
- schema-types-native-types       — Compliant
- schema-types-minimize-bitwidth  — Violation found
- schema-types-lowcardinality     — Compliant
- schema-types-avoid-nullable     — Compliant
- schema-partition-low-cardinality — Compliant
- schema-partition-lifecycle      — Compliant (TTL on ts)

## Findings

### Violations
- **schema-pk-cardinality-order**: ORDER BY lists
  high-cardinality `user_id` before low-cardinality
  `event_name`.
  - Current: `ORDER BY (user_id)`
  - Required: `ORDER BY (event_name, user_id)` — low-to-high
    cardinality, AND `event_name` is the more selective filter
  - Fix: see `rules/schema-pk-cardinality-order.md`

- **schema-pk-prioritize-filters**: `event_name` is the
  dominant filter column in query patterns, but is not in
  ORDER BY.
  - Current: `ORDER BY (user_id)`
  - Required: `event_name` must lead ORDER BY (or be the
    only column) for filter-aligned queries to use the
    primary index.
  - Fix: reorder as above.

- **schema-types-minimize-bitwidth**: `id` is `UUID` (16
  bytes) but the user message never queries by id alone —
  it's only emitted as a response.
  - Current: `id UUID`
  - Required: keep UUID for now, but if id is never
    filtered on, consider `UInt128` for compactness. Low
    priority unless table is > 1B rows.

## Recommendations
1. CRITICAL: reorder ORDER BY to `(event_name, user_id)` —
   flips primary index selectivity, fixes 2 violations
2. LOW: re-evaluate `id` type once table size is known
```
