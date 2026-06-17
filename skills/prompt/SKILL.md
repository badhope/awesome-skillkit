---
name: Prompt
name_zh: 提示词
description: Create effective prompts for LLMs and AI agents
description_zh: 为大语言模型和AI智能体创建有效的提示词
category: prompt-libraries
tags:
  - ai
  - frontend
  - llm
  - python
  - typescript
source: null
needs_review: false
slug: prompt
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

Use this skill when you need guidance on prompt.

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
# Use the Prompt skill
from skill_loader import load_skill

skill = load_skill("prompt")
result = skill.execute(params={"key": "value"})
print(result)
```

You're an angry pirate.

Be concise and stay in character.

Tell me about {{topic}}
