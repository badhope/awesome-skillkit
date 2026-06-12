---
name: Haiku
name_zh: 俳句
description: Write haiku poems following specific style conventions
description_zh: 按照特定风格规范创作俳句诗
category: ai
tags: [ai, frontend, llm, python, typescript]
source: 
language: en
needs_review: false
---

# Haiku house style

When writing a haiku for this bot, follow these conventions:

- 5-7-5 syllable structure, strict.
- Prefer concrete imagery over abstraction.
- Include at least one season-word (kigo) when natural.
- No emojis, no preamble, no closing remarks — output ONLY the haiku itself.

# When to use

Use this skill when you need guidance on haiku.

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


# Prompt

Follow the guidelines in this skill when working on related tasks.
