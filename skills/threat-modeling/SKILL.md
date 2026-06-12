---
name: Repository Threat Model
name_zh: 仓库威胁建模
description: '|'
description_zh: 写一份基于仓库证据的威胁建模 —— 划定系统范围、画出信任边界、列出资产、枚举绑定到资产的滥用路径、用显式 likelihood
  × impact 推理排优先级、最后验证假设。每一句结论都要在仓库里找到证据，别写通用检查表。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
license: MIT
language: en
author: 'OpenAI (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: threat-modeling
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

The user said "threat model this", "what could go
wrong with this codebase", "do an AppSec review of
the X path", or is starting work on a sensitive
change (auth, payments, cross-tenant data, file
upload, new external service) and wants to know
the realistic abuse paths before writing code.

The output is a single markdown report
(`threat_model_<repo>.md` by default) that an
engineer can read in 5 minutes and an AppSec
reviewer can use as a starting point. It is
**not** a generic STRIDE dump — every claim cites
a file, function, or config in the repo.

Use this when:

- The change touches auth, payments, or any
  cross-tenant data path
- The repo is going through a security review
  or an external audit
- A new external integration is being added
- A previously-written threat model is more than
  6 months old and the system has changed

**Do not** use this for general architecture
summaries, plain code review, or non-security
design work. For that, use the `code-review` skill
or `security-review` skill.

# Inputs

- `repo_path` — path to model.
- `in_scope_paths` (optional) — limit scope.
- `deployment_model` (optional) — how the system
  runs. `unknown` means infer from the repo.
- `existing_assets` (optional) — known
  crown-jewel assets to short-circuit asking.

# Output

A markdown file (default location
`threat_model_<repo>.md`) with seven sections.
The Threats section is the load-bearing one — 5-10
abuse paths, each tied to an asset, each with
likelihood and impact, each with a one-sentence
mitigation.

# Prompt

```prompt
You are writing a repository-grounded AppSec
threat model. Anchor every architectural claim
to evidence in the repo (file path, function
name, config key). Keep assumptions explicit.
Prefer realistic attacker goals and concrete
impacts over generic STRIDE dumps.

## 1. Scope and extract the system model

Identify, from the repo evidence:
  - Primary components and data stores
  - External integrations (HTTP clients, queues,
    SaaS APIs, message brokers)
  - How the system runs (server / CLI / library
    / worker) and its entry points
  - Runtime behavior vs CI / build / dev tooling
    vs tests / examples

Map the in-scope locations to those components.
Explicitly exclude out-of-scope items — readers
should not have to guess what was considered.

Do not claim components, flows, or controls
without citing a file.

## 2. Derive boundaries, assets, and entry points

Enumerate trust boundaries as concrete edges:

  - **Edge**: process boundary, network boundary,
    trust-domain boundary, tenant boundary
  - **Protocol**: HTTP / gRPC / file / queue
  - **Auth**: who authenticates at this edge
  - **Validation**: what is checked, by which
    code path
  - **Encryption**: in transit, at rest
  - **Rate limits**: per-edge or none

List the assets that drive risk:

  - Data (PII, credentials, model weights,
    signing keys)
  - Integrity-critical state (audit log,
    billing balance, role assignments)
  - Availability-critical components (auth
    service, payment gateway)
  - Build artifacts (release binaries, model
    checkpoints)

Identify entry points:

  - HTTP endpoints (file path + handler)
  - Upload surfaces (S3 buckets, multipart
    endpoints)
  - Parsers / decoders (JSON, protobuf,
    user-uploaded files)
  - Job triggers (cron, queue consumer, webhook)
  - Admin tooling (Django admin, kubectl
    exec, internal CLI)
  - Logging / error sinks (where untrusted
    data lands)

## 3. Calibrate attacker capabilities

Describe realistic attacker capabilities based on
exposure and intended usage. Examples:

  - **Unauthenticated internet user** —
    can hit any public endpoint, can upload
    arbitrary content, can send crafted JSON
  - **Authenticated low-privilege user** —
    can access own data, can probe for IDOR,
    can abuse expensive endpoints
  - **Authenticated cross-tenant user** —
    can attempt to read or write other tenants'
    data
  - **Malicious internal user** — has
    authenticated access to a subset of admin
    tooling
  - **Compromised dependency** — runs with
    the app's identity and can read env, files,
    network

Explicitly note non-capabilities to avoid
inflated severity (e.g. "this service is
single-tenant; cross-tenant attacks do not
apply").

## 4. Enumerate threats as abuse paths

Pick attacker goals that map to assets and
boundaries:

  - Exfiltration (PII, credentials, model
    weights)
  - Privilege escalation (user → admin,
    tenant A → tenant B)
  - Integrity compromise (audit log tampering,
    role assignment, billing balance)
  - Denial of service (auth service, payment
    gateway, expensive endpoint)

For each threat, write one paragraph:

  - **Asset(s)** impacted
  - **Boundary** the attacker crosses
  - **Entry point** they use
  - **Capability required** to attempt it
  - **Existing controls** that already reduce
    likelihood or impact
  - **Likelihood** (low / medium / high) with a
    one-sentence justification
  - **Impact** (low / medium / high) with a
    one-sentence justification
  - **Overall priority** = likelihood × impact,
    adjusted for existing controls (critical /
    high / medium / low)
  - **Mitigation** — a single concrete change
    that would lower the priority

Keep threats to 5-10. Quality over coverage.

## 5. Prioritize with explicit reasoning

State which assumptions most influence the
ranking. The most important threats to surface
are the ones where removing a single control
would jump priority by ≥ 2 levels.

## 6. Validate service context and assumptions

Before writing the final report, list the
assumptions that materially affect scope or
priorities:

  - Deployment topology (single-region vs
    multi-region, public vs internal)
  - Tenant model (single-tenant, multi-tenant,
    hybrid)
  - Auth model (session, JWT, mTLS, OIDC)
  - Data classification (PII, regulated data,
    public)
  - Out-of-scope components

Ask the user to confirm or correct these in
one batch. Do not write the final report until
assumptions are settled.

## 7. Final report format

```markdown
# Threat Model: <repo or scope>

## Scope
- In: <paths or components>
- Out: <paths or components, with reason>
- Deployment: <how it runs>
- Tenancy: <single / multi / hybrid>

## System model
- <one bullet per major component, with file
  reference>

## Trust boundaries
1. <edge name> — <protocol>, <auth>,
   <validation cite>, <encryption>,
   <rate limit>
2. ...

## Assets
- <asset 1 — file/citation>
- <asset 2 — file/citation>
- ...

## Threats

### T1 — <one-line summary>
- **Asset(s)**: ...
- **Boundary**: ...
- **Entry point**: ...
- **Capability required**: ...
- **Existing controls**: ...
- **Likelihood**: <low/med/high> — <reason>
- **Impact**: <low/med/high> — <reason>
- **Priority**: <critical/high/medium/low>
- **Mitigation**: <one concrete change>

(repeat for T2 ... TN)

## Mitigations not tied to a single threat
- <cross-cutting improvement>

## Assumptions to confirm
- <assumption 1>
- <assumption 2>
- ...
```
```

# When NOT to use

- **Generic STRIDE checklist** — this skill
  produces a repo-grounded model, not a
  one-size-fits-all list.
- **Architecture summary without security
  framing** — that's a different artifact.
- **One specific bug** — if you already know
  the bug, write a security review, not a
  threat model.
- **No access to the repo** — every claim
  needs a file/line citation; the model
  cannot fabricate those.
- **High-volume low-quality lists** — a
  50-threat checklist with no evidence is
  worse than 8 high-quality threats.

# Example

**Input:**

```yaml
repo_path: ./billing-service
in_scope_paths: [src/, migrations/]
deployment_model: saas
existing_assets: "Stripe API key in env, customer PII in PostgreSQL"
```

**Output (excerpt):**

```markdown
# Threat Model: billing-service

## Scope
- In: `src/`, `migrations/`
- Out: `frontend/` (separate repo, different
  threat surface)
- Deployment: multi-tenant SaaS, single
  region (us-east-1)
- Tenancy: row-level isolation by
  `tenant_id`; no physical separation

## System model
- `src/server.ts` — Express HTTP server,
  listens on :8080
- `src/billing/charge.ts` — Stripe wrapper
- `src/billing/webhook.ts` — POST
  /webhooks/stripe handler
- `migrations/` — PostgreSQL schema, includes
  `customers`, `charges`, `subscriptions`
  tables

## Trust boundaries
1. **Internet → Express** — HTTPS via ALB,
   JWT in `Authorization` header
   (`src/auth/jwt.ts:42`)
2. **Stripe → webhook** — POST with
   `Stripe-Signature` header verified in
   `src/billing/webhook.ts:18`
3. **Service → PostgreSQL** — private subnet,
   IAM auth via RDS token
   (`src/db/client.ts:11`)

## Assets
- Stripe secret key (env, not in repo)
- Customer PII (`migrations/004_customers.sql`)
- Stripe webhook signing secret
  (env, not in repo)
- `charges.balance_due` — integrity-critical
  (drives dunning)

## Threats

### T1 — webhook spoofing triggers duplicate
charge
- **Asset(s)**: `charges.balance_due`
- **Boundary**: Internet → Express (edge 1)
- **Entry point**: POST /webhooks/stripe
  (`src/server.ts:88`)
- **Capability required**: unauthenticated
  internet user, knowledge of endpoint
- **Existing controls**: signature
  verification at `webhook.ts:18`, but no
  replay protection (no event-id dedupe
  table)
- **Likelihood**: medium — endpoint is
  guessable, signature check is the only
  barrier
- **Impact**: high — duplicate charges
  trigger customer complaints and refund
  work
- **Priority**: high
- **Mitigation**: add a `processed_webhook_events`
  table with `event_id PRIMARY KEY`; reject
  inserts on duplicate
```

This skill is invoked by
`security-review` when the change introduces a
new external surface; pair the two skills
together.
