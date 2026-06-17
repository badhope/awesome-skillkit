---
name: datadog-query-recipes
name_zh:
description: 'Langfuse-specific Datadog query recipes for production telemetry research.'
description_zh:
category: observability
tags:
  - ai
  - api
  - backend
  - cli
  - datadog
source:
license: UNKNOWN
author: unknown
version: '0.1.0'
needs_review: false
slug: datadog-query-recipes
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

Use this skill when you need guidance on datadog query recipes.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Datadog Query Recipes

Use this skill for Langfuse production telemetry research where the main work is
finding the right Datadog data path. Keep findings evidence-based and include
the exact Datadog links or query shapes that support the answer.

## Required Scope

Unless the user explicitly narrows the scope, cover every production
environment:

- `prod-us`
- `prod-eu`
- `prod-hipaa`
- `prod-jp`

Query both Datadog sites when needed. Default to the EU site for `prod-eu` and
the US site for the other prod environments, but verify with a small count or
facet query before concluding an environment has no data.

Before querying live Datadog, load the relevant Datadog MCP guidance for the
data domain you need: traces, logs, metrics, and visualizations.

## Workflow

1. Identify the entity and signal: tenant ID, org ID, project ID, route, queue,
   service, error class, or metric.
2. Read only the relevant reference:
   - Prod environment/site routing:
     [`references/environments.md`](references/environments.md)
   - Public API tenant or legacy endpoint usage:
     [`references/public-api-tenant-usage.md`](references/public-api-tenant-usage.md)
   - Queue inventory, queue consumers, and queue metrics:
     [`references/queue-consumers.md`](references/queue-consumers.md)
3. Start with aggregate queries, grouped by environment, service, route,
   queue, project, org, status, or error facets as appropriate.
4. Fetch raw spans, logs, or traces only after aggregation identifies the
   cluster or sample you need.
5. For tenant-specific HTTP usage, prefer trace correlation over single-span
   queries when tenant tags and route tags live on different spans.
6. Report the windows, environments, sites, query links, and any sampling or
   missing-data caveats.

## When To Use Other Skills

- Use [`debug-issue-with-datadog`](../debug-issue-with-datadog/SKILL.md) when a
  Linear issue, GitHub issue, incident report, or monitor needs root-cause
  analysis and patch recommendations.
- Use [`weekly-production-review`](../weekly-production-review/SKILL.md) when
  the user asks for a weekly engineering overview of production bugs, pages,
  and incidents.
- Use [`linear-bug-triage`](../linear-bug-triage/SKILL.md) only after a human
  approves sharing measured findings in Linear.

## Output Expectations

Summarize what was checked, including:

- Datadog site and `env` values covered.
- Time windows.
- Core filters or metrics used.
- Count, rate, latency, queue depth, trace sample, or "No measurements found".
- Datadog links or trace IDs that let the human rerun the query.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

```python
# 查询API使用率（按租户分组）
query = """
@langfuse.project.id:* service:web-api
| stats count() by @langfuse.project.id, status
| filter status >= 400
"""

# 执行查询
from datadog_client import query_spans

results = query_spans(
    query=query,
    time_range="24h",
    environments=["prod-us", "prod-eu"]
)

# 按环境分组统计
for env in ["prod-us", "prod-eu"]:
    env_data = results.filter(env=env)
    print(f"{env}: {len(env_data)} errors")
    for project_id, count in env_data.group_by("project_id"):
        print(f"  Project {project_id}: {count} errors")
```

