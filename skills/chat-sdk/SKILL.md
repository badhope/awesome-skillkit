---
name: chat-sdk
name_zh: chat-sdk
description: 'Build multi-platform chat bots with the chat SDK. Use for Slack, Teams,'
description_zh: '构建 multi-platform chat bots with the chat SDK. Use for Slack, Teams,'
category: chat-uikits
tags:
  - ai
  - api
  - backend
  - cli
  - deployment
source: null
needs_review: false
slug: chat-sdk
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

Use this skill when you need to work with chat-sdk.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# Chat SDK

Unified TypeScript SDK for building chat bots across Slack, Teams, Google Chat, Discord, GitHub, and Linear. Write bot logic once, deploy everywhere.

## Critical: Read the bundled docs

The `chat` package ships with full documentation in `node_modules/chat/docs/` and TypeScript source types. **Always read these before writing code:**

```
node_modules/chat/docs/           # Full documentation (MDX files)
node_modules/chat/dist/           # Built types (.d.ts files)
```

Key docs to read based on task:

- `docs/getting-started.mdx` — setup guides
- `docs/usage.mdx` — event handlers, threads, messages, channels
- `docs/streaming.mdx` — AI streaming with AI SDK
- `docs/cards.mdx` — JSX interactive cards
- `docs/actions.mdx` — button/dropdown handlers
- `docs/modals.mdx` — form dialogs (Slack only)
- `docs/adapters/*.mdx` — platform-specific adapter setup
- `docs/state/*.mdx` — state adapter config (Redis, ioredis, memory)

Also read the TypeScript types from `node_modules/chat/dist/` to understand the full API surface.

## Quick start

```typescript
import { Chat } from 'chat';
import { createSlackAdapter } from '@chat-adapter/slack';
import { createRedisState } from '@chat-adapter/state-redis';

const bot = new Chat({
  userName: 'mybot',
  adapters: {
    slack: createSlackAdapter({
      botToken: process.env.SLACK_BOT_TOKEN!,
      signingSecret: process.env.SLACK_SIGNING_SECRET!,
    }),
  },
  state: createRedisState({ url: process.env.REDIS_URL! }),
});

bot.onNewMention(async (thread) => {
  await thread.subscribe();
  await thread.post("Hello! I'm listening to this thread.");
});

bot.onSubscribedMessage(async (thread, message) => {
  await thread.post(`You said: ${message.text}`);
});
```

## Core concepts

- **Chat** — main entry point, coordinates adapters and routes events
- **Adapters** — platform-specific (Slack, Teams, GChat, Discord, GitHub, Linear)
- **State** — pluggable persistence (Redis for prod, memory for dev)
- **Thread** — conversation thread with `post()`, `subscribe()`, `startTyping()`
- **Message** — normalized format with `text`, `formatted` (mdast AST), `raw`
- **Channel** — container for threads, supports listing and posting

## Event handlers

| Handler                    | Trigger                                           |
| -------------------------- | ------------------------------------------------- |
| `onNewMention`             | Bot @-mentioned in unsubscribed thread            |
| `onSubscribedMessage`      | Any message in subscribed thread                  |
| `onNewMessage(regex)`      | Messages matching pattern in unsubscribed threads |
| `onSlashCommand("/cmd")`   | Slash command invocations                         |
| `onReaction(emojis)`       | Emoji reactions added/removed                     |
| `onAction(actionId)`       | Button clicks and dropdown selections             |
| `onAssistantThreadStarted` | Slack Assistants API thread opened                |
| `onAppHomeOpened`          | Slack App Home tab opened                         |

## Streaming

Pass any `AsyncIterable<string>` to `thread.post()`. Works with AI SDK's `textStream`:

```typescript
import { ToolLoopAgent } from 'ai';
const agent = new ToolLoopAgent({ model: 'anthropic/claude-4.5-sonnet' });

bot.onNewMention(async (thread, message) => {
  const result = await agent.stream({ prompt: message.text });
  await thread.post(result.textStream);
});
```

## Cards (JSX)

Set `jsxImportSource: "chat"` in tsconfig. Components: `Card`, `CardText`, `Button`, `Actions`, `Fields`, `Field`, `Select`, `SelectOption`, `Image`, `Divider`, `LinkButton`, `Section`, `RadioSelect`.

```tsx
await thread.post(
  <Card title="Order #1234">
    <CardText>Your order has been received!</CardText>
    <Actions>
      <Button id="approve" style="primary">
        Approve
      </Button>
      <Button id="reject" style="danger">
        Reject
      </Button>
    </Actions>
  </Card>,
);
```

## Packages

| Package                       | Purpose                       |
| ----------------------------- | ----------------------------- |
| `chat`                        | Core SDK                      |
| `@chat-adapter/slack`         | Slack                         |
| `@chat-adapter/teams`         | Microsoft Teams               |
| `@chat-adapter/gchat`         | Google Chat                   |
| `@chat-adapter/discord`       | Discord                       |
| `@chat-adapter/github`        | GitHub Issues                 |
| `@chat-adapter/linear`        | Linear Issues                 |
| `@chat-adapter/state-redis`   | Redis state (production)      |
| `@chat-adapter/state-ioredis` | ioredis state (alternative)   |
| `@chat-adapter/state-memory`  | In-memory state (development) |

## Changesets (Release Flow)

This monorepo uses [Changesets](https://github.com/changesets/changesets) for versioning and changelogs. Every PR that changes a package's behavior must include a changeset.

```bash
pnpm changeset
# → select affected package(s) (e.g. @chat-adapter/slack, chat)
# → choose bump type: patch (fixes), minor (features), major (breaking)
# → write a short summary for the CHANGELOG
```

This creates a file in `.changeset/` — commit it with the PR. When merged to `main`, the Changesets GitHub Action opens a "Version Packages" PR to bump versions and update CHANGELOGs. Merging that PR publishes to npm.

## Webhook setup

Each adapter exposes a webhook handler via `bot.webhooks.{platform}`. Wire these to your HTTP framework's routes (e.g. Next.js API routes, Hono, Express).

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 chat-sdk 技能
skill = load_skill("chat-sdk")
result = skill.execute()
print(result)
```

