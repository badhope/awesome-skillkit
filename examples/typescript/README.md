# AI-SKILL — TypeScript SDK examples

Runnable scripts (Node 18+, Bun, Deno) that show how to drive the
AI-SKILL REST API from TypeScript. Each file is self-contained — pick
the one closest to what you're trying to do and copy the bits you need.

## Before you start

Make sure the backend is running locally (or point `SKILL_BASE_URL`
at a deployed instance). The default is `http://localhost:8000`.

## Install

```bash
npm install @ai-skill/sdk
# or, from source:
cd sdk/typescript && npm install && npm run build && npm link
cd ../../frontend && npm link @ai-skill/sdk
```

## Configure

The SDK reads the following environment variables:

| Variable           | Default                          | Purpose           |
|--------------------|----------------------------------|-------------------|
| `SKILL_BASE_URL`   | `http://localhost:8000`          | API base URL      |
| `SKILL_API_KEY`    | (unset)                          | Optional API key  |

Or pass them to the constructor.

## Files

| File                  | Purpose                            |
|-----------------------|------------------------------------|
| `auth.ts`             | Register, login, refresh, logout  |
| `search.ts`           | Semantic search                    |
| `createSkill.ts`      | POST a new skill                   |
| `paginatedList.ts`    | Walk the full catalog              |

## Usage

```typescript
import { SkillClient } from '@ai-skill/sdk';

const client = new SkillClient({ baseUrl: 'http://localhost:8000' });
await client.login({ email: 'you@example.com', password: 'hunter2' });
for await (const skill of client.iterSkills({ pageSize: 20, isPublic: true })) {
  console.log(skill.name);
}
```

See the per-file examples for the long form.
