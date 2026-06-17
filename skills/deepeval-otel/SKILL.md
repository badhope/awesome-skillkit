---
name: deepeval OTel Trace Export
name_zh: DeepEval OpenTelemetry
description: Suggested follow-up actions
description_zh: 使用 OpenTelemetry 集成 DeepEval 进行 LLM 应用的可观测性。
category: observability
tags:
  - ai
  - api
  - backend
  - cli
  - database
source: null
license: Apache-2.0
author: 'Confident AI (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: deepeval-otel
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

You're instrumenting an **AI application** — an LLM app, an agent,
a RAG pipeline, a chatbot — and you want its traces to land in
**Confident AI's Observatory** so you can evaluate, monitor, and
debug. You don't want to install the `deepeval` Python package; you
just want to point an OpenTelemetry exporter at the right place and
set the right attributes.

The mechanism is OpenTelemetry standard: any OTLP-capable SDK, any
language, the same `confident.*` attribute keys. Confident AI's
exporter reads those attributes off each span and assembles the
trace structure. Parent/child nesting is native OpenTelemetry span
context — nothing deepeval-specific.

**Use this skill when** you already have an OTel SDK in the project
and just need to repoint the exporter. Or when you're starting from
zero and want a minimal vendor-neutral setup that doesn't lock you
in to a Python-only framework.

**Don't use this skill for** non-AI software (web servers, CRUD
backends, infrastructure). The `confident.*` attributes describe
AI components (agent, llm, retriever, tool) and the Observatory is
built to render AI behaviour — putting non-AI spans in there is
waste of bandwidth and confusing to read.

For the deepeval SDK's native `@observe` decorator and framework
integrations (LangGraph, LangChain, etc.), use the
`deepeval-tracing` skill instead. For pytest-style eval suites and
metric definitions, use the `deepeval-eval-suite` skill.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `otel_endpoint` | yes | Pick region from API key prefix. US vs EU only. |
| `confident_api_key` | yes | Header value, never URL query. |
| `ai_components` | yes | Subset of `agent / llm / retriever / tool`. |
| `app_language` | yes | Determines which OTel SDK to install. |

`app_language` examples: `python` (use `opentelemetry-sdk` +
`opentelemetry-exporter-otlp-proto-http`), `typescript`
(`@opentelemetry/sdk-node` + `@opentelemetry/exporter-trace-otlp-http`),
`go` (`go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp`).

# Output

Plain-text confirmation. No JSON envelope, no schema enforcement.
The system of record is Confident AI's Observatory; this skill
just wires the export. Typical return:

```
Trace landed: https://app.confident-ai.com/observability/traces/abc123
Spans by type: llm=12, agent=4, retriever=3, tool=2
Next: review the trace timeline in the Observatory, attach a
      dataset, then create a metric to score the runs.
```

# Prompt

```prompt
You are wiring an AI application's OpenTelemetry export to Confident
AI. Follow the steps in order. Do not skip ahead.

1. Confirm the target is an AI app.
   It must have at least one of: LLM calls, an agent loop,
   retrieval / vector search, or tool calls. If none of these
   are present, STOP — this skill does not apply. Tell the user
   that `confident.*` attributes only describe AI components and
   Confident AI's Observatory is built to evaluate AI behaviour.

2. Inspect for existing OTel setup.
   Look for an existing `TracerProvider`, span exporters, an
   OpenTelemetry Collector, or an APM auto-instrumentation agent
   (Datadog, New Relic, etc.). If one exists, prefer repointing
   it to the Confident AI endpoint over adding a parallel
   pipeline.

3. Pick the OTLP/HTTP endpoint.
   Read the user's `CONFIDENT_API_KEY`. The key prefix tells
   you the region:
     - US key (starts with `us-`) → https://otel.confident-ai.com
     - EU key (starts with `eu-`) → https://otel.eu.confident-ai.com
   If the key has no clear prefix, ask the user which region
   they provisioned in. Do NOT guess.

4. Wire an OTLP/HTTP span exporter with the
   `x-confident-api-key` header set to the key value.
   For Python, start from a minimal exporter setup; for other
   languages, use the equivalent OTel SDK + HTTP exporter.
   NEVER use OTLP/gRPC — Confident AI's endpoint accepts HTTP
   only.

5. Isolate the export if the process has other OTel
   instrumentation. A web server emitting HTTP request spans, a
   database driver emitting query spans, or an APM agent
   exporting everything will pollute Confident AI with
   non-AI data. Set up either:
     - a dedicated `TracerProvider` only for AI spans, OR
     - a span filter that drops non-AI spans before they reach
       the Confident AI exporter.
   The `confident.*` attributes and span types
   (`agent / llm / retriever / tool`) describe AI components.
   Non-AI spans have no place in the Observatory.

6. Set `confident.span.*` attributes on each AI span.
   Required minimum:
     - `confident.span.type` = one of `agent / llm / retriever / tool`
   Recommended for `llm` spans:
     - `confident.span.model` (model id as the provider reports it)
     - `confident.span.input` / `confident.span.output` (the
       actual prompt and response, redacted)
   Use OTLP data-type rules: attribute values are primitives or
   homogeneous primitive lists. JSON-encode dicts and nested
   metadata as strings.

7. Set `confident.trace.*` attributes for trace-wide fields:
     - `confident.trace.name` (human-readable trace label)
     - `confident.trace.session_id` (links traces into a session)
     - `confident.trace.user_id` (the end user, if you have it)

8. If the app already emits OTel GenAI semantic conventions
   (`gen_ai.*` attributes), do NOT add redundant `confident.*`
   attributes. Confident AI's exporter reads the gen_ai
   conventions as a fallback.

9. Run the app, generate one trace, and confirm the span appears
   in Confident AI's Observatory. If it doesn't:
     - check the exporter's error log for HTTP 401/403
     - verify the endpoint matches the key region
     - check whether the spans have `confident.span.type` set
```

# When NOT to use

- **The target is non-AI software** (web server, CRUD API, queue
  consumer, cron). `confident.*` attributes describe AI components
  only. Setting them on a Postgres query span or an HTTP request
  span is meaningless and clutters the Observatory.
- **You need the deepeval SDK's `@observe` decorator** to mark
  functions. This skill is for raw OTLP, not the deepeval Python
  package. Use the `deepeval-tracing` skill instead.
- **You want to define metrics and run pytest eval suites.** This
  skill only handles trace export. Use the
  `deepeval-eval-suite` skill.
- **You must use gRPC** for trace export. Confident AI's endpoint
  accepts HTTP only. There is no fallback.
- **You want span → trace rollup computed client-side.** Confident
  AI does the rollup from the attributes. Don't double-count by
  setting `trace.id` or `parent_span` manually.
- **You have credentials or PII to put in span attributes.** Span
  attributes are not encrypted at rest on Confident AI's side.
  Redact before setting.

# Example

**Input:**

```yaml
otel_endpoint: https://otel.confident-ai.com
confident_api_key: us-cf_***     # region prefix is `us-`
ai_components: [llm, agent]
app_language: python
```

**Output:**

```
Trace landed: https://app.confident-ai.com/observability/traces/8f3a2c
Spans by type: llm=12, agent=4
Next:
  - Open the trace timeline in the Observatory
  - Create a metric (e.g. Answer Relevancy) and attach this trace
  - Link future traces in this session via session_id
```
