---
name: microcopy
name_zh: microcopy
description: 'UI copy and microcopy guidelines. Use for user-facing copy, buttons,'
description_zh: 'UI copy and microcopy guidelines. Use for 用户-facing copy, buttons,'
category: documentation
tags:
  - ai
  - api
  - evaluation
  - frontend
  - llm
source: null
needs_review: false
slug: microcopy
version: '1.0.0'
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
author: AI-SKILL
license: MIT
---
# When to use

Use this skill when you need to work with microcopy.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# LobeHub UI Microcopy Guidelines

This file is the quick-reference summary. For full prompt-style guidelines with extensive examples (anti-patterns, tone matrices, scenario walk-throughs), load the language-specific reference:

- **中文文案** — [`references/zh.md`](./references/zh.md)
- **English copy** — [`references/en.md`](./references/en.md)

Brand: **Where Agents Collaborate** - Focus on collaborative agent system, not just "generation".

## Fixed Terminology

| Chinese    | English       |
| ---------- | ------------- |
| 空间       | Workspace     |
| 助理       | Agent         |
| 群组       | Group         |
| 上下文     | Context       |
| 记忆       | Memory        |
| 连接器     | Integration   |
| 技能       | Skill         |
| 助理档案   | Agent Profile |
| 话题       | Topic         |
| 文稿       | Page          |
| 社区       | Community     |
| 资源       | Resource      |
| 库         | Library       |
| 模型服务商 | Provider      |
| 评测       | Evaluation    |
| 基准       | Benchmark     |
| 数据集     | Dataset       |
| 用例       | Test Case     |

## Brand Principles

1. **Create**: One sentence → usable Agent; clear next step
2. **Collaborate**: Multi-agent; shared Context; controlled
3. **Evolve**: Remember with consent; explainable; replayable

## Writing Rules

1. **Clarity first**: Short sentences, strong verbs, minimal adjectives
2. **Layered**: Main line (simple) + optional detail (precise)
3. **Consistent verbs**: Create / Connect / Run / Pause / Retry / View details
4. **Actionable**: Every message tells next step; avoid generic "OK/Cancel"

## Human Warmth (Balanced)

Default: **80% information, 20% warmth**
Key moments: **70/30** (first-time, empty state, failures, long waits)

**Hard cap**: At most half sentence of warmth, followed by clear next step.

**Order**:

1. Acknowledge situation (no judgment)
2. Restore control (pause/replay/edit/undo/clear Memory)
3. Provide next action

**Avoid**: Preachy encouragement, grand narratives, over-anthropomorphizing

## Patterns

**Getting started**:

- "Starting with one sentence is enough. Describe your goal."
- "Not sure where to begin? Tell me the outcome."

**Long wait**:

- "Running… You can switch tasks—I'll notify you when done."
- "This may take a few minutes. To speed up: reduce Context / switch model."

**Failure**:

- "That didn't run through. Retry, or view details to fix."
- "Connection failed. Re-authorize in Settings, or try again later."

**Collaboration**:

- "Align everyone to the same Context."
- "Different opinions are fine. Write the goal first."

## Errors/Exceptions

Must include:

1. **What happened**
2. (Optional) **Why**
3. **What user can do next**

Provide: Retry / View details / Go to Settings / Contact support / Copy logs

Never blame user. Put error codes in "Details".

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 microcopy 技能
skill = load_skill("microcopy")
result = skill.execute()
print(result)
```

