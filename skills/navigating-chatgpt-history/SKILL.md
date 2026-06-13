---
name: navigating-chatgpt-history
name_zh: navigating-chatgpt-history
description: 'Navigates archived ChatGPT or Claude-style conversation exports and a MemFS reference archive on demand. Use when recalling what a past assistant knew, searching old conversations, rendering specif...'
description_zh: 'Navigates archived ChatGPT or Claude-style conversation exports and a MemFS reference archive on demand. Use when recalling what a past assistant knew, searching old conversations, rendering specif...'
category: applications
tags:
  - ai
  - evaluation
  - javascript
  - llm
  - python
license: MIT
needs_review: false
source: null
slug: navigating-chatgpt-history
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
---
# When to use

Use this skill when you need guidance on navigating-chatgpt-history.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Navigating Chat History Without Digesting Everything

Use this skill when the goal is **referenceable history**, not immediate full ingestion.

## Good fits

- search my exported ChatGPT history for a topic
- figure out what the old assistant knew about me
- render the conversation where we discussed X
- keep this export around as external memory and only mine it when needed
- seed MemFS from `memories.json` or `projects.json`

## Default posture

Treat the export as an archive you can navigate later.

1. read the MemFS archive index first if it exists: `reference/chatgpt/index.md`
2. inspect the export with `scripts/inspect-export.py`
3. search or list before rendering broad ranges
4. preserve findings to `reference/chatgpt/` first
5. promote to `system/human.md` only when the fact is durable, current, and worth carrying every turn

Do **not** re-digest the entire archive unless the user explicitly wants that.

## Archive layout in MemFS

Keep the external-memory archive under `reference/chatgpt/`.

Recommended files:

- `reference/chatgpt/index.md` — source exports, schema notes, known paths, retrieval strategy
- `reference/chatgpt/export-YYYY-MM-DD.md` — inventory and sidecar summary for one export
- `reference/chatgpt/chatgpt-memory-summary-YYYY-MM-DD.md` — content from `memories.json`
- `reference/chatgpt/projects-YYYY-MM-DD.md` — projects sidecar summary when useful
- `reference/chatgpt/transcripts/NNN-slug.md` — curated high-signal conversation summaries
- `reference/chatgpt/notes/` — topic-specific notes mined later

Prefer progressive memory. Keep active memory small.

## Scripts

### `scripts/inspect-export.py`

Use first. It inventories the export and reads sidecars such as `memories.json`, `projects.json`, and `users.json`.

```bash
python3 scripts/inspect-export.py <export-path>
python3 scripts/inspect-export.py <export-path> --output /tmp/export-summary.md
```

### `scripts/list-conversations.py`

Use to browse by title, recency, or message count.

```bash
python3 scripts/list-conversations.py <export-path> --limit 25
python3 scripts/list-conversations.py <export-path> --title-contains Letta --sort messages
```

### `scripts/search-conversations.py`

Use when titles are not enough.

```bash
python3 scripts/search-conversations.py <export-path> --query "Recovery Bench"
python3 scripts/search-conversations.py <export-path> --query TFCC --role user --limit 20
```

### `scripts/render-conversation.py`

Use for one conversation once you know the index.

```bash
python3 scripts/render-conversation.py <export-path> --index 212
python3 scripts/render-conversation.py <export-path> --index 212 --compact-nontext --output /tmp/chat-212.md
```

### `scripts/render-range.py`

Use only for focused batches after search narrows the field.

```bash
python3 scripts/render-range.py <export-path> --start-index 210 --end-index 220 --output-dir /tmp/chat-range
```

## Workflow

### 1. Anchor yourself in existing MemFS notes

Before touching the raw export, check whether the archive already has:

- an export summary
- a prior project summary
- curated transcripts
- a note on the same topic

If yes, use that first.

### 2. Inspect before mining

Run `inspect-export.py` to answer:

- what export shape is this?
- how many conversations are there?
- does `memories.json` already contain a synthesized memory block?
- does `projects.json` hold useful background?

For large archives, this often answers the question before raw conversation mining is needed.

### 3. Narrow, then render

Prefer this sequence:

1. `list-conversations.py` for browse
2. `search-conversations.py` for content lookup
3. `render-conversation.py` for deep read
4. `render-range.py` only when several adjacent conversations matter

Do not render dozens of chats just because you can.

### 4. Write findings to progressive memory first

When a conversation matters, summarize it into:

- `reference/chatgpt/transcripts/` for high-signal conversation summaries
- `reference/chatgpt/notes/` for topic notes

Only then decide whether anything belongs in `system/human.md`.

### 5. Promotion rule

Promote to active memory only when the fact is:

- explicit or strongly evidenced
- current rather than historical-only
- likely useful across many future conversations
- low-risk to keep in context every turn

Everything else can stay in `reference/chatgpt/`.

## Reference files

Read `references/repository-layout.md` when creating or extending the MemFS archive layout.

## Notes on export formats

This skill is designed for newer exports that contain `conversations.json` with `chat_messages`, while still handling older shard-based exports with `conversations-*.json` and `mapping` graphs.

When in doubt, start with `inspect-export.py` instead of assuming the schema.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
