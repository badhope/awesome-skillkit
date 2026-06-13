---
name: add-function-examples
name_zh: add-函数-examples
description: 'Guide for adding new AI function examples, for testing specific features against the actual provider APIs.'
description_zh: 'Guide for adding new AI 函数 examples, for 测试 specific features against the actual provider APIs.'
category: applications
tags:
  - ai
  - api
  - backend
  - documentation
  - frontend
source: null
needs_review: false
slug: add-function-examples
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
## Adding Function Examples

Review the changes in the current branch, and identify new or modified features or bug fixes that would benefit from having an example in the `examples/ai-functions` directory. These examples are used for testing specific features against the actual provider APIs, and can also serve as documentation for users.

Determine for which kind of model and top-level function the example should be added. For a language model, the example should be added in two variants, one for `generateText` and one for `streamText`. For any other models kinds, add the example for the relevant top-level function (e.g. `generateImage`, `generateSpeech`).

After creating the example, run `pnpm type-check:full`; fix any errors encountered.

# When to use

Use this skill when you need guidance on add-function-examples.

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
# Use the add-function-examples skill
from skill_loader import load_skill

skill = load_skill("add-function-examples")
result = skill.execute(params={"key": "value"})
print(result)
```

