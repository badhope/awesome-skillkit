---
name: "gh-address-comments"
name_zh: "gh-address-comments"
description: Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and prompt the user to authenticate if not logged in.
description_zh: Help address 审查/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and 提示词 the 用户 to authenticate if not logged in.
category: "dev-tools"
tags: [ai, cli, database, frontend, git]
source: 
language: en
needs_review: false
---



# PR Comment Handler

Guide to find the open PR for the current branch and address its comments with gh CLI. Run all `gh` commands with elevated network access.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run `gh auth status` with escalated permissions (include workflow/repo scopes) so `gh` commands succeed. If sandboxing blocks `gh auth status`, rerun it with `sandbox_permissions=require_escalated`.

## 1) Inspect comments needing attention
- Run scripts/fetch_comments.py which will print out all the comments and review threads on the PR

## 2) Ask the user for clarification
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for it
- Ask the user which numbered comments should be addressed

## 3) If user chooses comments
- Apply fixes for the selected comments

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.

# When to use

Use this skill when you need guidance on gh-address-comments.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```bash
# Use the gh-address-comments skill
python scripts/use-skill.py gh-address-comments

# View skill details
python scripts/inspect-skill.py gh-address-comments
```


# Prompt

Follow the guidelines in this skill when working on related tasks.
