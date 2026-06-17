---
name: add-provider-doc
name_zh:
description: 'Add documentation for a new AI provider — usage docs, env vars, Docker'
description_zh:
category: dev-tools
tags:
  - ai
  - api
  - backend
  - database
  - docker
source:
needs_review: false
slug: add-provider-doc
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

Use this skill when you need to work with add-provider-doc.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# Adding New AI Provider Documentation

Complete workflow for adding documentation for a new AI provider.

## Overview

1. Create usage documentation (EN + CN)
2. Add environment variable documentation (EN + CN)
3. Update Docker configuration files
4. Update .env.example
5. Prepare image resources

## Step 1: Create Provider Usage Documentation

### Required Files

- `docs/usage/providers/{provider-name}.mdx` (English)
- `docs/usage/providers/{provider-name}.zh-CN.mdx` (Chinese)

### Key Requirements

- 5-6 screenshots showing the process
- Cover image for the provider
- Real registration and dashboard URLs
- Pricing information callout
- **Never include real API keys** - use placeholders

Reference: `docs/usage/providers/fal.mdx`

## Step 2: Update Environment Variables Documentation

### Files to Update

- `docs/self-hosting/environment-variables/model-provider.mdx` (EN)
- `docs/self-hosting/environment-variables/model-provider.zh-CN.mdx` (CN)

### Content Format

```markdown
### `{PROVIDER}_API_KEY`

- Type: Required
- Description: API key from {Provider Name}
- Example: `{api-key-format}`

### `{PROVIDER}_MODEL_LIST`

- Type: Optional
- Description: Control model list. Use `+` to add, `-` to hide
- Example: `-all,+model-1,+model-2=Display Name`
```

## Step 3: Update Docker Files

Update all Dockerfiles at the **end** of ENV section:

- `Dockerfile`
- `Dockerfile.database`
- `Dockerfile.pglite`

```dockerfile
# {New Provider}
{PROVIDER}_API_KEY="" {PROVIDER}_MODEL_LIST=""
```

## Step 4: Update .env.example

```bash
### {Provider Name} ###
# {PROVIDER}_API_KEY={prefix}-xxxxxxxx
```

## Step 5: Image Resources

- Cover image
- 3-4 API dashboard screenshots
- 2-3 LobeHub configuration screenshots
- Host on LobeHub CDN: `hub-apac-1.lobeobjects.space`

## Checklist

- [ ] EN + CN usage docs
- [ ] EN + CN env var docs
- [ ] All 3 Dockerfiles updated
- [ ] .env.example updated
- [ ] All images prepared
- [ ] No real API keys in docs

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 add-provider-doc 技能
skill = load_skill("add-provider-doc")
result = skill.execute()
print(result)
```

