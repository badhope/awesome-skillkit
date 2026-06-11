---
name: system-info
description: Get system information using executable scripts
license: MIT
metadata:
  version: 1.0.0
  author: agno
slug: system-info
version: 0.1.0
category: uncategorized
tags:
  - needs-tagging
inputs: []
output:
  format: markdown
author: unknown
created: '2026-06-11'
updated: '2026-06-11'
needs_review: true
---
# System Info Skill

This skill provides scripts to gather system information.

## Available Scripts

- `get_system_info.py` - Returns basic system information (OS, Python version, current time)
- `list_directory.py` - Lists files in a specified directory

## Usage

1. Use `run_skill_script("system-info", "get_system_info.py")` to get system information
2. Use `run_skill_script("system-info", "list_directory.py", args=["path"])` to list a directory
