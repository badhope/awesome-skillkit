---
name: pr-review
name_zh: pr-审查
description: Review a PR for correctness, security, code quality, and testing 
  issues.
description_zh: 审查 a PR for correctness, 安全, 代码 quality, and 测试 issues.
category: dev-tools
tags:
  - ai
  - api
  - backend
  - database
  - frontend
source:
author: autogpt-team
version: 1.0.0
needs_review: false
slug: pr-review
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
license: MIT
---
# When to use

Use this skill when you need to work with pr-review.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# PR Review

## Find the PR

```bash
gh pr list --head $(git branch --show-current) --repo Significant-Gravitas/AutoGPT
gh pr view {N}
```

## Read the PR description

Before reading code, understand the **why**, **what**, and **how** from the PR description:

```bash
gh pr view {N} --json body --jq '.body'
```

Every PR should have a Why / What / How structure. If any of these are missing, note it as feedback.

## Read the diff

```bash
gh pr diff {N}
```

## Fetch existing review comments

Before posting anything, fetch existing inline comments to avoid duplicates:

```bash
gh api repos/Significant-Gravitas/AutoGPT/pulls/{N}/comments --paginate
gh api repos/Significant-Gravitas/AutoGPT/pulls/{N}/reviews
```

## What to check

**Description quality:** Does the PR description cover Why (motivation/problem), What (summary of changes), and How (approach/implementation details)? If any are missing, request them — you can't judge the approach without understanding the problem and intent.

**Correctness:** logic errors, off-by-one, missing edge cases, race conditions (TOCTOU in file access, credit charging), error handling gaps, async correctness (missing `await`, unclosed resources).

**Security:** input validation at boundaries, no injection (command, XSS, SQL), secrets not logged, file paths sanitized (`os.path.basename()` in error messages).

**Code quality:** apply rules from backend/frontend CLAUDE.md files.

**Architecture:** DRY, single responsibility, modular functions. `Security()` vs `Depends()` for FastAPI auth. `data:` for SSE events, `: comment` for heartbeats. `transaction=True` for Redis pipelines.

**Testing:** edge cases covered, colocated `*_test.py` (backend) / `__tests__/` (frontend), mocks target where symbol is **used** not defined, `AsyncMock` for async.

## Output format

Every comment **must** be prefixed with `🤖` and a criticality badge:

| Tier | Badge | Meaning |
|---|---|---|
| Blocker | `🔴 **Blocker**` | Must fix before merge |
| Should Fix | `🟠 **Should Fix**` | Important improvement |
| Nice to Have | `🟡 **Nice to Have**` | Minor suggestion |
| Nit | `🔵 **Nit**` | Style / wording |

Example: `🤖 🔴 **Blocker**: Missing error handling for X — suggest wrapping in try/except.`

## Post inline comments

For each finding, post an inline comment on the PR (do not just write a local report):

```bash
# Get the latest commit SHA for the PR
COMMIT_SHA=$(gh api repos/Significant-Gravitas/AutoGPT/pulls/{N} --jq '.head.sha')

# Post an inline comment on a specific file/line
gh api repos/Significant-Gravitas/AutoGPT/pulls/{N}/comments \
  -f body="🤖 🔴 **Blocker**: <description>" \
  -f commit_id="$COMMIT_SHA" \
  -f path="<file path>" \
  -F line=<line number>
```

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 pr-review 技能
skill = load_skill("pr-review")
result = skill.execute()
print(result)
```

