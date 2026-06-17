---
name: figma-create-new-file
name_zh: figma-创建-new-文件
description: 'Create a new blank Figma file. Use when the user wants to create a new'
description_zh: 创建 a new blank Figma file. Use when the 用户 wants to 创建 a new
category: code-assistants
tags:
  - ai
  - figma
  - frontend
  - javascript
  - llm
source: null
needs_review: false
slug: figma-create-new-file
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

Use this skill when you need to work with figma-create-new-file.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# create_new_file — Create a New Figma File

Use the `create_new_file` MCP tool to create a new blank Figma file in the user's drafts folder. This is typically used before `use_figma` when you need a fresh file to work with.

## Skill Arguments

This skill accepts optional arguments: `/figma-create-new-file [editorType] [fileName]`

- **editorType**: `design` (default) or `figjam`
- **fileName**: Name for the new file (defaults to "Untitled")

Examples:
- `/figma-create-new-file` — creates a design file named "Untitled"
- `/figma-create-new-file figjam My Whiteboard` — creates a FigJam file named "My Whiteboard"
- `/figma-create-new-file design My New Design` — creates a design file named "My New Design"

Parse the arguments from the skill invocation. If editorType is not provided, default to `"design"`. If fileName is not provided, default to `"Untitled"`.

## Workflow

### Step 1: Resolve the planKey

The `create_new_file` tool requires a `planKey` parameter. Follow this decision tree:

1. **User already provided a planKey** (e.g. from a previous `whoami` call or in their prompt) → use it directly, skip to Step 2.

2. **No planKey available** → call the `whoami` tool. The response contains a `plans` array. Each plan has a `key`, `name`, `seat`, and `tier`.

   - **Single plan**: use its `key` field automatically.
   - **Multiple plans**: ask the user which team or organization they want to create the file in, then use the corresponding plan's `key`.

### Step 2: Call create_new_file

Call the `create_new_file` tool with:

| Parameter    | Required | Description |
|-------------|----------|-------------|
| `planKey`   | Yes      | The plan key from Step 1 |
| `fileName`  | Yes      | Name for the new file |
| `editorType`| Yes      | `"design"` or `"figjam"` |

Example:
```json
{
  "planKey": "team:123456",
  "fileName": "My New Design",
  "editorType": "design"
}
```

### Step 3: Use the result

The tool returns:
- `file_key` — the key of the newly created file
- `file_url` — a direct URL to open the file in Figma

Use the `file_key` for subsequent tool calls like `use_figma`.

## Important Notes

- The file is created in the user's **drafts folder** for the selected plan.
- Only `"design"` and `"figjam"` editor types are supported.
- If `use_figma` is your next step, load the `figma-use` skill before calling it.

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 figma-create-new-file 技能
skill = load_skill("figma-create-new-file")
result = skill.execute()
print(result)
```

