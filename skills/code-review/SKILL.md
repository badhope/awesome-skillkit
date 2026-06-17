---
name: Code Review Workflow
name_zh: 代码审查工作流
description: 'Canonical code-review workflow for any PR, branch, diff, or local change.
  Findings ordered by severity, defer to specialist skills when needed.'
description_zh:
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
license: MIT
author: 'Langfuse (downstream pack: badhope)'
version: '1.0.0'
needs_review: false
slug: code-review
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

You're **reviewing code** — a PR, a branch, a diff, or
local changes. The job is correctness, regressions,
risk, and missing tests. You are not the author; you
are the second pair of eyes.

The skill is built around three rules:

1. **Findings first, ordered by severity.** Never
   start with "looks good overall" and then hide the
   critical finding. The reviewer who reads the first
   line should see the worst issue.
2. **Defer to specialised skills.** When the change
   touches a domain with a dedicated skill — security,
   ClickHouse, frontend architecture, MCP — the
   review defers to that skill for the domain-specific
   checks. This skill covers the generic parts.
3. **No findings is a valid result.** If the change
   is clean, say so. Don't invent findings to fill
   space. Note residual risk and coverage gaps so the
   next reviewer knows what to look at.

**Don't use this skill for** implementing a feature
(use the feature's own skill). And don't use it as a
replacement for security review — defer to the
security-review skill on the same change.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `change_scope` | yes | PR number / URL / branch / diff path / "local". |
| `areas_touched` | no | Drives which specialised skills to consult. |
| `severity_threshold` | no | Lowest severity to report. Default `medium`. |

# Output

Plain-text review. Typical return:

```
Findings (3):

1. CRITICAL — Missing tenant isolation check
   File: web/src/server/api/routers/projects.ts:89
   Procedure `updateProject` does not verify the
   caller is a member of the project being updated.
   Required: ctx.session.user.memberOf(projectId)
   Fix: copy the call site at
        web/src/server/api/routers/projects.ts:42

2. HIGH — Missing test
   File: web/src/server/api/routers/projects.ts:89
   No test covers cross-tenant access denial.
   Add: web/src/server/api/routers/projects.test.ts
   case "user from project A cannot update project B"

3. MEDIUM — Untyped error response
   File: web/src/server/api/routers/projects.ts:104
   Error returned as `throw new Error(...)` instead of
   `throw new TRPCError({ code: 'FORBIDDEN' })`.
   Required: typed errors with code so the client can
   distinguish 401 / 403 / 404.

Deferred to:
  - security-review  (cross-tenant, RBAC)
  - frontend-large-feature-architecture (no — purely
     backend in this PR)

Residual risk:
  - did not run the test suite locally; CI must
    confirm
  - did not review the corresponding Fern SDK
    generator output
```

# Prompt

```prompt
You are reviewing code, not writing it. Output
findings first, ordered by severity, with file:line
references. No findings is a valid result.

1. Read the canonical review checklist first.

   Most repos have a `references/review-checklist.md`
   (or equivalent: `CONTRIBUTING.md`, `docs/review.md`,
   `AGENTS.md`). Read it. It encodes the rules the
   team has already agreed on. Do not duplicate those
   rules in your review.

   Examples of canonical rules (project-specific):
     - ClickHouse / Postgres migration expectations
     - tenant isolation checks
     - API generator (Fern / OpenAPI / tRPC) consistency
     - env var access patterns
     - banner-offset UI positioning

2. Identify the area(s) the change touches.

   - frontend     — UI, components, state, styles
   - backend      — API, business logic, queues
   - security     — auth, RBAC, secrets, outbound HTTP
   - database     — schema, migration, query
   - ci           — workflows, build, deploy
   - docs         — prose, examples, READMEs
   - infra        — terraform, k8s, network
   - mobile       — iOS / Android
   - none         — minor doc typo, comment-only

3. Defer to the specialised skill for the area.

   - security → also use the `security-review` skill
   - database (ClickHouse) → also use the
     `clickhouse-best-practices` skill
   - frontend (large feature) → also use the
     `frontend-large-feature-architecture` skill
   - database migration → also use the repo's
     migration checklist (often in the canonical
     review checklist)
   - new MCP server → also use the `mcp-builder`
     skill

   Do not duplicate the specialised skill's checks.
   Defer; cite; move on.

4. Focus the review on the four priorities.

   - correctness bugs         (does it work)
   - behavioural regressions   (did it break what
                                worked)
   - security / tenant risks   (who can access what)
   - missing / weak tests      (for risky changes)
   - performance w/ real impact (only if measurable)

   Do NOT report:
     - style nits the linter should catch
     - bikeshed naming
     - "I'd do it differently" without a concrete
       reason
     - speculative future-proofing

5. Output format.

   Findings first, ordered by severity:

     CRITICAL: correctness bug or direct exploit
     HIGH:     missing validation, missing test for
               a risky change
     MEDIUM:   hardening gap, defense in depth
     LOW:      nice-to-have, log / metric

   For each finding:
     - file:line
     - current behaviour
     - required behaviour
     - fix (name the call site to copy, or the
       canonical helper)

   After findings:
     - short summary (1-3 sentences)
     - list of specialised skills deferred to
     - residual risk: what you couldn't verify

   If there are no findings at or above the
   severity threshold, say so explicitly. Note any
   coverage gaps so the next reviewer knows where to
   look.

6. Honour the severity threshold.

   `critical-only` — only CRITICAL. Fast triage.
   `high`          — HIGH and above.
   `medium`        — MEDIUM and above (default).
   `low`           — everything, including LOW.
```

# When NOT to use

- **You're implementing a feature.** Use the
  feature's own skill. Code review is for the second
  pair of eyes, not the author.
- **You start with "looks good overall" before the
  findings.** The first line of the review should be
  the worst finding, not a compliment.
- **You duplicate the canonical review checklist.**
  The checklist is the source of truth. Read it;
  cite it; move on. Don't restate it in the review.
- **You report style nits the linter should catch.**
  A linter-fixed issue is not a finding.
- **You write findings without file:line references.**
  "There may be a bug in the integrations code" is
  not a finding. "integrations.ts:127 does X" is.
- **You treat "no findings" as a failure of the
  review.** No findings is a valid result. The
  reviewer who invented findings to fill space is
  the one who failed.
- **You skip the deferral to specialised skills.**
  The generic review covers correctness, regression,
  security, tests, performance. Domain-specific
  checks belong to the domain skill. Defer.
- **You give the author a fix without a call site
  to copy.** "Use a transaction" is not a fix. "Use
  the withTransaction helper at db.ts:42" is.
- **You hand-wave residual risk.** If you didn't
  run the test suite, say so. If you didn't review
  the SDK generator output, say so. The next
  reviewer needs to know what was not checked.
- **You review a 5000-line PR in one pass.** Split
  by sub-feature if the change is large. The
  findings list is a multi-pass product.

# Example

**Input:**

```yaml
change_scope: "PR #1423 — add updateProject procedure"
areas_touched: [backend, security]
severity_threshold: medium
```

**Output:**

```
Findings (3):

1. CRITICAL — Missing tenant isolation check
   File: web/src/server/api/routers/projects.ts:89
   Procedure `updateProject` does not verify the
   caller is a member of the project being updated.
   Required: ctx.session.user.memberOf(projectId)
   Fix: copy the call site at
        web/src/server/api/routers/projects.ts:42

2. HIGH — Missing test
   File: web/src/server/api/routers/projects.ts:89
   No test covers cross-tenant access denial.
   Add: web/src/server/api/routers/projects.test.ts
   case "user from project A cannot update project B"

3. MEDIUM — Untyped error response
   File: web/src/server/api/routers/projects.ts:104
   Error returned as `throw new Error(...)` instead of
   `throw new TRPCError({ code: 'FORBIDDEN' })`.
   Required: typed errors with code so the client can
   distinguish 401 / 403 / 404.

Deferred to:
  - security-review  (cross-tenant, RBAC scope drift)
  - clickhouse-best-practices (no schema changes)

Residual risk:
  - did not run the test suite locally; CI must
    confirm
  - did not review the corresponding Fern SDK
    generator output
```
