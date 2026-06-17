---
name: debug-package
name_zh:
description: 'LobeHub debug package and log namespace guide. Use when adding debug()
  logging, choosing lobe-* namespaces, troubleshooting DEBUG output, localStorage.debug,
  or log format specifiers.'
description_zh:
category: dev-tools
tags:
  - backend
  - cli
  - frontend
  - javascript
  - typescript
needs_review: false
source:
slug: debug-package
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

Use this skill when you need guidance on debug-package.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Debug Package Usage Guide

## Basic Usage

```typescript
import debug from 'debug';

// Format: lobe-[module]:[submodule]
const log = debug('lobe-server:market');

log('Simple message');
log('With variable: %O', object);
log('Formatted number: %d', number);
```

## Namespace Conventions

- Desktop: `lobe-desktop:[module]`
- Server: `lobe-server:[module]`
- Client: `lobe-client:[module]`
- Router: `lobe-[type]-router:[module]`

## Format Specifiers

- `%O` - Object expanded (recommended for complex objects)
- `%o` - Object
- `%s` - String
- `%d` - Number

## Enable Debug Output

### Browser

```javascript
localStorage.debug = 'lobe-*';
```

### Node.js

```bash
DEBUG=lobe-* npm run dev
DEBUG=lobe-* pnpm dev
```

### Electron

```typescript
process.env.DEBUG = 'lobe-*';
```

## Example

```typescript
// apps/server/src/routers/edge/market/index.ts
import debug from 'debug';

const log = debug('lobe-edge-router:market');

log('getAgent input: %O', input);
```

# Example

```typescript
// apps/server/src/services/agent.ts
import debug from 'debug';

const log = debug('lobe-server:agent');
const logError = debug('lobe-server:agent:error');

export async function createAgent(params: AgentParams) {
  log('Creating agent with params: %O', params);

  try {
    const agent = await agentService.create(params);
    log('Agent created successfully: %s', agent.id);
    return agent;
  } catch (err) {
    logError('Failed to create agent: %O', err);
    throw err;
  }
}
```

Enable output in development:

```bash
# Node.js
DEBUG=lobe-server:* npm run dev

# Browser console
localStorage.debug = 'lobe-server:*';
```

# When NOT to use

Do not use this skill for tasks outside its scope.
