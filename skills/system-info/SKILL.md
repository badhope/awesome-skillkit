---
name: "system-info"
name_zh: "system-info"
description: Get system information using executable scripts
description_zh: Get system information using executable scripts
category: ai
tags: [ai, python, typescript]
license: MIT
author: agno
version: 1.0.0
needs_review: false
source: 
language: en
---

# System Info Skill

This skill provides scripts to gather system information.

## Available Scripts

- `get_system_info.py` - Returns basic system information (OS, Python version, current time)
- `list_directory.py` - Lists files in a specified directory

## Usage

1. Use `run_skill_script("system-info", "get_system_info.py")` to get system information
2. Use `run_skill_script("system-info", "list_directory.py", args=["path"])` to list a directory

# When to use

Use this skill when you need guidance on system-info.

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


# Prompt

Follow the guidelines in this skill when working on related tasks.
