---
name: system-info
name_zh: system-info
description: Get system information using executable scripts
description_zh: Get system information using executable scripts
category: applications
tags:
  - ai
  - python
  - typescript
license: MIT
author: agno
version: 1.0.0
needs_review: false
source:
language: en
slug: system-info
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
---
# When to use

Use this skill when you need guidance on system-info.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# System Info Skill

This skill provides scripts to gather system information.

## Available Scripts

- `get_system_info.py` - Returns basic system information (OS, Python version, current time)
- `list_directory.py` - Lists files in a specified directory

## Usage

1. Use `run_skill_script("system-info", "get_system_info.py")` to get system information
2. Use `run_skill_script("system-info", "list_directory.py", args=["path"])` to list a directory

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```python
# Use the system-info skill
from skill_loader import load_skill

skill = load_skill("system-info")
result = skill.execute(params={"key": "value"})
print(result)
```

