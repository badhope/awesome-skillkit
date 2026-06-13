---
name: Standards Check
name_zh: 标准检查
description: Checks that a project follows standard conventions
description_zh: 检查代码是否符合项目标准和最佳实践。
category: dev-tools
tags:
  - ai
  - documentation
  - frontend
  - git
  - llm
source: null
license: UNKNOWN
author: unknown
version: '0.1.0'
needs_review: false
slug: standards-check
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

Use this skill when you need guidance on standards check.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Standards Check

Check that the project has the following required files:

1. `README.md` — project documentation

Report which required files are missing.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

```bash
# 检查项目是否符合标准规范

# 1. 检查必需文件
for f in README.md LICENSE CONTRIBUTING.md .editorconfig; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
  else
    echo "OK: $f"
  fi
done

# 2. 检查代码规范（以 Python 为例）
ruff check . --select E,W,F,I,N
black --check .

# 3. 检查 TypeScript 规范
tsc --noEmit
eslint . --ext .ts,.tsx

# 4. 检查 CI 配置
if [ ! -f ".github/workflows/ci.yml" ]; then
  echo "WARNING: No CI workflow found"
fi
```

