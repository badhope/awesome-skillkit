---
name: MCP Server Builder
name_zh: MCP Server 构建指南
description: 'You''re building an **MCP server** that lets an LLM call into some'
description_zh: '用 Python (FastMCP) 或 TypeScript (MCP SDK) 写一个高质量 MCP server。覆盖研究、schema 设计、工具实现、错误处理，以及新 server 上线前要带的 10 道评估题。'
category: mcp-protocol
tags:
  - ai
  - api
  - backend
  - cli
  - database
source: null
license: Complete terms in LICENSE.txt
author: 'Anthropic (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: mcp-builder
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

You're building an **MCP server** that lets an LLM call into some
external service — a third-party API, an internal database, a CLI
tool, anything with a stable interface that an agent should be able
to compose.

The bar is high: an MCP server is "good" only if a real LLM can
actually answer real questions by calling its tools. A server with
10 tools that all work, with clear names, with actionable error
messages, with a 10-question eval set you can run repeatedly, is
infinitely more useful than one with 50 tools that are half-broken.

The job is split into four phases:

1. **Research** — read the MCP spec, the relevant SDK README, the
   target service's API docs. Decide tool list and naming before
   writing code.
2. **Implementation** — scaffold the project, write a shared API
   client, then implement each tool with input + output schema,
   actionable errors, and the four annotations
   (`readOnlyHint` / `destructiveHint` / `idempotentHint` /
   `openWorldHint`).
3. **Build + test** — compile, smoke-test with the MCP Inspector,
   exercise read-only tools end to end.
4. **Evaluation** — author 10 independent, read-only, complex,
   realistic, verifiable, stable questions. Run them with the eval
   harness. A server that ships without this set is half-finished.

**Don't use this skill for** a thin wrapper around a CLI you've
already wrapped as a tool_use function — MCP is for cross-client
standardization, not for one-off wiring. And don't use it for
non-MCP tool integration in a single app (use whatever your
framework provides).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `target_service` | yes | The service the server wraps + a one-line purpose. |
| `language` | yes | `python` (FastMCP) or `typescript` (MCP SDK). |
| `transport` | yes | `streamable-http` (default) or `stdio`. |
| `deployment_target` | no | `mcpb` / `remote` / `local`. Decide after Phase 1 if unsure. |

If the user has not chosen a language, recommend TypeScript unless
they already have a Python FastMCP codebase or a hard Python
dependency. TypeScript has the better SDK, the broader AI code
fluency, and clean MCPB packaging.

# Output

Plain-text summary of what was created. Typical return:

```
Files created:
  src/server.ts            - server entry, tool registration
  src/api/client.ts        - shared HTTP client + auth
  src/tools/repos.ts       - github_list_repos, github_search_code
  src/tools/issues.ts      - github_create_issue, github_list_issues
  evals/questions.xml      - 10 read-only eval questions
  evals/run.ts             - eval runner

Tools: 9
  - github_list_repos (readOnly, idempotent, openWorld)
  - github_search_code (readOnly, idempotent, openWorld)
  - github_get_issue (readOnly, idempotent, openWorld)
  - github_list_issues (readOnly, idempotent, openWorld)
  - github_create_issue (destructive, idempotent=false)
  - github_update_issue (destructive, idempotent)
  - github_add_comment (destructive, idempotent=false)
  - github_list_prs (readOnly, idempotent, openWorld)
  - github_search_prs (readOnly, idempotent, openWorld)

Eval: 10/10 questions answered correctly by Claude Sonnet 4
Open questions:
  - pagination not yet implemented on github_list_issues
  - rate-limit backoff needs retry-after handling
```

# Prompt

```prompt
You are building an MCP server. Follow the four phases in order.
Do not skip research, do not skip eval.

Phase 1 — Research
==================

1.1 Read modern MCP design guidance. Three tradeoffs to balance:

  - API coverage vs workflow tools. Workflow tools (e.g.
    "summarize_issue_thread") are convenient for a specific task
    but lock in the server's opinions. Comprehensive endpoint
    coverage (e.g. github_list_repos, github_get_issue,
    github_list_issues) gives agents flexibility to compose.
    When uncertain, prefer comprehensive coverage. Some clients
    benefit from code execution that combines basic tools; others
    work better with higher-level workflows. Let the user choose
    based on the client they target.
  - Naming. Tool names should be `<service>_<verb>_<noun>`,
    lowercase, action-oriented. The prefix is the service name
    (e.g. `github_`, `stripe_`). Keep names stable across versions
    — agents are trained on them.
  - Context management. Tools should return focused, paginated
    results. Use field selection (e.g. `?fields=id,title,state`)
    where the API supports it. Never dump a 10-MB JSON blob.

1.2 Read the MCP specification.

  - Start at https://modelcontextprotocol.io/sitemap.xml to find
    the relevant pages.
  - Fetch specific pages with a `.md` suffix for markdown
    (e.g. https://modelcontextprotocol.io/specification/draft.md).
  - Key pages: specification overview, transport mechanisms
    (streamable HTTP, stdio), tool/resource/prompt definitions.

1.3 Load the SDK documentation for the chosen language.

  TypeScript (recommended):
    https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md
    Use WebFetch to load it. Look for the current tool-registration
    pattern (server.registerTool with Zod input schema,
    structuredContent in tool responses).

  Python:
    https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md
    Use WebFetch to load it. Look for FastMCP and the
    @mcp.tool decorator pattern.

1.4 Study the target service.

  - Find the official API documentation. Identify auth (OAuth
    bearer? API key? mTLS?).
  - List endpoints the agent needs. Start with read-only ones.
  - Identify rate limits, pagination style, and any quirks
    (cursor-based vs page-based, opaque vs numeric cursors).
  - Note the data model. The tools you write mirror the data
    model — get the entities right first.

Phase 2 — Implementation
========================

2.1 Scaffold the project.

  TypeScript:
    package.json with @modelcontextprotocol/sdk and zod
    tsconfig.json targeting ES2022
    src/server.ts as entry

  Python:
    pyproject.toml with mcp[cli] and pydantic
    src/<name>_server.py as entry

2.2 Write the shared infrastructure BEFORE any tool.

  - API client class (auth, base URL, request shape, error
    handling, retry on 429/5xx with exponential backoff)
  - Error formatter that turns HTTP errors into actionable
    messages ("rate limited; retry after 30s" not "error 429")
  - Response formatter (return both text content and
    structuredContent when the SDK supports it)
  - Pagination helper (wrap list endpoints in a `paginate`
    function that follows cursors)

2.3 For each tool:

  Input schema (TypeScript: Zod; Python: Pydantic):
    - Mark every field `description:` with a one-line purpose
    - Add `examples:` for ambiguous fields
    - Constrain to enums when the API is closed
    - Use `.optional()` / `default=` for optional fields

  Output schema:
    - Always define `outputSchema` when the result is structured
    - Use `structuredContent` in tool responses (TypeScript SDK
      feature) so clients can render the result without parsing
      text
    - For unstructured text, return a single `text` content item

  Tool description:
    - One sentence: what the tool does
    - Parameter descriptions (or rely on schema for that)
    - Return type info, plus any caveats (e.g. "paginates up
      to N items per page")

  Implementation:
    - async/await for I/O
    - Try/catch with actionable error messages
    - Pagination where the underlying API supports it
    - Return both text and structured data (TypeScript SDK)

  Annotations (all four, set explicitly):
    - readOnlyHint:      true for read-only endpoints
    - destructiveHint:   true for write/delete endpoints
    - idempotentHint:    true for PUT/DELETE-by-id; false for
                         POST that creates
    - openWorldHint:     true for external APIs; false for local
                         state the server owns

Phase 3 — Build and test
=========================

3.1 Quality review.

  - No duplicated code (shared helpers in src/api/client.ts)
  - Consistent error handling (single error formatter, not
    bespoke try/catch in every tool)
  - Full type coverage (no `any` in TypeScript; no missing
    Pydantic models in Python)
  - Tool descriptions are clear, one-sentence, action-oriented

3.2 Build.

  TypeScript:
    npm run build     # must succeed with zero TS errors
  Python:
    python -m py_compile src/<name>_server.py

3.3 Smoke-test with the MCP Inspector.

  npx @modelcontextprotocol/inspector

  - Connect to the local server (stdio or streamable HTTP)
  - List tools, confirm the names and descriptions are what
    the LLM will see
  - Call one read-only tool with a known input, confirm the
    response shape
  - Call one write tool against a test resource, confirm the
    destructiveHint annotation is set
  - Trigger an error path (bad auth, missing field, rate
    limit) and confirm the error message is actionable

Phase 4 — Evaluation
====================

4.1 Why this matters.

  An MCP server that passes MCP Inspector smoke tests can still
  be useless to an LLM — the tool names might be ambiguous, the
  descriptions might not convey the right intent, the pagination
  might force the LLM into 10 calls when 1 would do. Evaluation
  is the only way to catch that.

4.2 Author 10 evaluation questions.

  Each question must be:
    - Independent      — no chain of dependencies between
                          questions
    - Read-only        — only non-destructive tools required
    - Complex          — requires multiple tool calls and
                          deep exploration
    - Realistic        — based on a real use case a human
                          would care about
    - Verifiable       — has a single, clear answer that can
                          be checked by string comparison
    - Stable           — the answer won't change over time

  Process:
    a. List every tool the server exposes.
    b. Use the read-only tools to explore the data the
       questions will be about. Build intuition for what's
       actually answerable.
    c. Write 10 questions. Solve each one yourself with the
       tools to confirm the answer is what you think it is.
    d. Reject any question where the answer is "maybe",
       "depends", or requires non-deterministic external state.

4.3 Write the eval set as XML.

  <?xml version="1.0" encoding="UTF-8"?>
  <evaluation>
    <qa_pair>
      <question>...</question>
      <answer>...</answer>
    </qa_pair>
    <!-- 9 more qa_pairs -->
  </evaluation>

4.4 Run the eval with Claude (or your target model) against
    the local server. Score: 10/10 means the server is ready
    to ship. Anything less: fix the tool description, add a
    missing field to the schema, or split a confused tool into
    two.
```

# When NOT to use

- **The target is a single CLI tool** you've already wrapped
  once. MCP is for cross-client standardization; if the
  consumer is one specific app, use that app's native tool
  integration.
- **You don't know the target service's API yet.** Phase 1
  research is non-negotiable. A server with 50 guessed
  endpoints is worse than one with 5 verified ones.
- **You want a workflow tool that bakes in your opinions.**
  Default to comprehensive endpoint coverage. Workflow tools
  are nice-to-have on top, not a replacement.
- **The eval set is not feasible** (e.g. the target service
  is unstable or has no read-only paths). If you can't author
  10 read-only verifiable questions, the server is not ready
  for general release — narrow the scope or wait for
  stability.
- **You want to ship without `outputSchema` and
  `structuredContent`.** Modern SDKs support structured
  outputs. Use them. Agents render JSON much more reliably
  than they render text you ask them to parse.
- **The annotations are omitted.** Every tool needs all four
  hints set explicitly. Without `destructiveHint` clients
  can't warn users before dangerous calls; without
  `readOnlyHint` clients can't cache; without `idempotentHint`
  clients can't safely retry; without `openWorldHint` clients
  can't make authorization decisions.

# Example

**Input:**

```yaml
target_service: GitHub REST API
language: typescript
transport: streamable-http
deployment_target: mcpb
```

**Output:**

```
Files created:
  src/server.ts            - server entry, tool registration
  src/api/client.ts        - shared HTTP client + auth
  src/tools/repos.ts       - github_list_repos, github_search_repos
  src/tools/issues.ts      - github_get_issue, github_list_issues
  src/tools/contents.ts    - github_get_file_contents
  evals/questions.xml      - 10 read-only eval questions
  evals/run.ts             - eval runner
  package.json             - @modelcontextprotocol/sdk, zod
  tsconfig.json

Tools: 5 (all readOnly, all idempotent, all openWorld)
  - github_list_repos
  - github_search_repos
  - github_get_issue
  - github_list_issues
  - github_get_file_contents

Eval: 10/10 questions answered correctly.
Sample question:
  Q: "Find the issue titled 'OAuth callback fails on Safari'
      in the anthropics/skills repo. What is the issue number?"
  A: "84"

Open questions:
  - write tools (create_issue, add_comment) deferred — read-only
    path is enough for the first eval
  - rate-limit handling is conservative (1 retry, no
    retry-after parsing) — revisit when traffic picks up
```
