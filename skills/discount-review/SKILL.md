---
name: discount-review
name_zh: discount-审查
description: 'Inspect the discount policy fixture with a repeatable review checklist'
description_zh: 'Inspect the discount policy fixture with a repeatable 审查 checklist'
category: dev-tools
tags:
  - ai
  - frontend
  - llm
  - python
  - typescript
source: null
needs_review: false
slug: discount-review
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
Use this skill when asked to review the discount-policy fixture under `skill_fixture/repo`.

1. Do not enumerate this skill directory; the workflow below is complete.
2. Run `python3 skills/discount-review/scripts/analyze_discount_policy.py skill_fixture/repo`.
3. Use the helper output as the source of truth for ticket id, severity, owner, primary file, and minimal fix.
4. Inspect `skill_fixture/repo/src/discount_policy.py` before answering.
5. Return a concise maintainer report that includes the helper command you ran.

# When to use

Use this skill when you need to work with discount-review.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 discount-review 技能
skill = load_skill("discount-review")
result = skill.execute()
print(result)
```

