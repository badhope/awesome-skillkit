---
name: deepeval Pytest Eval Suite
name_zh: DeepEval 评估套件
description: Targeted fix to attempt next round
description_zh: 配置和运行 DeepEval 评估套件进行全面的 LLM 测试。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - evaluation
source: null
license: Apache-2.0
author: 'Confident AI (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: deepeval-eval-suite
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

You're adding a **repeatable eval loop** to an AI application
(LLM app, agent, RAG pipeline, chatbot). You want a committed
pytest suite — not a notebook or a throwaway script — that you
can re-run after every change, with metrics, a dataset, and
failure traces you can actually look at.

This is the **pytest + deepeval test run** path. It's separate
from `deepeval-tracing` (which is just the instrumentation) and
`deepeval-otel` (raw OpenTelemetry without the deepeval package).
You need the instrumentation done first if you want traced evals.

The job is: pick the right test shape (chatbot / agent / RAG /
single-turn), pick the right metrics for that shape, reuse the
dataset if it exists or generate one with `deepeval generate`,
run the suite with `deepeval test run`, and iterate on
failures for N rounds.

**Don't use this skill for** non-AI software or for ad-hoc
"is this prompt OK" checks. The pytest suite is the deliverable.
For one-off prompt grading, just run the metric in a notebook.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `use_case` | yes | Exactly one. Drives test shape. |
| `dataset_source` | yes | `existing` or `generate`. Never hand-roll. |
| `eval_model` | yes | The judge. Separate creds from the app's model. |
| `tracing` | yes | `true` when an integration exists. |
| `confident_ai` | yes | `true` when reports / dashboards are wanted. |
| `iteration_rounds` | yes | Default 5. Capped 10. |

# Output

Plain-text confirmation of what was created and the latest run
status. Typical return:

```
Created:
  tests/evals/test_single_turn_tracing.py
  tests/evals/metrics.py
  tests/evals/datasets/qa_v1.json
Latest run: 18/20 passing (90%), 2 failures
Top failure: Answer Relevancy on prompts asking for pricing
Next change: tighten system prompt to refuse off-topic
             pricing questions explicitly; rerun round 2/5
```

# Prompt

```prompt
You are building a pytest eval suite for an AI app with DeepEval.
Follow the steps in order. Do not skip the intake questions.

1. Inspect the codebase.
   Grep for framework imports, model calls, existing DeepEval
   metrics, and any committed dataset (look for `*.json` with
   `input` / `expected_output` keys in `tests/evals/datasets/`
   or `data/evals/`). If DeepEval is already in use, KEEP its
   existing metrics and thresholds unless the user explicitly
   asks to change them.

2. Ask the intake questions before writing any test code:
   - Which use case: chatbot, multi-turn agent, agent, RAG, or
     single-turn LLM? (Pick exactly one; precedence is
     chatbot / multi-turn-agent > agent > rag.)
   - Dataset: does the user already have a committed dataset, or
     should we run `deepeval generate`?
   - Eval model: which model is the judge / scorer? (Separate
     from the app's own model.)
   - Tracing: should each test case capture a trace? (Default
     `true` when a supported integration exists.)
   - Confident AI: should results push to Confident AI for
     hosted reports? (Requires `CONFIDENT_API_KEY` or `deepeval
     login`.)
   - Iteration rounds: how many failure → fix → rerun cycles?
     (Default 5. Cap 10.)

3. Choose the test shape. The skill uses these templates:
     - chatbot / multi-turn agent  → `templates/test_multi_turn_e2e.py`
     - agent / RAG / single-turn, tracing available
                                    → `templates/test_single_turn_tracing.py`
     - single-turn, no tracing
                                    → `templates/test_single_turn_no_tracing.py`
   Do not write a single-turn test when the use case is multi-turn.
   Do not skip tracing when an integration is available.

4. Choose metrics. Put metric instances in a separate
   `tests/evals/metrics.py` module — NOT inline in the test
   file. Reuse the project's existing metrics module if there
   is one. Pick from:
     - General: Answer Relevancy, Faithfulness, Hallucination
     - RAG: Contextual Precision / Recall / Relevancy
     - Agent: Tool Correctness, Task Completion, Plan Quality
     - Chatbot: Knowledge Retention, Role Adherence, Conversation Completeness

5. Prepare the dataset.
     - If `dataset_source = existing`, read the existing
       `*.json` and reuse it. Do not regenerate.
     - If `dataset_source = generate`, run `deepeval generate`
       with the target model and the chosen source corpus.
       Do not hand-write goldens.

6. If `tracing = true` AND no deepeval-tracing has been done,
   STOP and tell the user to run the deepeval-tracing skill
   first. Traced evals need the app instrumented.

7. Run the suite.
     - Use `deepeval test run tests/evals/` — NOT bare `pytest`.
       `deepeval test run` is what wires the metrics, the
       dataset, and the (optional) Confident AI push.
     - Capture pass rate and per-test failures.
     - If `confident_ai = true`, the report link is the next
       step for the user; surface it.

8. Iterate for `iteration_rounds` rounds (default 5).
   For each round:
     a. Read the failure details + (if `tracing`) the trace.
     b. Pick the SINGLE highest-leverage change — a system prompt
        tweak, a retrieval re-rank, a tool signature fix.
     c. Apply it. Don't bundle multiple changes in one round.
     d. Rerun. If pass rate drops, revert that round and pick a
        different change.
   Stop when pass rate plateaus, target metric thresholds are
   met, or rounds are exhausted.

9. Final report: test files created, metric module, dataset path,
   final pass rate, and a one-line summary of what changed
   across rounds.
```

# When NOT to use

- **The target is not an AI app.** DeepEval metrics describe
  LLM / agent behaviour. Running them on a regular CRUD app
  is meaningless.
- **You want to instrument the app, not build a test suite.**
  Use `deepeval-tracing` first. This skill assumes that step
  is done (when `tracing = true`).
- **You want to define metrics inline in the test file.** Metric
  instances belong in a separate `metrics.py` module so multiple
  test files can import them. This is a hard rule, not taste.
- **The user wants a one-off prompt grading.** Use a notebook
  or the `deepeval` CLI directly. A pytest suite is overkill
  for a single check.
- **You can't decide between tracing and no-tracing without
  user input.** Default to `tracing = true` when a supported
  integration exists; ask otherwise.
- **You have access to PII or secrets in the eval corpus.** The
  dataset is uploaded to Confident AI if `confident_ai = true`.
  Redact before committing.

# Example

**Input:**

```yaml
use_case: agent
dataset_source: generate
eval_model: gpt-4.1
tracing: true
confident_ai: true
iteration_rounds: 3
```

**Output:**

```
Created:
  tests/evals/test_single_turn_tracing.py
  tests/evals/metrics.py
  tests/evals/datasets/agent_v1.json
Run 1/3: 12/15 (80%); failures: Tool Correctness on 'search_orders'
Change: tighten tool signature to require `order_id: str`; rerun
Run 2/3: 14/15 (93%); failure: Task Completion on 'refund_request'
Change: add explicit refund-policy tool to agent prompt; rerun
Run 3/3: 15/15 (100%)
Report: https://app.confident-ai.com/evals/runs/abc123
```
