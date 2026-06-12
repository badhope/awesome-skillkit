---
name: guidelines
name_zh: guidelines
description: "Response formatting and communication guidelines for generating clear, accurate, and well-structured replies."
description_zh: "Response formatting and communication guidelines for generating clear, accurate, and well-structured replies."
category: ai
tags: [ai, frontend, llm, python, typescript]
source: 
language: en
needs_review: false
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


# Prompt

Follow the guidelines in this skill when working on related tasks.
