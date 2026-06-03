TypeScript / JavaScript SDK providing a typed interface to interact with the AI-SKILL API.

## Installation

```bash
npm install @skill-library/sdk
# or
yarn add @skill-library/sdk
# or
pnpm add @skill-library/sdk
```

## Quick Start

```typescript
import { SkillLibraryClient, SkillNotFoundError, AuthenticationError } from "@skill-library/sdk";

const client = new SkillLibraryClient({
  baseUrl: "https://api.skills.example.com",
  apiKey: "your-api-key",
  timeout: 30_000,
});

// Authentication
const token = await client.auth.login({ username: "user", password: "pass" });
// or
client.setToken("your-jwt-token");

// List skills
const result = await client.skills.list({
  categorySlug: "programming",
  search: "python",
  page: 1,
  pageSize: 20,
});
console.log(`Found ${result.total} skills`);
for (const skill of result.items) {
  console.log(`  - ${skill.name} (v${skill.version})`);
}

// Semantic search
const search = await client.skills.search({ q: "machine learning", limit: 10 });
for (const r of search) {
  console.log(`  - ${r.name} (score: ${r.score.toFixed(2)})`);
}

// Get a single skill
const skill = await client.skills.get("my-awesome-skill");
console.log(`${skill.name}: ${skill.description}`);

// Create a skill
const newSkill = await client.skills.create({
  name: "My New Skill",
  slug: "my-new-skill",
  description: "A powerful new skill",
  version: "1.0.0",
  categorySlug: "programming",
  tags: ["typescript", "ai"],
  content: { prompt: "You are a helpful assistant..." },
});

// Update a skill
await client.skills.update("my-new-skill", {
  description: "Updated description",
  version: "1.1.0",
});

// Featured / popular / trending
const featured = await client.skills.getFeatured(5);
const popular = await client.skills.getPopular(5);
const trending = await client.skills.getTrending(5);

// Versions
const versions = await client.skills.getVersions("my-skill");
await client.skills.createVersion("my-skill", {
  version: "1.2.0",
  content: { prompt: "Updated prompt" },
  changelog: "Improved accuracy by 20%",
});

// Dependencies
const deps = await client.skills.getDependencies("my-skill");
await client.skills.addDependency("my-skill", {
  dependsOnSkillSlug: "base-skill",
  versionConstraint: ">=1.0",
});
await client.skills.removeDependency("my-skill", { depId: "..." });

// Similar skills
const similar = await client.skills.getSimilar("my-skill", 5);

// Rating
await client.skills.rate("my-skill", { rating: 4, comment: "Great skill!" });

// Usage tracking
await client.skills.logUsage("my-skill", { action: "download" });

// Categories
const categories = await client.categories.list();
const tree = await client.categories.tree();

// Tags
const tags = await client.tags.popular(20);

// Analytics
const dashboard = await client.analytics.dashboard();
const trends = await client.analytics.skillUsage(30);

// Compositions
const compositions = await client.compositions.list();
const composition = await client.compositions.create({
  name: "My Workflow",
  slug: "my-workflow",
  description: "A composed workflow",
});

// Delete
await client.skills.delete("my-new-skill");
```

## Error Handling

```typescript
import {
  SkillLibraryClient,
  SkillNotFoundError,
  AuthenticationError,
  PermissionDeniedError,
  RateLimitError,
  ValidationError,
  APIError,
  ConnectionError,
} from "@skill-library/sdk";

const client = new SkillLibraryClient({ baseUrl: "https://api.skills.example.com" });

try {
  const skill = await client.skills.get("non-existent-skill");
} catch (err) {
  if (err instanceof SkillNotFoundError) {
    console.log(`Skill not found: ${err.message}`);
  } else if (err instanceof AuthenticationError) {
    console.log(`Auth failed: ${err.message}`);
  } else if (err instanceof RateLimitError) {
    console.log(`Rate limited, retry after ${err.retryAfter}s`);
  } else if (err instanceof ValidationError) {
    console.log(`Invalid data: ${err.message}`);
  } else if (err instanceof PermissionDeniedError) {
    console.log(`Forbidden: ${err.message}`);
  } else if (err instanceof ConnectionError) {
    console.log(`Connection failed: ${err.message}`);
  } else if (err instanceof APIError) {
    console.log(`API error (${err.statusCode}): ${err.message}`);
  } else {
    throw err;
  }
}
```

## Configuration

The client accepts the following `ClientConfig` options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `baseUrl` | `string` | `http://localhost:8000` | Base URL of the AI-SKILL API |
| `apiKey` | `string` | — | API key for authentication |
| `token` | `string` | — | JWT access token (alternative to `apiKey`) |
| `timeout` | `number` (ms) | `30000` | Per-request timeout |
| `maxRetries` | `number` | `3` | Max retry attempts for transient failures |
| `retryDelay` | `number` (ms) | `1000` | Initial backoff (exponential) |
| `headers` | `Record<string,string>` | `{}` | Extra headers to send with every request |

## Building

```bash
npm install
npm run build
```

This produces `dist/index.js` (CJS), `dist/index.mjs` (ESM) and `dist/index.d.ts` (types) using `tsup`.

## License

MIT
