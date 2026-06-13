---
name: "Doc Co-Authoring Workflow"
name_zh: 文档共写工作流
slug: doc-coauthoring
description: "三阶段结构化文档共写工作流 - Context Gathering / Refinement & Structure / Reader Testing。当用户提到写文档、起草提案、创建 spec 时触发。跳出写完即发的陷阱。"
description_zh: "三阶段结构化文档共写工作流 - Context Gathering / Refinement & Structure / Reader Testing。当用户提到写文档、起草提案、创建 spec 时触发。跳出写完即发的陷阱。"
category: documentation
tags: [ai, documentation, frontend, llm, security]
source: null
license: MIT
author: AI-SKILL
version: 1.0.0
created: 2026-06-12
updated: 2026-06-12
needs_review: false
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

You're about to co-author a **substantial document** —
an RFC, a design doc, a PRD, a decision record, a
runbook, a tutorial. The user said "write a doc",
"draft a proposal", or "create a spec". The doc is
meant to be read by other humans (and often re-read
by an LLM later).

The three-stage workflow catches the most common
doc failures:

1. **Stage 1 — Context Gathering.** The user dumps
   what they know; the LLM asks clarifying questions.
   Skipping this stage is the most common cause of
   "the doc doesn't address the actual question" —
   the author never said what they actually wanted.
2. **Stage 2 — Refinement & Structure.** Iteratively
   build each section. Brainstorm, then tighten. The
   structure emerges from the content, not the other
   way around.
3. **Stage 3 — Reader Testing.** Test the doc with a
   fresh LLM (no context from the co-authoring
   session) and see if it works. This catches blind
   spots the author has because they know too much.

The "Reader Testing" stage is the most novel and
the most easily skipped. A doc that doesn't survive
a fresh-LLM test will not survive a fresh-human
test.

**Don't use this skill for** one-line changelog
entries, commit messages, or comments in code.
Use a writing skill or just write it.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `doc_type` | yes | Drives the section template. |
| `audience` | yes | Drives depth and assumed context. |
| `current_stage` | no | If omitted, start at stage 1. |

# Output

Plain-text next step. Typical return (stage 1):

```
Current stage: Context Gathering
Audience: engineering team

Questions to ask the user:
  - What is the decision or change this doc is
    proposing / recording?
  - Why now? What changes if we don't act?
  - Who is the audience beyond "engineering team"
    (e.g. on-call, security, leadership)?
  - Are there constraints or non-goals the
    proposal must respect?
  - What is the desired reader action after
    reading: align? review? approve? implement?

Section template (for stage 2):
  1. Context: why this doc exists
  2. Decision / Proposal: what we're doing
  3. Alternatives considered
  4. Open questions
  5. Rollout plan
  6. Risks

Next action: wait for the user's answers to the
questions; do NOT start drafting yet.
```

# Prompt

```prompt
You are co-authoring a substantial document with the
user. Follow the three stages in order. Do not skip
stage 3 (Reader Testing) — it's the most novel and
the most easily skipped.

1. Identify the doc type and audience.

   Ask:
     - What kind of doc? (RFC, design doc, PRD,
       decision record, runbook, tutorial)
     - Who reads this? (Engineering? Leadership?
       External partners? On-call?)
     - What's the desired reader action? (Align?
       Review? Approve? Implement?)

   The answer to "desired reader action" drives
   the structure. A doc whose reader is supposed
   to "approve" needs Risks and Open Questions
   up front. A doc whose reader is supposed to
   "implement" needs a Rollout plan and
   concrete examples.

2. Stage 1 — Context Gathering.

   Goal: the user dumps everything they know; you
   ask clarifying questions.

   - Ask 3-7 open-ended questions. Do NOT start
     drafting until the user has answered.
   - The questions should expose:
       - the actual problem (not the surface
         request)
       - constraints and non-goals
       - the audience and their prior context
       - the desired reader action
       - what would make the user say "this
         doc is done"
   - Capture the user's answers verbatim or
     near-verbatim. The wording carries nuance
     the LLM may not infer.

   Do NOT skip this stage. A doc written without
   context is a doc that doesn't address the
   actual question.

3. Stage 2 — Refinement & Structure.

   Goal: iteratively build each section.

   For each section:
     a) Brainstorm: the user (and you) dump
        everything relevant. Don't worry about
        order.
     b) Cluster: group related ideas into
        paragraphs.
     c) Tighten: rewrite for clarity. Replace
        phrases with shorter ones. Replace
        adjectives with facts.
     d) Move on to the next section.

   The structure emerges from the content. Do NOT
   pick a template first and force the content
   into it. The template is a checklist at the
   end, not a starting point.

   Section templates (suggested, not required):
     - RFC:        Context, Proposal, Alternatives,
                   Open Questions, Rollout
     - Design doc: Problem, Goals, Non-Goals,
                   Design, Alternatives, Open
                   Questions
     - PRD:        Background, Goals, User Stories,
                   Requirements, Out of Scope,
                   Open Questions
     - Decision record: Context, Decision,
                   Consequences, Alternatives
     - Runbook:    Symptoms, Root Cause, Fix,
                   Verification, Escalation
     - Tutorial:   Goal, Prerequisites, Steps,
                   Verification, Next Steps
     - FAQ:        Audience context, Question,
                   Answer, Related

4. Stage 3 — Reader Testing.

   Goal: confirm the doc works for a reader who
   has none of the context the author has.

   - Open a fresh LLM session (no chat history
     from stages 1-2).
   - Give it ONLY the doc text. No "we discussed
     this earlier" references.
   - Ask the reader-LLM to answer:
       - What is this doc proposing / recording?
       - What is the desired reader action?
       - What are the open questions?
       - What did the author forget to mention?
   - If the reader-LLM's answer is materially
     different from what the user intended, the
     doc is broken. Fix and re-test.

   Do NOT skip this stage. A doc that doesn't
   survive a fresh-LLM test will not survive a
   fresh-human test. The reader-LLM is a
   cheap proxy for a busy colleague.

5. End-of-stage checklist.

   Before declaring done:
     - Reader-LLM can answer "what is this
       proposing?" correctly.
     - All "Open Questions" have a status
       (open, deferred, answered, parked).
     - The audience's prior context is
       explicit, not assumed.
     - The desired reader action is named.
     - The non-goals are listed.
     - The risks are named.
     - The user has approved the final version.
```

# When NOT to use

- **The doc is a one-line changelog entry or
  commit message.** Use a writing skill or just
  write it.
- **You skip stage 1 (Context Gathering) and
  start drafting from a template.** The most
  common doc failure is "doesn't address the
  actual question". Stage 1 catches it.
- **You treat the section template as a
  starting point.** The template is a checklist
  at the end. Starting from the template
  produces a doc that fits the template but
  doesn't fit the content.
- **You skip stage 3 (Reader Testing).** A doc
  that doesn't survive a fresh-LLM test will
  not survive a fresh-human test. The reader
  test is the cheapest way to catch blind spots
  the author has.
- **The reader-LLM's answer is materially
  different from the user's intent and you
  declare the doc done anyway.** A doc the
  reader can't understand is not a doc.
- **You re-use the chat history from stages
  1-2 in the reader test.** The reader-LLM
  has none of the context the author has. A
  fresh session is the point.
- **You write the doc for yourself, not the
  audience.** The audience drives depth and
  assumed context. An exec doc that dives
  into implementation details is wrong. An
  engineering doc that hand-waves
  implementation is also wrong.
- **You forget the non-goals.** A doc without
  non-goals is a doc where everything is
  in-scope. That's not a doc, that's a
  brain dump.
- **You ship before the user has approved.**
  Stage 3 is a check, not a sign-off. The
  user has to say "yes" before the doc
  goes to the audience.
- **You treat the doc as a one-shot.** Most
  substantial docs are revised at least
  once. Plan for iteration; the
  three-stage workflow is the iteration
  tool.

# Example

**Input:**

```yaml
doc_type: design-doc
audience: engineering team
current_stage: gather
```

**Output:**

```
Current stage: Context Gathering
Audience: engineering team

Questions to ask the user:
  1. What is the change this doc is proposing?
     (one sentence)
  2. Why now? What changes if we don't act?
  3. Are there constraints or non-goals the
     proposal must respect (e.g. backward
     compatibility, deadline, dependencies)?
  4. Who is the audience beyond "engineering
     team" (e.g. on-call, security, leadership)?
  5. What is the desired reader action after
     reading: align? review? approve?
     implement?
  6. What would make you say "this doc is done"?

Section template (for stage 2):
  1. Problem
  2. Goals
  3. Non-Goals
  4. Design
  5. Alternatives Considered
  6. Open Questions
  7. Rollout

Next action: wait for the user's answers; do NOT
start drafting the doc.
```
