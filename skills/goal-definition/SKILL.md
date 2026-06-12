---
name: Goal Definition
name_zh: 目标定义
description: '|'
description_zh: 在动手前把一个模糊的意图重写成一个具体、可衡量的目标 —— 
  用具体语言复述、优先采用数字证据、拒绝纯活动型目标，只在真正达标时再记录。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - database
  - evaluation
source:
license: MIT
language: en
author: 'OpenAI (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: goal-definition
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

The user said "I want to…" or "let's set a goal" or
"what should the success criteria be?" — and the
intention is still fuzzy. The output is a single
objective string the rest of the work can be measured
against, **not** a project plan, decision log, or
backlog.

Use this when:

- The user explicitly asks to define a goal, set
  success criteria, or sharpen an objective.
- A task is multi-step and the team needs agreement
  on what "done" means before starting.
- The existing goal is vague ("improve things",
  "make progress", "investigate X") and needs to be
  rewritten before it can drive work.

**Do not** use this to plan, design, or execute the
work itself. The output is one objective string, not
a roadmap.

# Inputs

- `intent` — the fuzzy thing the user wants to
  accomplish, in their own words.
- `artifact_scope` (optional) — which repo, system,
  or surface the goal targets.
- `budget` (optional) — only set when the user
  explicitly asked for a token or time budget.

# Output

Either a `## REWRITE` block (the original intent
fails the quality bar — propose a concrete rewrite
and ask the user to confirm), or a `## GOAL` block
with a one-sentence objective and a short evidence
section.

The objective must name:

- the **specific outcome** that will be true
- the **artifact / system** it touches
- how completion will be **verified**
- what is **in scope** and out of scope
- the **stop condition** for asking vs. grinding

# Prompt

```prompt
You are a senior engineer turning a fuzzy intention
into an objective the rest of the work can be
measured against. The output is ONE objective
string, not a plan.

## Decision: do we actually need a goal?

Use this skill when the user:
  - asks to "set a goal", "define success", or
    "what does done look like?"
  - gives a multi-step task that needs agreement
    before anyone starts
  - presents a goal that is too vague to drive work
    and explicitly asks to sharpen it

Skip this skill when:
  - the user only wants ordinary implementation work
    — just do the work
  - the user wants durable snapshots, decision logs,
    or resume files — different skill
  - the goal is already concrete enough — confirm
    and proceed

## Restate in concrete terms

A usable goal names:
  1. the specific outcome that will be true when done
  2. the main artifact, system, repo, environment,
     or user-facing behavior involved
  3. how completion will be verified
  4. what is in scope
  5. what is out of scope when ambiguity would matter
  6. the stop condition for asking the user instead
     of grinding

## Make it quantitative when the domain supports it

Prefer numbers that represent real success, not
decorative precision:
  - pass/fail validators: exact tests, CI jobs,
    evals, commands, acceptance criteria
  - quality thresholds: latency, error rate, cost,
    accuracy, recall, precision, coverage, flake
    rate, bundle size, memory, uptime, completion
    rate
  - artifact constraints: file paths, affected
    modules, allowed commands, output formats,
    target environments, deadlines, blast radius
  - evidence counts: reproduced failures, reviewed
    examples, addressed comments, verified cases

## Repair weak goals before setting them

  - Rewrite vague goals into measurable objectives
    when local context makes the rewrite safe.
  - Ask one concise clarification question when the
    missing detail changes the intended outcome or
    validation.
  - Reject pure activity goals ("make progress",
    "keep investigating", "improve things", "work
    on X") unless sharpened into a verifiable
    outcome.

## Output

Pick exactly one of these two shapes.

### Shape A: REWRITE (goal fails the bar)

```markdown
## REWRITE
The original intent ("<user's words>") is too
vague to commit to. Suggested rewrite:

> <one-sentence objective with concrete evidence
and scope bounds>

Confirm or correct:
  - Is this the outcome you want?
  - Is the evidence type right?
  - Anything missing from the scope?
```

### Shape B: GOAL (goal passes the bar)

```markdown
## GOAL
<one-sentence objective with concrete evidence
and scope bounds, ≤ 30 words>

### Evidence
- <validator 1 — exact command / test / artifact>
- <validator 2 — exact threshold or acceptance
  criterion>

### Scope
In: <what is included>
Out: <what is excluded, only when ambiguity matters>

### Stop condition
Ask the user when: <decision the model must not
make on its own>
Grind through when: <work that should not require
check-ins>
```

## Quality bar (gate before Shape B)

The objective must answer all of:
  - What concrete thing will be true when this is
    done?
  - What evidence will prove it?
  - What quantitative or binary threshold defines
    success?
  - What is in scope and what is out?

If any of these is missing, fall back to Shape A
and ask the one most-important question.
```

# When NOT to use

- **The intention is already concrete** — confirm
  with the user, do not re-cast a working goal.
- **The user wants a project plan** — that's a
  planning skill, not a goal-setting one. This
  outputs one objective string.
- **The user wants durable snapshots, decision
  logs, or resume files** — those are different
  artifacts; this skill only writes the goal.
- **The user is asking ordinary "do the work"
  questions** — skip goal creation, just do the
  task.
- **The goal is pure activity** ("investigate",
  "make progress", "look into it") and cannot be
  sharpened — push back and ask why before
  committing.

# Example

**Input:**

```yaml
intent: "make the API faster"
artifact_scope: "internal billing service"
budget: 0
```

**Output:**

```markdown
## REWRITE
The original intent ("make the API faster") is
too vague to commit to. Suggested rewrite:

> Cut p95 latency of the billing service's
> `POST /charge` endpoint from 480ms to ≤ 200ms
> on the production-us region, verified by a
> load test of 500 RPS for 10 minutes, with no
> regression in the existing 5xx rate.

Confirm or correct:
  - Is p95 latency on `POST /charge` the right
    outcome, or do you care about a different
    endpoint / percentile?
  - Is 200ms a real product bar, or a stretch
    goal that needs review?
  - Anything else that should be in scope
    (caching, DB queries, downstream calls)?
```

**Input (vague activity that should be rejected):**

```yaml
intent: "investigate the dashboard issue"
budget: 0
```

**Output:**

```markdown
## REWRITE
The original intent ("investigate the dashboard
issue") is pure activity and not committable.
Two ways to sharpen it — pick one:

1. Diagnostic: "Identify the root cause of the
   p99 load-time regression on `/dashboards/team`
   by 2026-06-18, with a written root-cause
   analysis citing the offending commit(s) and
   proposed fix paths."
2. Resolution: "Bring p99 load time of
   `/dashboards/team` back under 2.0s on
   production-us, verified by the 24h RUM
   dashboard, by 2026-06-25."

Which is it — diagnose, or fix?
```
