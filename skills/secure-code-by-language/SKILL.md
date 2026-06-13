---
name: Secure Code by Language
name_zh: 按语言的安全编码指南
description: 'The user said "write this securely", "do a security'
description_zh: '在写或审查代码前，按语言 / 框架查安全编码指南 —— 挑对参考文件（Python / JavaScript / TypeScript / Go / 前后端分查），按正确模式用（主动写、被动检测、完整报告）。只在用户明确说"secure by default"、"security review"或"AppSec"时触发，不接普通 code review 的活儿。'
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source: null
license: MIT
author: 'OpenAI (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: secure-code-by-language
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

The user said "write this securely", "do a security
review", "check this code against security best
practices", or "I'm starting a new <language> project
and want to follow the OWASP-style guidance from
day one". The skill is **explicit-only** — it does
not trigger on general code review, debugging, or
non-security tasks.

Use this when:

- Starting a new service in a supported language
- Adding a new external integration, auth flow,
  or data path
- The user explicitly asks for a security review
  or report
- Doing a periodic AppSec audit of an existing
  service

**Do not** use this for general code review
(that's `code-review`), for a single specific bug
(that's `security-review` with a smaller scope),
or for design work that has no security framing.

# Inputs

- `languages` — list all languages in the project
  (don't skip one even if you think it's not in
  scope).
- `frameworks` (optional) — list the major
  frameworks so the right reference file is
  loaded.
- `mode` — how to apply the guidance: proactive
  (write secure code going forward), passive
  detect (flag only, don't derail), or full
  report.
- `report_path` (optional) — where to write the
  full report when `mode=full-report`.

# Output

- `proactive` — a `## Checklist` of references
  loaded and the decisions the agent will apply
  going forward.
- `passive-detect` — inline notes attached to
  file:line locations as the agent does other
  work; do not derail the user's task.
- `full-report` — a markdown report at
  `report_path` (or
  `security_best_practices_report.md`) with
  severity sections and a finding ID per issue.

# Prompt

```prompt
You are applying language- and framework-specific
secure-by-default guidance to a codebase. Anchor
every claim to the matching reference file. The
goal is not to produce a 200-item checklist — it
is to write or review code that does not need a
re-audit.

## 1. Identify all languages and frameworks

From the repo, list:

  - **Languages** (Python / JavaScript /
    TypeScript / Go / other)
  - **Frameworks** (Express, FastAPI, Django,
    Gin, React, Next.js, etc.)
  - **Stack split** (frontend / backend /
    CLI / library / worker)
  - **Data classification** (PII, regulated,
    public, internal)

Be explicit. "The project uses TypeScript" is
not enough — list the runtime (Node, Bun, Deno)
and the framework (Express, Hono, NestJS).

## 2. Load the matching reference files

Reference filename convention:

  <language>-<framework>-<stack>-security.md
  <language>-general-<stack>-security.md

Examples:

  python-fastapi-backend-security.md
  typescript-express-backend-security.md
  javascript-general-web-frontend-security.md
  go-gin-backend-security.md

Load **all references** that match a language or
framework actually present in the repo. If the
repo has both a frontend and a backend, load
references for **both**. If the frontend
framework is unspecified, also load
`javascript-general-web-frontend-security.md`.

If a reference is missing, fall back to the
language-general reference for that stack. If
that is also missing, do not invent — note the
gap in the report and rely on your own knowledge
of the language and OWASP / CWE guidance.

## 3. Pick the operating mode

### Mode A: proactive (default)

Apply the loaded references to all code you
write from this point forward. The output is a
short `## Checklist` of references loaded and
the decisions applied, so the user can audit
your defaults later.

Common defaults to set:

  - Secret management: env vars, never in code,
    never in commit history
  - Input validation: validate at the edge,
    trust internal types
  - Output encoding: framework-default
    escaping, no `dangerouslySetInnerHTML` /
    `|safe` without justification
  - Auth: framework-default session or JWT
    library, not hand-rolled
  - Crypto: language stdlib, not
    hand-rolled; authenticated encryption for
    data at rest
  - Logging: structured logs, redact PII and
    secrets, never log Authorization headers

### Mode B: passive-detect

While doing other work (refactor, new feature,
bug fix), flag major issues as you encounter
them. Constraints:

  - **Focus on the largest impact**: critical
    and high-severity findings only
  - **Do not derail the user's task** — flag
    in one sentence with file:line, ask if
    they want a follow-up
  - **Cite the reference rule** that was
    violated

### Mode C: full-report

Write `security_best_practices_report.md` (or
`report_path`) with:

  - **Executive summary** (3-5 bullets, one
    sentence each)
  - **Critical findings** (with one-sentence
    impact statement per finding, finding ID
    like `SEC-001`, file:line citation)
  - **High findings**
  - **Medium findings**
  - **Low findings** (optional; skip if noisy)
  - **Reference index** (which references were
    loaded)

Number findings (`SEC-001`, `SEC-002`, ...)
so reviewers can refer to them. Include line
numbers for the cited code.

## 4. Overrides

Customers may have project-specific reasons to
bypass a best practice. When that happens:

  - Apply the override
  - Mention it to the user in one sentence
  - Suggest documenting the override in the
    project's own security notes (e.g.
    `SECURITY.md`) so the bypass is visible to
    future readers

Do not fight the user. A documented override
beats an unenforced rule.

## 5. Output

Pick the right shape for `mode`.

### Mode A output

```markdown
## Secure-by-default checklist

### Loaded references
- <reference file 1 — what it covers>
- <reference file 2 — what it covers>
- ...

### Decisions applied going forward
- <decision 1 — e.g. "All env-var secrets
  read via a typed config module, not
  `os.environ`">
- <decision 2 — e.g. "All SQL via the
  parameterized query builder, raw
  `cursor.execute` blocked at lint level">
- ...
```

### Mode B output

Inline notes only. Example:

  > `src/server.ts:42` — `app.use(cors())` with
  > no `origin` allowlist. Reference rule
  > `typescript-express-backend-security.md#cors`.
  > Want a follow-up fix?

### Mode C output

A markdown report file with the structure
described in section 3. Save the file, then
summarize the findings in chat (terse — name the
top 3, point at the file for the rest).
```

# When NOT to use

- **General code review** — use `code-review`.
  This skill is for explicit security review.
- **One specific bug** — use `security-review`
  with a smaller surface. This skill is for
  broad language-and-framework coverage.
- **No language reference available** — the
  skill needs reference files. If the language
  has no reference and you cannot apply known
  best practices honestly, say so; do not
  fabricate.
- **Bug-bounty triage** — that's an external
  workflow with its own rules. Use the
  appropriate intake skill.
- **A non-security design question** — the
  word "security" must appear in the user's
  intent for this skill to trigger.

# Example

**Input:**

```yaml
languages: [typescript, python]
frameworks: [nextjs, fastapi]
mode: full-report
```

**Output (excerpt):**

```markdown
# Security Best Practices Report

## Executive summary
- 2 critical, 3 high, 4 medium findings
- Primary risk: missing CSRF protection on
  FastAPI mutating endpoints (SEC-001)
- Secondary risk: `dangerouslySetInnerHTML`
  in three Next.js pages without sanitization
  (SEC-002)

## Critical

### SEC-001 — FastAPI mutating endpoints
lack CSRF protection
- **Impact**: An attacker can trick an
  authenticated user's browser into making a
  state-changing request to the API.
- **Location**: `app/api/charges.py:18`,
  `app/api/users.py:24`
- **Reference**: `python-fastapi-backend-security.md#csrf`
- **Fix**: Add a CSRF middleware that
  validates the `X-CSRF-Token` header on
  POST / PUT / DELETE / PATCH.

### SEC-002 — `dangerouslySetInnerHTML` in
Next.js pages without sanitization
- **Impact**: Stored XSS in the blog post
  body field can hijack any reader's session.
- **Location**: `pages/blog/[slug].tsx:31`,
  `pages/admin/preview.tsx:18`,
  `pages/marketing/landing.tsx:42`
- **Reference**: `javascript-general-web-frontend-security.md#xss`
- **Fix**: Render markdown via a sanitizing
  pipeline (DOMPurify, rehype-sanitize)
  before passing to `dangerouslySetInnerHTML`.
```

The full report is at
`security_best_practices_report.md`. The
references loaded were
`typescript-nextjs-frontend-security.md`,
`python-fastapi-backend-security.md`, and
`javascript-general-web-frontend-security.md`.
