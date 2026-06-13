---
name: analyze-cloud-costs
name_zh: 分析云成本
description: Analyze Langfuse Cloud infrastructure cost structure using Metabase
description_zh: 分析和优化云服务的成本，识别浪费和优化机会。
category: dev-tools
tags:
  - ai
  - cli
  - frontend
  - javascript
  - llm
source: null
license: UNKNOWN
author: unknown
version: '0.1.0'
needs_review: false
slug: analyze-cloud-costs
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

Use this skill when you need guidance on analyze cloud costs.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Analyze Cloud Costs

## Overview

Use this skill for evidence-backed Langfuse Cloud cost analysis. The primary
source is the Metabase infra cost dashboard and its production cost marts; the
deliverable should name the time window, query grain, top drivers, and caveats.

## Workflow

1. Clarify the question and choose the grain:
   - Headline daily totals: total, AWS, ClickHouse, tracing events, and cost per
     100k events.
   - Cost structure: provider, service, usage type, operation, account, and day.
   - Driver or regression analysis: compare a recent complete-day window against
     a prior baseline.
2. Load [`references/cost-marts.md`](references/cost-marts.md) for table IDs,
   field IDs, query examples, and caveats.
3. Use the Metabase MCP. If the Metabase tools are not visible, discover them
   with tool search before falling back to manual interpretation.
4. Prefer complete UTC days. Avoid treating current-day AWS cost as final
   because AWS CUR rows can arrive late.
5. Start broad, then drill down:
   - Provider split.
   - Service split within the dominant provider.
   - Usage type, operation, and account split for the top services.
   - Daily trend when explaining change over time.
6. Report only what the queried data supports. If a requested slice is absent,
   say that no rows were found for that slice instead of inventing a driver.

## Query Rules

- Use `mcp__metabase__.query` for quick reads. Use
  `construct_query` plus `execute_query` when you need to inspect or reuse the
  opaque query.
- Pass `filters`, `aggregations`, `group_by`, and `fields` as JSON arrays. Some
  tool schemas may display these as strings; if that happens, serialize the same
  arrays without changing their shape.
- Keep limits explicit and small enough for analysis. Use pagination only when
  the continuation token is needed.
- Include the Metabase dashboard link or query result context in the final
  answer when useful.

## Output Expectations

Summarize:

- Time window and whether it uses complete UTC days.
- Total cost and provider split when relevant.
- Top cost drivers by service, usage type, operation, or account.
- Trend or baseline comparison when the user asks "why did this change?"
- Caveats, especially incomplete current-day AWS data and ClickHouse credit
  labeling in the unified mart.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.


```python
# 使用 analyze-cloud-costs 进行监控
from monitor import Monitor, Metric

# 初始化监控器
monitor = Monitor(
    skill="analyze-cloud-costs",
    metrics=["response_time", "error_rate", "throughput"]
)

# 收集指标
metrics = monitor.collect(duration="5m")

# 分析指标
analysis = monitor.analyze(metrics)
print(f"Average response time: {analysis.avg_response_time}ms")
print(f"Error rate: {analysis.error_rate}%")
```
