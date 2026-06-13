---
name: app
name_zh: app
description: Opinionated app components building on top of ./ui primitives
description_zh: Opinionated app components building on top of ./ui primitives
category: applications
tags:
  - ai
  - frontend
  - javascript
  - llm
  - python
source: null
needs_review: false
slug: app
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

Use this skill when you need guidance on app.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```python
# Use the app skill
from skill_loader import load_skill

skill = load_skill("app")
result = skill.execute(params={"key": "value"})
print(result)
```

- Can include business logic and state management
- Can include data fetching and caching logic
- Should use original spelling for HTML-native events and `camelCase` for custom events
- Props and markup attributes should be listed alphabetically
- Use JS Objects and Arrays for CSS classes and styles when they are dynamic
- Whenever there can be repetition in the component's markup, if it's too small to be decoupled as a separate component — use Svelte 5's `{#snippet}` + `{@render}`
