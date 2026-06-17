---
name: Task
name_zh: 任务
description: Execute tasks within the LobeHub task system using the lh task CLI
description_zh:
category: dev-tools
tags:
  - ai
  - cli
  - documentation
  - frontend
  - javascript
source:
needs_review: false
slug: task
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

Use this skill when you need guidance on task.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Task Lifecycle

| Command                         | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| `lh task view <id>`             | View task details, instruction, workspace, activities |
| `lh task edit <id>`             | Update task name, instruction, status, priority       |
| `lh task complete <id>`         | Mark task as completed                                |
| `lh task comment <id> -m "..."` | Add a progress comment                                |
| `lh task tree <id>`             | View subtask tree with dependencies                   |

# Working with Subtasks

| Command                                   | Description       |
| ----------------------------------------- | ----------------- |
| `lh task create -i "..." --parent <id>`   | Create a subtask  |
| `lh task list --parent <id>`              | List subtasks     |
| `lh task sort <parentId> <id1> <id2> ...` | Reorder subtasks  |
| `lh task dep add <id> <dependsOnId>`      | Add dependency    |
| `lh task dep rm <id> <dependsOnId>`       | Remove dependency |

# Task Workspace (Documents)

| Command                                           | Description               |
| ------------------------------------------------- | ------------------------- |
| `lh task doc create <id> -t "title" -b "content"` | Create and pin a document |
| `lh task doc pin <id> <docId>`                    | Pin existing document     |
| `lh task doc unpin <id> <docId>`                  | Unpin document            |

# Task Topics (Conversations)

| Command                             | Description              |
| ----------------------------------- | ------------------------ |
| `lh task topic list <id>`           | List conversation topics |
| `lh task topic view <id> <topicId>` | View topic messages      |

# Usage Pattern

1. Read the reference file for detailed command options: `readReference('references/commands')`
2. Run commands via `runCommand` — the `lh` prefix is automatically handled
3. Use `--json` flag on any command for structured output
4. Use `lh task <subcommand> --help` for full command-line help

# Task Execution Guidelines

- **Check your task first**: Use `lh task view` to understand the full instruction and context
- **Use workspace documents**: Store outputs and deliverables as task documents
- **Report progress**: Use `lh task comment` to log key milestones
- **Respect dependencies**: Check `lh task tree` to understand task ordering
- **Complete when done**: Use `lh task complete` when all deliverables are ready
  \</task_skill_guides>

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```bash
# Use the Task skill
python scripts/use-skill.py task

# View skill details
python scripts/inspect-skill.py task
```

\<task_skill_guides>
You are executing a task within the LobeHub task system. Use the `lh task` CLI via `runCommand` to manage your task and related resources.
