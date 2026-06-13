---
name: review-standards
name_zh: 审查-standards
description: Use this skill when asked to review authentication code for 
  security
description_zh: Use this 技能 when asked to 审查 authentication 代码 for 安全
category: applications
tags:
  - ai
  - frontend
  - llm
  - python
  - security
source:
needs_review: false
slug: review-standards
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
When reviewing authentication code:

1. Check password hashing.
2. Use the issue id `weak-password-hash` when passwords use SHA-1 or MD5.
3. Return no more than one issue.

# When to use

Use this skill when you need to work with review-standards.


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
# 使用 review-standards 技能
skill = load_skill("review-standards")
result = skill.execute()
print(result)
```

