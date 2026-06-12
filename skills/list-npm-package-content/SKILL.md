---
name: list-npm-package-content
name_zh: list-npm-package-content
description: List the contents of an npm package tarball before publishing. Use 
  when the user wants to see what files are included in an npm bundle, verify 
  package contents, or debug npm publish issues.
description_zh: List the contents of an npm package tarball before publishing. 
  Use when the 用户 wants to see what files are included in an npm bundle, verify 
  package contents, or 调试 npm publish issues.
category: dev-tools
tags:
  - ai
  - documentation
  - frontend
  - git
  - javascript
source:
language: en
needs_review: false
slug: list-npm-package-content
version: 1.0.0
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

Use this skill when you need guidance on list-npm-package-content.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# List npm Package Content

This skill lists the exact contents of an npm package tarball - the same files that would be uploaded to npm and downloaded by users.

## Usage

Run the script from the package directory (e.g., `packages/ai`):

```bash
bash scripts/list-package-files.sh
```

The script will build the package, create a tarball, list its contents, and clean up automatically.

## Understanding Package Contents

The files included are determined by:

1. **`files` field in `package.json`** - explicit allowlist of files/directories
2. **`.npmignore`** - files to exclude (if present)
3. **`.gitignore`** - used if no `.npmignore` exists
4. **Always included**: `package.json`, `README`, `LICENSE`, `CHANGELOG`
5. **Always excluded**: `.git`, `node_modules`, `.npmrc`, etc.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
