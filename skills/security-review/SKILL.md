---
name: Security Review Checklist
name_zh: 安全审查清单
description: 'You''re reviewing or designing a change that touches a'
description_zh:
category: guardrails
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
license: MIT
author: 'Langfuse (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: security-review
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

You're reviewing or designing a change that touches a
**security-sensitive surface**:

- a user-supplied URL, host, endpoint, or webhook target
- a new outbound HTTP request (fetch, axios, AWS SDK
  client init, OpenAI / Anthropic / Bedrock client with
  a custom baseURL)
- a new integration form (Settings → Integrations) that
  points at an external service
- a new tRPC procedure or public API route that mutates
  project-scoped data or changes who can access it
- secrets, API keys, signing secrets, encryption-at-rest
  fields
- redirect-following or cross-origin header handling
- file uploads, image proxies, or binary data flowing in
  or out

The skill collects the **recurring findings** the team has
seen in external security reports so future agents catch
them at design and review time rather than after the fact.

The catalog is intentionally short and extensible. Each
topic is a thin reference file with: threat, canonical
helpers, known-good call sites, required defenses,
anti-patterns.

**Don't use this skill for** general code review (use a
`code-review` skill). And don't use it for compliance
(SOC 2, ISO 27001 — that's a separate audit pipeline).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `change_type` | yes | `review` / `design-plan` / `new-integration` / `new-procedure`. |
| `trigger_surfaces` | yes | Which security surfaces the change touches. |
| `repo_helpers_root` | no | Path to the project helpers. |

# Output

Plain-text findings report. Typical return:

```
Findings (3):

1. CRITICAL — SSRF (references/outbound-url-validation.md)
   File: web/src/server/api/routers/integrations.ts:127
   Current: `fetch(input.baseURL + path)` with no IP
            validation
   Required: `validateOutboundUrl(input.baseURL)` at
              save-time, plus DNS resolution check at
              use-time to defeat DNS rebinding
   Fix: copy the call site at
        web/src/server/api/routers/integrations.ts:152
        which already uses `validateOutboundUrl`

2. HIGH — Missing negative test
   File: web/src/server/api/routers/integrations.ts:127
   Missing test: private IP (127.0.0.1, 169.254.169.254)
   should be rejected at save time
   Add to: web/src/server/api/routers/integrations.test.ts

3. MEDIUM — Cross-tenant scope
   File: web/src/server/api/routers/projects.ts:89
   Procedure `updateProject` does not verify the caller
   is a member of the project being updated
   Required: ctx.session.user.memberOf(projectId)
   Fix: copy the call site at
        web/src/server/api/routers/projects.ts:42

Missing negative tests:
  - private IP rejection (127.0.0.1, 169.254.169.254,
    ::1, link-local)
  - cross-tenant access denied
  - redirect to private IP after fetch

Defer to:
  - code-review — for general code review
  - backend-dev-guidelines — for save-time vs use-time
    validation placement
```

# Prompt

```prompt
You are reviewing or designing a security-sensitive change.
Walk the trigger surfaces in order; cite the matching
reference for each finding.

1. Identify which trigger surfaces apply.

   Walk the change. For each surface below, decide
   "fires" or "not applicable":

   - user-supplied URL: does the change accept a URL,
     host, or endpoint from the user?
   - new outbound HTTP: does the change make a new
     outbound fetch / client init?
   - new integration form: is there a new admin-
     configurable network destination?
   - new procedure: is there a new tRPC / public API
     route that mutates project-scoped data?
   - secrets: does the change touch API keys, signing
     secrets, encryption-at-rest fields?
   - redirect following: does the change follow 3xx
     redirects or set cross-origin headers?
   - file upload: does the change accept binary input
     or proxy binary output (image, blob)?

2. For each firing surface, load the topic reference.

   Open the matching `references/<topic>.md` file.
   Each reference has:
     - Threat in plain language
     - Canonical helpers in the project
     - Known-good call sites to copy
     - Required defenses (save-time, use-time, etc.)
     - Anti-patterns to flag in review

   Do NOT skip reading the reference. Citing a topic
   without reading it is a misapplication.

3. Output findings ordered by severity.

   CRITICAL: direct exploit path (SSRF, secret leak,
             auth bypass, SQLi)
   HIGH:     missing validation that would lead to a
             finding if exploited
   MEDIUM:   hardening gap, defense in depth
   LOW:      nice-to-have (logging, rate limit headers)

   For each finding:
     a) Cite the topic file
     b) File:line of the issue
     c) Current behaviour (what the code does)
     d) Required behaviour (what it should do)
     e) Fix: name the canonical helper or call site to
        copy
     f) If a negative test is missing, name it as a
        finding — not a nice-to-have

4. Output expectations for design-plan mode.

   When the skill is used in design mode (not reviewing
   code), restate which surfaces the new feature exposes
   and name the validator or helper that must be invoked
   at which layer:

     - save-time:     validation when the user submits
                      the form
     - use-time:      validation at each fetch / client
                      init
     - connection-time: validation at the transport
                        layer
     - redirect-time: validation on every 3xx hop

   "We will validate later" is a design defect.
   Validation belongs in the same change that introduces
   the surface.

5. Defer to the right skill.

   - general code review: hand off to `code-review`
   - save-time vs use-time placement:
     hand off to `backend-dev-guidelines`
   - Linear handoff for confirmed issues:
     hand off to `linear-bug-triage` (or your
     project's bug-triage skill)

6. Treat missing negative tests as findings.

   For each finding, name the test that should exist
   to prevent regression. Examples:
     - private IP (127.0.0.1, 169.254.169.254, ::1,
       link-local) rejected at save
     - cross-tenant access denied
     - redirect to private IP blocked
     - missing scope on a procedure raises 403
     - secret round-trip through encryption-at-rest is
       byte-identical

   Add these to a "Missing negative tests" block at
   the end of the report.
```

# When NOT to use

- **The change does not touch a security surface.**
  This skill is for SSRF, secrets, RBAC, file uploads,
  redirect, cross-tenant data. General code review is
  not this skill's job.
- **You cite a topic reference without reading it.**
  The reference file is short. Read it. Citing from
  memory leads to misapplication (e.g. forgetting
  use-time validation in addition to save-time).
- **You treat "we'll validate later" as acceptable.**
  In design-plan mode, validation belongs in the same
  change. A follow-up is a finding, not a plan.
- **You write findings without file:line references.**
  "There may be SSRF in the integrations code" is not
  a finding. "integrations.ts:127 does X" is.
- **You conflate the catalog with the full threat
  model.** The catalog covers the *recurring* findings.
  A novel issue is still a finding, even if it doesn't
  have a reference file.
- **You treat missing negative tests as nice-to-haves.**
  They are findings. A finding without a regression
  test will come back.
- **You hand off confirmed issues to "the security
  team" without a reproduction.** Confirmed issues go
  through the project's bug-triage skill, not vague
  escalation. Reproduction evidence is required.
- **You only check the surface the change introduced.**
  Existing code in the same file can also be vulnerable.
  A PR adding a new field to an integration form should
  also re-review the form's URL handling.
- **You skip the use-time check.** Save-time validation
  alone is not enough: a user can save a benign URL and
  then later rebind the DNS to a private IP (DNS
  rebinding). The use-time check (resolve and re-validate
  the IP just before connecting) is what closes the
  gap.

# Example

**Input:**

```yaml
change_type: review
trigger_surfaces:
  - user-supplied-url
  - new-outbound-http
  - new-procedure
```

**Output:**

```
Findings (3):

1. CRITICAL — SSRF / outbound URL validation
   (references/outbound-url-validation.md)
   File: web/src/server/api/routers/integrations.ts:127
   Current: `fetch(input.baseURL + path)` with no IP
            validation
   Required: `validateOutboundUrl(input.baseURL)` at
              save-time, plus DNS resolution check at
              use-time to defeat DNS rebinding
   Fix: copy the call site at
        web/src/server/api/routers/integrations.ts:152
        which already uses `validateOutboundUrl`

2. HIGH — Missing negative test
   File: web/src/server/api/routers/integrations.ts:127
   Missing: private IP (127.0.0.1, 169.254.169.254, ::1,
   link-local) should be rejected at save time
   Add to: web/src/server/api/routers/integrations.test.ts

3. MEDIUM — Cross-tenant scope
   File: web/src/server/api/routers/projects.ts:89
   Procedure `updateProject` does not verify the caller
   is a member of the project being updated
   Required: ctx.session.user.memberOf(projectId)
   Fix: copy the call site at
        web/src/server/api/routers/projects.ts:42

Missing negative tests:
  - private IP rejection
  - cross-tenant access denied
  - redirect to private IP blocked

Defer to:
  - code-review
  - backend-dev-guidelines
```
