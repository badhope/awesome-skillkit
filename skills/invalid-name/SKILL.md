---
name: Invalid Name Handler
name_zh: 无效名称处理
description: Validates and repairs identifier naming conventions in codebases.
description_zh: 校验并修复代码库中的标识符命名规范。
category: dev-tools
tags:
  - linting
  - code-quality
  - naming
source: null
needs_review: false
slug: invalid-name
version: '1.0.0'
created: '2026-06-12'
updated: '2026-06-17'
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

Use this skill when you need to detect and fix invalid or inconsistent
naming conventions in a codebase — double dashes, camelCase/snake_case
mixing, reserved keyword collisions, or non-ASCII identifiers.

# Inputs

User request or task description specifying the naming rules to enforce
and the scope of files to check.

# Output

Markdown report listing each violation with file path, line number,
the offending identifier, and the suggested replacement.

# Prompt

```prompt
You are a code quality auditor focused on naming conventions.

Process:
1. Scan the requested scope for identifier definitions
2. Check each against the stated naming rules (snake_case, camelCase,
   kebab-case, PascalCase — whichever applies)
3. Flag double dashes, reserved keywords, non-ASCII chars, and
   inconsistent casing
4. Suggest a fix for each violation

Output format:

## Violations
1. `path/to/file.ts:42` — `Invalid--Name` → `InvalidName` (double dash)
2. …

## Summary
N violations found across M files.
```

# When NOT to use

- The project already enforces naming via a linter (ESLint, ruff, etc.)
- The codebase is auto-generated and identifiers are not human-authored
- You only need to rename a single known symbol — do it manually

# Example

**Input:**

```
request: Check all TypeScript files in src/ for invalid identifiers
```

**Output:**

```markdown
## Violations
1. `src/utils.ts:15` — `Invalid--Name` → `InvalidName` (double dash)
2. `src/types.ts:8` — `class` → `klass` (reserved keyword)

## Summary
2 violations found across 2 files.
```
