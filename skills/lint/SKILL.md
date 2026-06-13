---
name: lint
name_zh: lint
description: Run linting and formatting checks on Ray code
description_zh: 运行 linting and formatting checks on Ray 代码
category: dev-tools
tags:
  - ai
  - api
  - documentation
  - frontend
  - git
source: null
needs_review: false
slug: lint
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

Use this skill when you need guidance on lint.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Lint Modified Files

Run pre-commit on the files you changed:

```bash
pre-commit run --files $(git diff --name-only HEAD)
```

`pre-commit run` without `--files` only operates on staged files, so pass the
modified file list explicitly.

If pre-commit is not installed:
```bash
pip install -c python/requirements_compiled.txt pre-commit && pre-commit install
```

## Handling remaining errors

Pre-commit auto-fixes simple issues (formatting, long lines, unused imports).
Review any remaining errors — these typically need code changes such as adding a
missing import, resolving a name conflict, or restructuring logic. Fix them by
editing the source code directly.

Use `# noqa` only for false positives that cannot be resolved by changing the code,
and include the rule code and reason: `# noqa: E501 — URL cannot be split`.

## Exclusions

pyproject.toml lists files in `per-file-ignores` and `extend-exclude`. When the PR
modifies a file that is on one of these lists, fix the lint issues in your changes
and consider removing the file from the list. Leave exclusion entries for files
outside the PR scope untouched.

## Reference

- Hook config: .pre-commit-config.yaml
- Ruff config: pyproject.toml (`[tool.ruff]` section)
- Docs: doc/source/ray-contribute/development.rst ("Development tooling")

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
