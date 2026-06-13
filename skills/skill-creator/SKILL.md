---
name: Skill Authoring Loop
name_zh: 技能编写迭代流程
description: 'You''re authoring a **skill** — a self-contained'
description_zh: 从零创建新技能或改进已有技能 —— 起草、写测试 prompt、跑定性 + 定量评估、迭代 description 
  以提升触发准确率、扩充测试集、再来一遍。这个循环就是技能本身。
category: dev-tools
tags:
  - ai
  - backend
  - cli
  - database
  - documentation
source: null
license: Complete terms in LICENSE.txt
author: 'Anthropic (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: skill-creator
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

You're authoring a **skill** — a self-contained
Markdown file that an LLM can read and act on. Skills
take many forms: a code-review checklist, a test case
generator, a documentation co-authoring guide, a
debugging rubric. The shape of a good skill is the
same regardless of the topic.

The work is iterative, not write-once. The first
draft is rarely the final skill. The loop is:

1. **Decide** what the skill does and roughly how
2. **Draft** a SKILL.md
3. **Write** 5-10 test prompts
4. **Run** the skill (or an LLM with access to the
   skill) against the prompts
5. **Evaluate** the outputs qualitatively (eyeball)
   and quantitatively (metric)
6. **Iterate** the skill based on findings
7. **Expand** the test set to 30+ cases
8. **Repeat** steps 4-7 until quality plateaus

This is a meta-skill: it teaches the loop, not a
specific subject. The subject of each individual
skill is your problem to figure out.

**Don't use this skill for** one-off prompts (just
write a prompt). And don't use it for skills that
are essentially prompt-engineering collections
(that's a prompt library, not a skill).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `stage` | yes | `new-skill` / `draft` / `evaluate` / `iterate` / `expand`. |
| `skill_path` | no | Required for `draft` / `evaluate` / `iterate` / `expand`. |
| `target_description_accuracy` | no | Trigger accuracy goal. Default 0.9. |
| `eval_method` | no | `qualitative` / `quantitative` / `both` (default). |

# Output

Plain-text summary. Typical return (iterate stage):

```
Skill: skills/clickhouse-best-practices/SKILL.md
Qualitative findings (3):
  - description too broad; LLM triggers for any SQL
    question, not just ClickHouse
  - "When to use" is missing the "not just" clauses
    (rule fires for Postgres questions too)
  - "Prompt" section has the right structure but
    requires a lot of judgement from the LLM
Quantitative metrics:
  trigger_accuracy: 0.78 (target 0.90)
  output_completeness: 0.92
  wrong_trigger_rate: 0.18 (target < 0.05)
Proposed edits:
  1. Tighten description: "ClickHouse 28-rule review
     checklist. Use only for ClickHouse-specific
     questions (columnar, MergeTree, sparse index)."
  2. Add "When NOT to use" section listing Postgres,
     MySQL, DuckDB
  3. Convert step 4 in the Prompt section to a
     single decision question
```

# Prompt

```prompt
You are writing or improving a skill. The work is a
loop. The loop is the skill.

1. Find where the user is in the loop.

   - They want to start from scratch → narrow scope
   - They have a draft → evaluate it
   - They have results → revise the skill
   - They want to scale up → expand the test set
   - They have a finished skill → done (until a
     new test case fails)

2. For a new skill: narrow scope first.

   Ask:
     - What does the skill do in one sentence?
     - What is the LLM's job when this skill is
       triggered?
     - What does the LLM's output look like?
     - What does the LLM NOT do? (Anti-scope)
     - What does the user already know?

   A skill that tries to do everything does nothing.
   If you can't write a single sentence that fits in
   a tweet, the scope is too broad. Refine.

3. Draft the skill.

   The shape is:
     - YAML frontmatter (slug, name, description,
       inputs, output, source)
     - "When to use" — trigger conditions
     - "Inputs" — what the LLM needs
     - "Output" — what the LLM produces
     - "Prompt" — the step-by-step procedure
     - Optional: "When NOT to use", "Example"

   The most common drafting error is putting the
   "what" in the "When to use" instead of the
   "Prompt". "When to use" is the trigger
   condition, not the behaviour.

4. Write 5-10 test prompts.

   Each prompt should:
     - Be a realistic user request
     - Have a verifiable correct answer
       (or a class of correct answers)
     - Cover a different angle of the skill
     - Include both happy-path and edge cases
     - Include 1-2 "should NOT trigger" prompts
       to test description accuracy

   Do NOT start with 30 prompts. The first iteration
   is 5-10. A larger test set is an iteration of
   the loop, not the start.

5. Run the skill.

   The most common way:
     - Place SKILL.md where the LLM can read it
     - For each test prompt, run the LLM with the
       skill available
     - Capture the LLM's output
     - Record whether the LLM triggered the skill
       (description accuracy)

   Some harnesses offer a "skill observer" mode.
   Use it. The qualitative reading of the output
   is what catches the misses a metric would miss.

6. Evaluate.

   Qualitative:
     - Does the output match what the skill promised?
     - Does the LLM follow the Prompt steps?
     - Does the LLM produce the Output schema?
     - Where did the LLM improvise? Was the
       improvisation correct (good) or wrong (skill
       is missing)?

   Quantitative:
     - Trigger accuracy: out of N test prompts,
       how many should have triggered the skill
       and how many did?
     - Wrong trigger rate: how many prompts
       triggered the skill that should not have?
     - Output completeness: does the LLM's output
       contain the fields the skill promised?

   Use both. The metric catches regressions, the
   eyeball catches novel misses.

7. Iterate.

   - Edit the description if trigger accuracy is
     low. The description is what the LLM reads to
     decide whether to use the skill. Too broad:
     wrong trigger. Too narrow: missed trigger.
   - Edit the Prompt if output completeness is
     low. The Prompt is what the LLM reads to do
     the work. Add steps, add examples, add
     anti-patterns.
   - Edit the Inputs if the LLM is asking the
     user for things the skill should have
     defined.
   - Edit the Output if the LLM is producing
     things the skill did not define.

   Do NOT rewrite the whole skill on each
   iteration. Diff-driven edits: change one thing
   per pass, evaluate, change another.

8. Expand.

   When the skill is consistent at 5-10 prompts,
   scale to 30+:
     - Add edge cases (unusual input shapes)
     - Add adversarial prompts (where the skill is
       intentionally tempted to overreach)
     - Add prompts in different phrasings (test
       description triggering, not just keyword
       matching)
     - Add prompts that test "When NOT to use"

   Larger test sets catch regressions that a
   small one misses.

9. Repeat 5-8.

   Stop when:
     - trigger_accuracy >= target
     - wrong_trigger_rate < 5%
     - output_completeness >= target
     - the qualitative findings are diminishing
       (no more glaring misses)
```

# When NOT to use

- **You write the skill and ship it without running
  evals.** The loop is the skill. Shipping without
  evaluation is shipping a guess.
- **The description is too broad ("a general-purpose
  coding assistant").** It will trigger for every
  coding question. Tighten to a specific trigger
  condition.
- **The description is too narrow ("when the user
  asks about React 19 useActionState in Next 15
  with a Zustand store").** It will never trigger.
  Generalize the trigger, then add specifics in
  the Prompt.
- **The Prompt section is missing step-by-step
  procedure.** "Help the user with X" is not a
  Prompt. The Prompt is the procedure.
- **You rewrite the whole skill on each
  iteration.** Diff-driven edits: change one
  thing per pass, evaluate, change another. A
  full rewrite loses the learning from the
  previous pass.
- **You start with 30 test prompts.** The first
  iteration is 5-10. Scale up in later iterations.
- **You treat qualitative and quantitative as
  alternatives.** They are complementary. The
  metric catches regressions, the eyeball
  catches novel misses.
- **The skill is just a prompt-engineering
  collection.** That's a prompt library, not a
  skill. Skills are self-contained procedures
  with a trigger, inputs, and output schema.
- **You forgot the "When NOT to use" section.**
  The trigger condition has two sides: when to
  use, and when not to. Without the latter, the
  LLM has no negative example.
- **You declared done at 5 prompts.** Quality
  plateaus only after 20-30+ prompts and 3+
  iterations.

# Example

**Input (iterate stage):**

```yaml
stage: iterate
skill_path: skills/clickhouse-best-practices/SKILL.md
target_description_accuracy: 0.90
eval_method: both
```

**Output:**

```
Skill: skills/clickhouse-best-practices/SKILL.md

Qualitative findings (3):
  - description too broad; LLM triggers for any SQL
    question, not just ClickHouse
  - "When to use" is missing the "not just" clauses
    (rule fires for Postgres questions too)
  - "Prompt" section has the right structure but
    requires a lot of judgement from the LLM

Quantitative metrics:
  trigger_accuracy: 0.78 (target 0.90)
  output_completeness: 0.92
  wrong_trigger_rate: 0.18 (target < 0.05)

Proposed edits:
  1. Tighten description: "ClickHouse 28-rule review
     checklist. Use only for ClickHouse-specific
     questions (columnar, MergeTree, sparse index)."
  2. Add "When NOT to use" section listing Postgres,
     MySQL, DuckDB
  3. Convert step 4 in the Prompt section to a
     single decision question
```
