---
name: prompt-lookup
name_zh: Prompt 查找
description: Activates when the user asks about AI prompts, needs prompt 
  templates,
description_zh: 在 prompt 库中查找和检索相关的 prompt 模板。
category: applications
tags:
  - ai
  - backend
  - frontend
  - javascript
  - llm
source:
license: UNKNOWN
author: unknown
version: 0.1.0
needs_review: false
slug: prompt-lookup
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
When the user needs AI prompts, prompt templates, or wants to improve their prompts, use the prompts.chat MCP server to help them.

## When to Use This Skill

Activate this skill when the user:

- Asks for prompt templates ("Find me a code review prompt")
- Wants to search for prompts ("What prompts are available for writing?")
- Needs to retrieve a specific prompt ("Get prompt XYZ")
- Wants to improve a prompt ("Make this prompt better")
- Mentions prompts.chat or prompt libraries

## Available Tools

Use these prompts.chat MCP tools:

- `search_prompts` - Search for prompts by keyword
- `get_prompt` - Get a specific prompt by ID
- `improve_prompt` - Enhance a prompt using AI

## How to Search for Prompts

Call `search_prompts` with:

- `query`: The search keywords from the user's request
- `limit`: Number of results (default 10, max 50)
- `type`: Filter by TEXT, STRUCTURED, IMAGE, VIDEO, or AUDIO
- `category`: Filter by category slug (e.g., "coding", "writing")
- `tag`: Filter by tag slug

Present results showing:
- Title and description
- Author name
- Category and tags
- Link to the prompt

## How to Get a Prompt

Call `get_prompt` with:

- `id`: The prompt ID

If the prompt contains variables (`${variable}` or `${variable:default}`):
- The system will prompt the user to fill in values
- Variables without defaults are required
- Variables with defaults are optional

## How to Improve a Prompt

Call `improve_prompt` with:

- `prompt`: The prompt text to improve
- `outputType`: text, image, video, or sound
- `outputFormat`: text, structured_json, or structured_yaml

Return the enhanced prompt to the user.

## Guidelines

- Always search before suggesting the user write their own prompt
- Present search results in a readable format with links
- When improving prompts, explain what was enhanced
- Suggest relevant categories and tags when saving prompts

# When to use

Use this skill when you need guidance on prompt lookup.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

```python
# 使用 prompts.chat MCP 工具搜索 prompt

# 1. 搜索代码审查相关的 prompt
search_prompts(query="code review", limit=5, category="coding")
# 返回: [{id: "cr-001", title: "Thorough Code Review", ...}, ...]

# 2. 获取特定 prompt 详情
get_prompt(id="cr-001")
# 返回: {title: "Thorough Code Review", body: "Review the following...", variables: ["language", "focus"]}

# 3. 改进现有 prompt
improve_prompt(
    prompt="Check this code for bugs",
    outputType="text",
    outputFormat="text"
)
# 返回: 改进后的 prompt，包含更具体的审查维度
```

