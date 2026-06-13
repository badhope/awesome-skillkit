---
name: Haiku
name_zh: 俳句
description: Write haiku poems following specific style conventions
description_zh: 按照特定风格规范创作俳句诗
category: applications
tags:
  - ai
  - frontend
  - llm
  - python
  - typescript
source: null
needs_review: false
slug: haiku
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

Use this skill when you need guidance on haiku.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Haiku house style

When writing a haiku for this bot, follow these conventions:

- 5-7-5 syllable structure, strict.
- Prefer concrete imagery over abstraction.
- Include at least one season-word (kigo) when natural.
- No emojis, no preamble, no closing remarks — output ONLY the haiku itself.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```python
# Use the Haiku skill
from skill_loader import load_skill

skill = load_skill("haiku")
result = skill.execute(params={"key": "value"})
print(result)
```

