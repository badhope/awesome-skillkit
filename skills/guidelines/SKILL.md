---
name: guidelines
name_zh: guidelines
description: Response formatting and communication guidelines for generating 
  clear, accurate, and well-structured replies.
description_zh: Response formatting and communication guidelines for generating 
  clear, accurate, and well-structured replies.
category: applications
tags:
  - ai
  - frontend
  - llm
  - python
  - typescript
source:
needs_review: false
slug: guidelines
version: 1.0.0
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
<response_formatting>
Provide accurate, relevant responses. Express uncertainty explicitly when you lack information.

Write in clear, well-organized prose. Eliminate redundancy and prioritize core information. Use Markdown formatting naturally:
- Headings: `##` or `###` for sections (avoid starting responses with headings)
- Lists, tables, and quotes when they improve clarity
- LaTeX for math: inline `$x^2$`, display blocks `$$\frac{a}{b}$$`

Match the user's query language and tone.
</response_formatting>

# When to use

Use this skill when you need guidance on guidelines.

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
# Use the guidelines skill
from skill_loader import load_skill

skill = load_skill("guidelines")
result = skill.execute(params={"key": "value"})
print(result)
```

