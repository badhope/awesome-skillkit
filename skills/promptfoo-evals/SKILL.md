---
name: promptfoo Eval Suite Author
name_zh: Promptfoo 评估
description: Confirmation of the suite path, the assertion mix, and the
description_zh: 使用 Promptfoo 运行和评估 prompt 的性能。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - deployment
source:
ref: main
license: MIT
language: en
author: 'Promptfoo (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: promptfoo-evals
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

You're putting **eval coverage** on something LLM-driven — a
prompt template, an HTTP endpoint, an agent, a RAG pipeline, a
chatbot, or a code-generation prompt. You want a maintainable
`promptfoo` suite: a YAML config, prompt files, test cases, and
assertions. The suite lives in the repo and is re-runnable on
every change, locally and in CI.

This is the **regression / matrix / coverage** skill for
promptfoo. It's separate from `promptfoo-redteam` (adversarial
attacks). The two share a config file format but serve different
purposes: this one measures "does it still work?"; redteam
measures "can I break it?".

The job is: pick the simplest provider pattern that matches the
real system, write deterministic assertions first, fall back to
model-graded only where the output is qualitative, and keep
provider count low. Resist the urge to test five models at once.

**Don't use this skill for** adversarial testing (use
`promptfoo-redteam`), or for non-LLM software (pytest / jest is
the right tool — no need for promptfoo).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `target` | yes | Drives provider pattern choice. |
| `suite_layout` | no | Default `evals/<suite-name>/`. Reuse repo convention. |
| `provider_count` | yes | 1 for regression, 2 for comparison. Cap 3. |
| `assertion_style` | yes | `mixed` is the safe default. |
| `dataset` | no | `inline` for small suites, `csv` / `jsonl` for big. |

# Output

Plain-text confirmation. The system of record is promptfoo's
own CLI output. Typical return:

```
Suite: evals/customer-support/
Prompts: 3, Tests: 28, Pass rate: 24/28 (86%)
Failing assertions:
  - contains('Order ID:')  × 2 cases (output cuts off)
  - is-json  × 1 case (trailing whitespace)
  - llm-rubric  × 1 case (judge flagged missing apology)
```

# Prompt

```prompt
You are writing a promptfoo eval suite. Follow the steps in order.

1. Find or create the suite.
   Grep for existing `promptfooconfig.yaml`, `promptfooconfig.yml`,
   or any `evals/` / `promptfoo/` directory. If one exists and
   the layout matches the repo's convention, EXTEND it — don't
   make a parallel suite.
   For a new suite, default to:
       evals/<suite-name>/
         promptfooconfig.yaml
         prompts/
         tests/
   Always start the config with:
       # yaml-language-server: $schema=https://promptfoo.dev/config-schema.json

2. Write prompts.
   Put each prompt in its own file under `prompts/`. Plain text
   prompts use `prompts/<name>.txt`; chat-format prompts use
   `prompts/<name>.json` with `[{role, content}, ...]`.
   Reference from config: `file://prompts/<name>.txt` or
   `file://prompts/<name>.json`.
   Use `{{variable}}` for test-time inputs.
   If the app builds prompts dynamically (e.g. a chat template
   in Python), use a JS/Python provider instead of duplicating
   the logic in a static prompt file.

3. Choose providers.
   Pick the simplest pattern that matches the real system:

     Compare models  → `openai:chat:gpt-4.1-mini`,
                       `anthropic:messages:claude-sonnet-4-6`
     Test an HTTP API → `id: https` with `config.url`,
                         `config.body`, `transformResponse`
     Test local code → `file://provider.py` or
                       `file://provider.js`
     Echo / passthrough → `id: echo` (returns prompt as-is;
                        useful for assertion-only tests)

   For JSON output, add `response_format`:
       config:
         temperature: 0
         response_format:
           type: json_object

   Keep `provider_count` low: 1 for regression, 2 for comparison,
   3 max. More dilutes the signal.

4. Write tests.
   Prefer file-based tests so they scale:
       tests: file://tests/*.yaml
   For large / importable suites, use a dataset:
       tests: file://tests.csv
       tests: file://generate_tests.py:create_tests
   Every test case has:
     - `description` — short, specific
     - `vars` — the inputs
     - `assert` — validations
   Cover: happy paths, edge cases (empty, very long, unicode),
   known regressions, safety / refusal, output format
   compliance.

5. Add assertions.
   **Deterministic first** — fast, reliable, free:
     `equals`, `contains`, `icontains`, `regex`, `is-json`,
     `contains-json`, `starts-with`, `ends-with`,
     `is-valid-openai-tools-call`, `python` (custom assertion),
     `javascript` (custom assertion).
   **Model-graded only where needed**:
     `llm-rubric` (judge on a custom rubric),
     `g-eval` (G-Eval chain-of-thought),
     `answer-relevance`, `factuality`, `moderation`,
     `select-best` (compare across providers).
   Don't model-grade what you can regex-check. JSON shape
   verification belongs in `is-json` or `contains-json`, not in
   `llm-rubric`.

6. Run the suite.
     promptfoo eval -c evals/<suite-name>/promptfooconfig.yaml
   Capture pass rate and per-assertion failure breakdown.

7. CI gate (optional but recommended).
   Use `promptfoo eval --fail-on=...` in CI to block merges on
   regression. For matrix runs, use `--output results.json` to
   feed dashboards.
```

# When NOT to use

- **The target is non-LLM software** (CRUD API, image pipeline,
  data transformation). Use pytest / jest / go test. Promptfoo
  exists to evaluate LLM-driven output, not to test
  deterministic code.
- **You want adversarial / redteam testing.** Use the
  `promptfoo-redteam` skill. This one measures
  "does it still work?"; redteam measures "can I break it?"
- **You have a static prompt and need a one-off judgment.** A
  pytest suite with one model call is simpler. The promptfoo
  suite is worth it when you have ≥5 test cases or you'll
  re-run it.
- **You want to test that two models produce the same output.**
  Use `select-best` (one assertion) or just diff the outputs in
  a script. Building a whole promptfoo suite for a single
  comparison is overkill.
- **You have 50+ providers to compare.** Promptfoo's value
  fades past 3-4 providers. The output becomes hard to read
  and per-provider analysis gets noisy. Pick a subset, or
  write a custom comparison script.
- **You want to deploy the eval as a service.** Promptfoo is a
  CLI tool. For hosted eval-as-a-service, use Braintrust,
  Langfuse, or DeepEval.

# Example

**Input:**

```yaml
target: endpoint
suite_layout: evals/customer-support/
provider_count: 2
assertion_style: mixed
dataset: inline
```

**Output:**

```
Suite: evals/customer-support/
  promptfooconfig.yaml
  prompts/system.txt
  prompts/fewshot.txt
  tests/refunds.yaml
  tests/edge-cases.yaml
Prompts: 2, Tests: 28, Pass rate: 24/28 (86%)
Failing assertions:
  - contains('Order ID:')        × 2 cases (output cuts off)
  - is-json                      × 1 case (trailing whitespace)
  - llm-rubric: 'contains apology' × 1 case

Next: tighten the system prompt to require "Order ID:" prefix
      on refund responses; add is-json trim transform.
```
