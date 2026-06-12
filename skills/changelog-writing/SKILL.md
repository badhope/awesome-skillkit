---
name: changelog-writing
name_zh: 编写变更日志
description: Shared workflow for writing Langfuse changelog entries after a 
  feature
description_zh: 编写清晰、用户友好的变更日志，记录版本更新和改进。
category: dev-tools
tags:
  - ai
  - deployment
  - documentation
  - frontend
  - git
source:
license: UNKNOWN
language: en
author: unknown
version: 0.1.0
needs_review: false
slug: changelog-writing
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

Use this skill when you need guidance on changelog writing.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Changelog Writing

Use this skill when a completed feature branch needs a changelog entry.

## Workflow

1. Understand the change set.
2. Study recent changelog patterns in `../langfuse-docs/pages/changelog`.
3. Find related documentation links in `../langfuse-docs/pages`.
4. Draft a user-focused changelog entry.
5. Recommend whether an image or screenshot should be added.

## What To Gather

- The branch diff relative to `main`
- The Linear issue, if the branch name includes an `lfe-XXXX` identifier
- The affected product areas
- Relevant docs pages to link or create

## Writing Rules

- Write for users, not internal implementation detail
- Prefer second person: "you can now..."
- Focus on what changed, why it matters, and how to use it
- Match the structure and tone of recent changelog posts
- Keep technical detail only where it improves user understanding

## Output Format

Provide:

1. A short summary of what changed
2. The complete changelog post content
3. Whether an image should be added and what it should show
4. Any docs pages that should be linked or created

## Reference Files

- Changelog destination: `../langfuse-docs/pages/changelog`
- Recent changelog examples: inspect 3-5 recent files in that directory
- Existing docs: `../langfuse-docs/pages`

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

```bash
# 1. 查看分支变更
git diff main..HEAD --stat

# 2. 查看最近的changelog格式
ls ../langfuse-docs/pages/changelog/ | tail -5
cat ../langfuse-docs/pages/changelog/2024-01-release.md

# 3. 生成changelog草稿
python scripts/generate-changelog.py \
  --branch feature/new-dashboard \
  --output changelog-draft.md

# 4. 检查格式
python scripts/validate-changelog.py changelog-draft.md
```

