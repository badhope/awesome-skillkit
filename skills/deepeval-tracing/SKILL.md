---
slug: deepeval-tracing
name: deepeval SDK Tracing
name_zh: deepeval SDK 打点
version: 0.1.0
description: Instrument a Python AI app with DeepEval's `@observe` decorator and framework integrations so traces land in Confident AI's Observatory. The Python-only counterpart to the OTel-based deepeval-otel skill.
description_zh: 用 DeepEval 的 `@observe` 装饰器和框架集成给 Python AI 应用打点，让 trace 进 Confident AI 的 Observatory。Python-only，跟 OTel 路径（deepeval-otel）互补。

category: observability
tags: [deepeval, tracing, observe, python, integrations]
platforms: []

inputs:
  - name: framework
    type: string
    required: true
    description: |
      AI framework / SDK in use. Pick from: langgraph, langchain,
      openai-agents, llamaindex, pydantic-ai, crewai, autogen,
      haystack, semantickernel, vertex, bedrock — or `custom` if
      none of these match. `custom` triggers manual `@observe`
      instead of a native integration.
  - name: model_provider
    type: string
    required: true
    description: |
      LLM provider actually called by the app: openai, anthropic,
      google, bedrock, azure, cohere, mistral, ollama, vllm. The
      deepeval integration may patch the provider's SDK to
      auto-capture input/output tokens.
  - name: vector_db
    type: string
    required: false
    description: |
      Vector store in use, if any. Supported: pinecone, qdrant,
      weaviate, chroma, milvus, pgvector. Empty = no retrieval
      component.
  - name: confident_api_key
    type: string
    required: true
    description: |
      `CONFIDENT_API_KEY` from Confident AI. Or run `deepeval
      login` once per machine, which writes the key to
      `~/.deepeval/`. CI must export the env var.

output:
  format: text
  description: |
    Confirmation that traces are arriving in Confident AI's
    Observatory. No structured payload — Confident AI is the
    system of record. Typical return is a trace URL and a list of
    detected span types.
  schema:
    type: object
    properties:
      trace_url: { type: string }
      detected_spans: { type: array, items: { type: string } }
      instrumented_files: { type: array, items: { type: string } }

author: "Confident AI (downstream pack: badhope)"
license: Apache-2.0
source:
  url: https://github.com/confident-ai/deepeval/tree/main/skills/deepeval-tracing
  ref: main
  commit: latest
created: 2026-06-10
updated: 2026-06-10
---

# When to use

You're instrumenting a **Python AI app** (LLM app, agent, RAG
pipeline, chatbot) and you want its execution to show up span by
span in **Confident AI's Observatory** so you can later attach
metrics and iterate. You're OK installing the `deepeval` Python
package and using its SDK conventions (`@observe`, framework
integrations).

This is the **Python + deepeval SDK** path. If you want a
language-agnostic setup or you don't want to install deepeval
itself, use the `deepeval-otel` skill (raw OpenTelemetry) instead.
If you want to define metrics and run pytest eval suites, use the
`deepeval-eval-suite` skill.

The job is exactly three things: pick a supported integration
when one exists, fall back to manual `@observe` otherwise, and
give every span a meaningful type (`llm` / `retriever` / `tool`
/ `agent`). The skill stops at producing well-formed traces —
attaching metrics and running evals is the eval-suite skill's job.

**Don't use this skill for** non-AI software. The span types
describe AI components, and the Observatory renders AI behaviour.
Tracing a Postgres query or a Flask handler is meaningless.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `framework` | yes | Drives integration choice. `custom` = manual `@observe`. |
| `model_provider` | yes | Patched automatically by the matching integration. |
| `vector_db` | no | Empty = no retriever spans needed. |
| `confident_api_key` | yes | Or `deepeval login` for interactive setup. |

`framework` examples: `langgraph` uses `deepeval.integrations.langgraph`
patching, `crewai` uses `deepeval.integrations.crewai`, etc. If the
project mixes two frameworks (e.g. LangChain inside a CrewAI flow),
list both — integrations stack cleanly.

# Output

Plain-text confirmation. The system of record is Confident AI's
Observatory; this skill just wires the SDK. Typical return:

```
Trace landed: https://app.confident-ai.com/observability/traces/d41f3a
Detected spans: llm=8, agent=3, retriever=2, tool=1
Instrumented: src/agents/customer_support.py:42 (@observe)
              src/agents/customer_support.py:87 (@observe type=llm)
```

# Prompt

```prompt
You are wiring DeepEval tracing into a Python AI application. Follow
the steps in order. Do not skip ahead.

1. Confirm the target is an AI app.
   It must have at least one of: LLM calls, an agent loop, retrieval
   / vector search, or tool calls. If none are present, STOP — this
   skill does not apply. Tell the user that DeepEval's span types
   describe AI components and Confident AI's Observatory is built
   to evaluate AI behaviour.

2. Detect what's in the codebase.
   Grep for imports / framework signatures. Identify:
     - AI framework (langgraph, langchain, openai-agents,
       llamaindex, pydantic-ai, crewai, autogen, haystack, semantickernel)
     - LLM provider (openai, anthropic, google, bedrock, azure, cohere,
       mistral, ollama, vllm)
     - Vector store (pinecone, qdrant, weaviate, chroma, milvus, pgvector)
   If you can't detect any AI framework, mark `framework = custom` —
   that triggers manual `@observe` below.

3. Read the exact integration doc for the detected framework +
   provider. The docs/SDK are the source of truth for which functions
   to patch and which auto-captures are enabled. Do not guess based
   on framework name alone.

4. If a native integration fits, use it. Add the patch call to the
   app's startup (or test fixture for pytest). Skip the manual
   `@observe` step for code paths the integration auto-traces.
   If no native integration fits (`framework = custom` or you have
   app-owned wrapper boundaries that the integration can't see),
   proceed to manual `@observe`.

5. Manual `@observe` rules:
   - Decorate the top-level agent / chain / pipeline function.
   - Decorate every LLM call with `@observe(type="llm")`.
   - Decorate every retrieval call with `@observe(type="retriever")`.
   - Decorate every tool call with `@observe(type="tool")`.
   - Let span names default to the function name. Override only when
     the function name is too generic (e.g. `def call`).
   - Capture inputs and outputs in span metadata when they help
     diagnose failures. NEVER include raw user PII, secrets, or
     credentials.

6. Trace-level tags and metadata (optional but recommended for
   production):
   - `session_id` (link traces into a session / conversation)
   - `user_id` (the end user, if known and allowed)
   - `environment` (dev / staging / prod)
   - `git_sha` (the deployed commit)

7. Confirm the API key is reachable. Either:
     - `deepeval login` was run once and the key is in
       `~/.deepeval/`, OR
     - `CONFIDENT_API_KEY` is exported in the environment.
   CI must export the env var. Bare `deepeval login` doesn't work
   in CI.

8. Run the app, trigger one trace, and verify it shows up in
   Confident AI's Observatory. If it doesn't:
     - check the deepeval logs for auth errors
     - verify `@observe` decorators are actually imported and
       called
     - check whether the framework's integration has been
       initialised (most need an explicit `patch_*()` call)
```

# When NOT to use

- **The app is not in Python** (or you don't want to install
  `deepeval`). Use the `deepeval-otel` skill — it's the
  language-agnostic OTLP path and works without the deepeval package.
- **You want to define metrics and run pytest eval suites.** This
  skill stops at producing well-formed traces. Use
  `deepeval-eval-suite`.
- **The target is non-AI software** (web server, CRUD API, queue
  consumer, cron). DeepEval span types describe AI components.
  Tracing a Flask request handler produces empty / meaningless spans.
- **You want the cheapest possible tracing and don't care about
  Confident AI.** Use OpenTelemetry's SDK directly with a console or
  OTLP exporter and skip this whole skill.
- **You have PII / secrets to capture in span attributes.** DeepEval
  forwards everything to Confident AI unredacted. Redact before
  decorating.

# Example

**Input:**

```yaml
framework: langgraph
model_provider: openai
vector_db: qdrant
confident_api_key: us-cf_***
```

**Output:**

```
Trace landed: https://app.confident-ai.com/observability/traces/d41f3a
Detected spans: llm=8, agent=3, retriever=2, tool=1
Instrumented:
  src/agents/customer_support.py:42  @observe
  src/agents/customer_support.py:87  @observe(type="llm")
  src/agents/customer_support.py:120 @observe(type="retriever")
  src/agents/customer_support.py:151 @observe(type="tool")
Next: run the eval-suite skill to attach metrics.
```
