---
name: creating-letta-code-channels
name_zh: creating-letta-代码-channels
description: 'Builds and debugs Letta Code channels, including first-party channel adapters and dynamic user channel plugins under ~/.letta/channels. Use when adding Telegram, WhatsApp, Bluesky, Slack, Discord, ...'
description_zh: 'Builds and debugs Letta 代码 channels, including first-party channel adapters and dynamic 用户 channel plugins under ~/.letta/channels. Use when adding Telegram, WhatsApp, Bluesky, Slack, Discord, or c...'
category: dev-tools
tags:
  - ai
  - api
  - cli
  - deployment
  - documentation
source: null
license: MIT
needs_review: false
slug: creating-letta-code-channels
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

Use this skill when you need guidance on creating-letta-code-channels.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Creating Letta Code channels

Use this when adding or debugging Letta Code channel support.

## First choice

- **User plugin** (`~/.letta/channels/<id>/`) for headless experiments, community plugins, and fast workflow tests.
- **First-party channel** (`src/channels/<id>/`) when the channel needs bespoke Desktop UI, custom account snapshots, Slack/Discord-style auto-routing, rich protocol fields, or migration/compatibility shims.

User plugins cannot shadow first-party ids: `telegram`, `slack`, and `discord` are ignored under `~/.letta/channels/`. Use ids like `telegram-test`, `whatsapp-community`, or `custom-chat`.

## Core workflow

1. Work in `~/letta/letta-code` or a worktree.
2. Read `src/channels/README.md` on branches with dynamic plugins.
3. For a user plugin, create:
   - `~/.letta/channels/<id>/channel.json`
   - `~/.letta/channels/<id>/plugin.mjs`
   - `~/.letta/channels/<id>/accounts.json`
4. Always implement `messageActions` if agents should reply via `MessageChannel`.
5. Start with `dmPolicy: "pairing"` for testing, or `allowlist`/`open` for known headless deployments.
6. Test all four legs:
   - plugin discovery/import
   - inbound `adapter.onMessage(msg)` to route/pairing
   - routed channel notification reaches the agent
   - outbound `MessageChannel` calls `messageActions.handleAction` → `adapter.sendMessage`
7. Run targeted tests, then `bun run typecheck`, `bun run lint`, `bun run build`.

## References

Read only what is needed:

- `references/user-plugins.md` — dynamic plugin manifest/account/runtime/headless flow and gotchas.
- `references/first-party-channels.md` — first-party channel file cascade and safety checks.
- `references/testing.md` — smoke-test checklist and commands.

## Scaffold helper

Use the bundled scaffold for a minimal user plugin skeleton. Replace `<path-to-this-skill>` with this skill directory path:

```bash
npx tsx <path-to-this-skill>/scripts/scaffold-user-channel-plugin.ts \
  my-channel "My Channel" \
  --runtime-package some-sdk@1.0.0 \
  --runtime-module some-sdk
```

It creates `channel.json`, `plugin.mjs`, and `accounts.example.json`. Replace the TODO inbound/outbound implementation with the real SDK calls.

## Hard lessons

- `MessageChannel` silently feels broken if `plugin.messageActions` is missing. Every plugin that should reply needs `describeMessageTool()` and `handleAction()`.
- For public channels, suppress tool approval/control prompts unless there is verified operator routing. Posting approval prompts publicly leaks tool input and invites forged `approve` replies.
- User plugin runtime resolution must not count parent/dev `node_modules`. Runtime modules should resolve from explicit runtime dirs only.
- Headless pairing is CLI-first: `letta channels pair --channel <id> --code <code> --agent <agent-id> --conversation <conversation-id>`.
- Running listeners reload `pairing.yaml` and `routing.yaml` on the next inbound miss; restart only when adapter/account config itself changed.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
