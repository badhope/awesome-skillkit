# AI-SKILL — TypeScript SDK examples

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
