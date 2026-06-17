---
name: memfs-search
name_zh: memfs-搜索
description: 'Semantic search over agent memory files. Use when you need to find conceptually'
description_zh: 'Semantic search over 智能体 memory files. Use when you need to find conceptually'
category: memory
tags:
  - ai
  - documentation
  - evaluation
  - frontend
  - javascript
source: null
needs_review: false
slug: memfs-search
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

Use this skill when you need to work with memfs-search.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# MemFS Search

Semantic search over your memory filesystem. Useful when Grep isn't enough — finding conceptually related blocks, discovering forgotten reference files, or answering "what do I know about X" across all memory.

## Setup

First time only. Run the setup script to create the index and generate embeddings:

```bash
bash <SKILL_DIR>/scripts/memfs-search.sh setup
```

This creates a QMD collection over `$MEMORY_DIR`, adds context annotations, and embeds all `.md` files. First run downloads ~2GB of local GGUF models to `~/.cache/qmd/models/`.

For installation, embedding model options, and troubleshooting: [references/qmd-setup.md](references/qmd-setup.md).

## Searching

Three tiers. Pick based on what you know about your query:

| You have... | Use | Command | Speed |
|-------------|-----|---------|-------|
| An exact term or phrase | **keyword** | `search` | ~0.3s |
| A vague concept ("what do I know about X") | **semantic** | `vsearch` | ~2s cold, <1s warm |
| No idea, need the best results | **hybrid** | `query` | ~3s cold, <1s warm |

```bash
S="bash <SKILL_DIR>/scripts/memfs-search.sh"

# Keyword — fast, use first
$S search "lettabot architecture"

# Semantic — conceptual, use when keyword misses
$S vsearch "how does the user feel about code reviews"

# Hybrid — best quality, uses keyword + vectors + reranking
$S query "projects cameron is working on"
```

**Always start with keyword search.** Only escalate when it misses. Hybrid is 10x slower than keyword.

### Output Formats

All commands accept output flags forwarded to QMD:

```bash
$S search "topic" --json       # structured (for processing)
$S search "topic" --files      # file paths only (pipe into Read)
$S search "topic" --full       # full document, not snippet
$S search "topic" -n 15        # more results (default: 5)
```

`--json` returns an array of objects with `file`, `score`, `snippet`, and `context` fields.

### Retrieval

Fetch a specific file or batch of files without searching:

```bash
# Single file
qmd get "system/human/identity.md" -c memory --full

# Batch by glob
qmd multi-get "reference/projects/*" -c memory
```

## When to Search Proactively

Don't wait to be asked. Search memory when:

1. **Before creating a new memory file** — check if the topic already exists. `$S search "topic" --files` tells you instantly.
2. **User asks "do you know about X"** — search before saying no. Reference files you haven't loaded recently might have it.
3. **During `/init` or memory reorg** — verify coverage. Search for key concepts and confirm they're stored somewhere.
4. **Debugging "I told you about this"** — the user thinks you should know something. Search memory before falling back to message history.

## Maintenance

After bulk memory changes (e.g. after `/init`, reorganization, creating many files):

```bash
bash <SKILL_DIR>/scripts/memfs-search.sh reindex
```

Check index health:

```bash
bash <SKILL_DIR>/scripts/memfs-search.sh status
```

## When NOT to Use

- Exact string matching — use Grep.
- Finding files by name/pattern — use Glob.
- Reading a file you already know the path to — use Read.
- Searching message history — use the `searching-messages` skill.
- The query is a single word that would match literally — keyword Grep is faster.

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 memfs-search 技能
skill = load_skill("memfs-search")
result = skill.execute()
print(result)
```

