---
name: git-workflow
name_zh: Git 工作流
description: Git workflow guidance for commits, branches, and pull requests
description_zh: 遵循 Git 工作流最佳实践，包括分支策略和提交规范。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - documentation
  - frontend
source: null
license: Apache-2.0
author: unknown
version: '0.1.0'
needs_review: false
slug: git-workflow
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

Use this skill when you need guidance on git workflow.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Git Workflow Skill

You are a Git workflow assistant. Help users with commits, branches, and pull requests following best practices.

## Commit Message Guidelines

For commit message generation and validation, use `get_skill_script("git-workflow", "commit_message.py")`.

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, no code change
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```
feat(auth): add OAuth2 login support

Implemented OAuth2 authentication flow with Google and GitHub providers.
Added token refresh mechanism and session management.

Closes #123
```

```
fix(api): handle null response from external service

Added null check before processing response data to prevent
NullPointerException when external service returns empty response.

Fixes #456
```

## Branch Naming

### Format
```
<type>/<ticket-id>-<short-description>
```

### Examples
- `feature/AUTH-123-oauth-login`
- `fix/BUG-456-null-pointer`
- `chore/TECH-789-update-deps`

## Pull Request Guidelines

### Title
Follow commit message format for the title.

### Description Template
```markdown
## Summary
Brief description of what this PR does.

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

## Common Commands

### Starting Work
```bash
git checkout main
git pull origin main
git checkout -b feature/TICKET-123-description
```

### Committing
```bash
git add -p  # Interactive staging
git commit -m "type(scope): description"
```

### Updating Branch
```bash
git fetch origin
git rebase origin/main
```

### Creating PR
```bash
git push -u origin feature/TICKET-123-description
# Then create PR on GitHub/GitLab
```

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.

