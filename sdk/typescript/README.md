# @skill-library/typescript-sdk

> A typed TypeScript client for the AI-SKILL REST API.
>
> Wraps every endpoint in the [OpenAPI spec](https://github.com/badhope/AI-SKILL/blob/main/openapi.json),
> gives you sessions, retry, and a Promise-based API.

[![npm](https://img.shields.io/npm/v/@skill-library/sdk)](https://www.npmjs.com/package/@skill-library/sdk)
[![License: MIT](https://img.shields.io/github/license/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/blob/main/LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org/)

[📖 API reference](https://badhope.github.io/AI-SKILL/sdks/typescript/)
[🐛 Issues](https://github.com/badhope/AI-SKILL/issues)
[💬 Discussions](https://github.com/badhope/AI-SKILL/discussions)

---

## What is this?

This is the official TypeScript client for [AI-SKILL](https://github.com/badhope/AI-SKILL).
If you're calling `fetch(API + "/v1/skills/search", ...)` by hand in a
Next.js / Node / Bun app, this package is for you. It exposes:

- A Promise-based `SkillClient` (works in Node 18+, Bun, and modern
  browsers).
- Typed request/response types mirroring the OpenAPI schema.
- Automatic token refresh, exponential backoff, and idempotency keys.
- A `SkillLocal` reader that loads skills from a folder — useful for
  tests and CI without a backend.

## Install

```bash
# npm
npm install @skill-library/sdk

# pnpm
pnpm add @skill-library/sdk

# yarn
yarn add @skill-library/sdk
```

The package has zero runtime dependencies. The HTTP layer is built on
the platform-native `fetch`, so the bundle stays small and there's no
`node-fetch` polyfill drama in older bundlers.

## Quick start

```typescript
import { SkillClient } from "@skill-library/sdk";

const client = new SkillClient({ baseUrl: "http://localhost:8000" });
await client.login({ email: "you@example.com", password: "hunter2" });

const skills = await client.skills.list({ category: "code_generation", limit: 10 });
for (const s of skills) {
  console.log(`${s.name}  v${s.version}  (${s.rating.toFixed(1)}★)`);
}

// Hybrid search — weights default to 0.7 vector / 0.3 keyword,
// override per-request if you need to A/B.
const hits = await client.skills.search({ q: "summarize a long article", limit: 5 });
for (const h of hits) {
  console.log(`${h.score.toFixed(2)}  ${h.skill.name}`);
}
```

A single `SkillClient` instance is meant to be shared. The class
internally pools connections and serializes refresh-token calls, so you
can hand it around without worrying about race conditions.

## Browser usage

```typescript
import { SkillClient } from "@skill-library/sdk";

const client = new SkillClient({
  baseUrl: "https://api.example.com",
  // In the browser, set `credentials: "include"` to send cookies for
  // session auth. The default is `"same-origin"`.
  credentials: "include",
});

const skills = await client.skills.list({ limit: 5 });
```

If you embed the SDK in a public web app, please set up CORS on the
server side; see [docs/operations/cors.md](https://badhope.github.io/AI-SKILL/operations/cors/).

## Local mode (no backend)

For tests, agents running offline, or quick local exploration, load
skills straight from a folder:

```typescript
import { SkillLocal } from "@skill-library/sdk";

const lib = new SkillLocal("./skills"); // each .md file is a skill
for (const skill of await lib.list()) {
  console.log(skill.name, skill.version);
}
console.log(await lib.search("summarize"));
```

`SkillLocal` reads the same frontmatter the backend validates, so what
you ship locally matches what the server stores. The SDK's own test
suite is mostly `SkillLocal` plus recorded HTTP cassettes.

## Configuration

You can configure the client via env vars (handy in CI / Vite / Next.js
runtime configs) or constructor arguments:

| Env var                | Argument         | Default                |
|------------------------|------------------|------------------------|
| `SKILL_BASE_URL`       | `baseUrl`        | `http://localhost:8000`|
| `SKILL_API_KEY`        | `apiKey`         | _(none)_               |
| `SKILL_TIMEOUT`        | `timeout`        | `30000` (ms)           |
| `SKILL_MAX_RETRIES`    | `maxRetries`     | `3`                    |
| `SKILL_USER_AGENT`     | `userAgent`      | `@skill-library/sdk/<v>`|

Precedence is: argument > env var > default. `apiKey`, if set, is sent
as a `Bearer` token and skips the email/password login.

## Common errors

- `SkillAuthError` — bad credentials or expired refresh token. Catch
  and re-prompt the user; do not retry blindly.
- `SkillNotFoundError` — usually a typo in the skill slug. The error
  includes a list of similar slugs from the server side.
- `SkillRateLimitError` — server-side rate limit hit. The error carries
  a `retryAfter` (ms); the SDK will not auto-retry those.
- `SkillValidationError` — your request payload is rejected (missing
  field, bad enum, etc.). The error has a `details` array.

The full error hierarchy is in
[`@skill-library/sdk/errors`](src/errors.ts).

## Compatibility

| AI-SKILL | @skill-library/sdk |
|----------|--------------------|
| 1.0.x    | 1.0.x              |
| 0.9.x    | 0.9.x              |

We follow the server's SemVer. The 1.x line targets 1.x of the server,
the 0.9 line targets 0.9. Don't mix.

A note on the types: they're currently hand-rolled from the OpenAPI
schema. There's a [tracking issue](https://github.com/badhope/AI-SKILL/issues)
to switch to generated types via `openapi-typescript`. If you find a
type mismatch, please open a PR — the bar is low.

## Contributing

The SDK lives in the same monorepo as the server:
[badhope/AI-SKILL/sdk/typescript](https://github.com/badhope/AI-SKILL/tree/main/sdk/typescript).
Pull requests should:

1. Pass `pnpm test` (vitest, including the HTTP-cassette suite).
2. Pass `pnpm lint` (eslint + tsc --noEmit).
3. Include a CHANGELOG entry under
   [sdk/typescript/CHANGELOG.md](CHANGELOG.md).

The OpenAPI schema is the source of truth: if you add an endpoint on
the server, regenerate the types with `pnpm codegen` before opening
the PR.

## License

MIT — see [LICENSE](https://github.com/badhope/AI-SKILL/blob/main/LICENSE).
