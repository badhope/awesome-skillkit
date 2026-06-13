---
name: Internal Comms Authoring
name_zh: 内部沟通文档写作
description: 'You''re drafting a **piece of internal communication** —'
description_zh: '写七种常见的内部沟通文档 —— 3P update、status report、领导汇报、项目进展、incident report、FAQ answer、公司 newsletter。每种有结构、语气、提前要收集的素材清单。通用，适用于任何公司。'
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - deployment
source: null
license: Complete terms in LICENSE.txt
author: 'Anthropic (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: internal-comms
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

You're drafting a **piece of internal communication** —
a 3P update, a status report, a leadership update, a
project update, an incident report, an FAQ answer, or
a company newsletter. The reader is inside the
organisation; the format and tone are scoped to that.

Each of the seven types has a structure that fits the
way the reader will read it:

- **3P update** — Progress / Plans / Problems. Scannable
  bullets. Read at standup or async on Monday.
- **Status report** — short. What changed since the last
  one. Often a regression table.
- **Leadership update** — decisions needed, not status.
  Stop reading if you are not the decision owner.
- **Project update** — narrative. What moved, what's
  next, what's blocking.
- **Incident report** — facts, timeline, root cause,
  follow-ups. No narrative, no blame.
- **FAQ answer** — one question, one answer, related.
  Scannable for the answer in the first sentence.
- **Company newsletter** — curated highlights,
  not a status report. Light tone.

If you don't know which one it is, default to
`general-comms` and ask the user.

**Don't use this skill for** external communications
(customer-facing blog posts, press releases, support
responses) — those have different audience expectations
and different review paths.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `comm_type` | yes | The 8-value enum above. |
| `audience` | yes | Reader. Drives tone and depth. |
| `period` | no | Time window. |
| `raw_inputs` | no | Source material. |

# Output

Plain-text draft + a "left out" block. Typical return:

```
## Incident — 2026-06-09, 14:22 UTC, prod-us

**What happened:** API latency spiked to 8s for 11
minutes, affecting all read endpoints.

**Timeline:**
- 14:22 — alert fired: p95 latency > 5s
- 14:23 — on-call engaged
- 14:25 — root cause identified: a single ClickHouse
  query with a missing ORDER BY prefix column
- 14:31 — query pinned to a specific shard to bypass
  the bad plan
- 14:33 — latency recovered

**Root cause:** The query plan regressed when the
underlying table's ORDER BY was changed in a migration
that did not include a query rewrite.

**Customer impact:** ~0.4% of read requests in the
window returned >5s responses. No data loss.

**Follow-ups:**
- [ ] Add a regression test that fails when a query
      uses the new ORDER BY without the rewrite
- [ ] Audit other queries against the same migration
- [ ] Postmortem scheduled for 2026-06-12

---

**Left out and why:**
- Names of the on-call engineers (audience is
  cross-team, not leadership; incident-report is not
  the place for credit)
- The internal Slack channel link (not shareable)
- The customer's specific error code (jargon for the
  audience)
```

# Prompt

```prompt
You are drafting an internal communication. Pick the
type, identify the audience, gather the right
material, draft, then explain what you left out.

1. Identify the comm type.

   If the user is vague, ask. Default to `general-comms`
   only as a last resort. The 7 named types each have
   a structure that fits how the reader will read.

   - 3p-update            → Progress / Plans / Problems
   - status-report        → short, what changed since last
   - leadership-update    → decisions needed, not status
   - project-update       → narrative, what moved / next
                             / blocking
   - incident-report      → facts, timeline, root cause,
                             follow-ups
   - faq-answer           → one question, one answer
   - company-newsletter   → curated highlights, light
                             tone

2. Identify the audience.

   - team          — direct colleagues, full jargon OK
   - leadership    — VPs, C-suite. Decisions needed.
                     No jargon, no status, no detail
                     unless asked.
   - company       — full company. Inclusive tone. No
                     team-internal references.
   - cross-team    — peers in another team. Brief
                     context on what your team does.
   - customers     — internal "customers" (e.g. sales,
                     support). No internal-only terms.
   - external      — partners, vendors. No insider
                     references.

   The audience drives the depth and what NOT to
   include. A leadership update that includes
   build-pipeline tweaks is wrong.

3. Gather material (don't draft yet).

   3p-update gather list:
     - what got done since last update
     - what's planned for next period
     - what's blocking or at risk

   status-report gather list:
     - metrics (if any) since last report
     - incidents (link, not narrative)
     - on-track / at-risk items
     - asks of the reader

   leadership-update gather list:
     - decisions the leadership must make
     - context for each decision (one paragraph)
     - recommended choice (don't make leadership
       pick between options without a recommendation)
     - cost of inaction (what happens if we don't
       decide this week)

   project-update gather list:
     - what moved since last update (3-5 bullets)
     - what's next (3-5 bullets)
     - blockers (1-3 bullets)
     - asks (1-3 bullets)

   incident-report gather list:
     - facts only: what, when, where, who detected,
       who responded
     - timeline with timestamps (UTC, minutes)
     - root cause (single sentence)
     - customer impact (numbers, not adjectives)
     - follow-up action items (with owners)

   faq-answer gather list:
     - the question, verbatim
     - the short answer (one sentence, first)
     - the longer explanation
     - related questions

   company-newsletter gather list:
     - 3-5 highlights (wins, launches, hires)
     - 1-2 community items
     - no status reporting, no project updates

4. Draft.

   Use the type's structure. Length:
     - 3p-update          → 5-10 bullets
     - status-report      → 1 page
     - leadership-update  → 1 page
     - project-update     → 1-2 pages
     - incident-report    → 1-2 pages
     - faq-answer         → 1 paragraph + optional
                             longer
     - company-newsletter → 1 page

   The reader will read this once. Front-load the
   conclusion. The first sentence is the answer.

5. Output a "Left out and why" block.

   List the things you considered but didn't include,
   and why. This is critical for:
     - jargon filtered out (so the user can re-add
       it if the audience is wrong)
     - details that would distract (so the user can
       re-add them if the audience needs them)
     - names, channels, or links that don't belong
       in this audience

   The block is the safety net for the next reviewer.
```

# When NOT to use

- **You start drafting before gathering material.**
  A 3P update without a Plan bullet is a 2P update.
  An incident report without a timeline is a tweet.
  Gather first, draft second.
- **You front-load context instead of the answer.**
  The reader reads once. The first sentence is the
  answer. The rest is support.
- **You mix comm types.** A 3P update that opens
  with a 200-word leadership-update is wrong. Pick
  one type and stick to it.
- **You put jargon in a leadership or company
  audience piece.** "We migrated to VTT-13" means
  nothing to leadership. Strip or rename.
- **You write an incident report as a narrative.**
  Incident reports are facts + timeline + root
  cause + follow-ups. The narrative is for the
  postmortem, not the report.
- **You forgot the follow-ups on an incident report.**
  A report without action items is a story. The
  follow-ups are the actual fix.
- **You use `general-comms` as a default.** Default
  to a specific type. `general-comms` is a fallback
  when nothing fits, not a default.
- **You forgot the "Left out and why" block.** That
  block is the safety net for the next reviewer. A
  draft without it is opaque about its choices.
- **You added a section the user did not ask for.**
  A status report does not need "Q&A". A leadership
  update does not need "Fun fact of the week". Keep
  the structure tight.
- **You wrote a company newsletter as a status
  report.** Newsletters are curated highlights, not
  the weekly all-hands. Different tone, different
  content.

# Example

**Input:**

```yaml
comm_type: incident-report
audience: company
period: 2026-06-09
raw_inputs:
  - "API latency spiked 14:22 to 14:33 UTC"
  - "Read endpoints affected; writes unaffected"
  - "0.4% of read requests returned >5s"
  - "No data loss"
  - "Root cause: a query plan regression after a
     ClickHouse migration that changed the table's
     ORDER BY"
```

**Output:**

```
## Incident — 2026-06-09, 14:22 UTC, prod-us

**What happened:** API latency spiked to 8s for 11
minutes, affecting all read endpoints. ~0.4% of
read requests in the window returned >5s. No data
loss.

**Timeline:**
- 14:22 — alert fired: p95 latency > 5s
- 14:23 — on-call engaged
- 14:25 — root cause identified: a ClickHouse query
  with a missing ORDER BY prefix column
- 14:31 — query pinned to a specific shard to bypass
  the bad plan
- 14:33 — latency recovered

**Root cause:** The query plan regressed when the
underlying table's ORDER BY was changed in a
migration that did not include a query rewrite.

**Customer impact:** ~0.4% of read requests in the
window returned >5s responses. No data loss.

**Follow-ups:**
- [ ] Add a regression test that fails when a query
      uses the new ORDER BY without the rewrite
- [ ] Audit other queries against the same migration
- [ ] Postmortem scheduled for 2026-06-12

---

**Left out and why:**
- Names of the on-call engineers (audience is
  company, not leadership; incident-report is not
  the place for credit)
- The internal Slack channel link (not shareable)
- The customer's specific error code (jargon for
  the audience)
```
