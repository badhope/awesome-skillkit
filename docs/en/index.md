# AI-SKILL

> A self-hostable library for AI agent skills — prompts, tool definitions,
> and small reusable workflows that you can search, version, and compose.
>
> We built it because we kept rewriting the same prompt glue on every project.
> We're sharing it so you don't have to.

[![License: MIT](https://img.shields.io/github/license/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/badhope/AI-SKILL/ci.yml?branch=main&label=build)](https://github.com/badhope/AI-SKILL/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/badhope/AI-SKILL?include_prereleases)](https://github.com/badhope/AI-SKILL/releases)
[![Issues](https://img.shields.io/github/issues/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/issues)

[📖 Source on GitHub](https://github.com/badhope/AI-SKILL) ·
[🚀 Quick start](getting-started/quickstart/) ·
[🧱 Architecture](architecture/) ·
[📦 Deployment](deployment/) ·
[🛠️ Operations](operations/) ·
[🤝 Contributing](community/contributing/)

---

## What is this?

AI-SKILL is a small web service + UI for storing **skills** — pieces of
prompt text, tool schemas, instructions for an agent — in a searchable
library. Think of it as a private Hugging Face for your team's prompt
toolbox.

A skill is just a Markdown file with YAML frontmatter:

```yaml
---
name: Summarize a URL
description: Fetches a URL and returns a 3-bullet summary.
tags: [summarization, web]
---

# Summarize a URL
…
```

You can publish it to the library, version it, tag it, declare dependencies
on other skills, and let your agents find it through a search bar or the
HTTP API.

## Why does it exist?

Most teams we know end up with the same problem: a Notion page of
"approved prompts" that no one updates, half of which are copy-pasted into
the wrong project. AI-SKILL is the boring version of that — git-tracked,
versioned, searchable, with a real API.

We're not trying to replace your agent framework. We're providing the
**shared library** part that most agent stacks are missing.

## Who is it for?

- **Individual developers** who want a single place to keep prompts they
  reuse across projects.
- **Small teams** that need a shared "approved" library of agent skills
  with a UI that non-engineers can browse.
- **Tool builders** who want a typed Python / TypeScript SDK for talking
  to a skill service instead of hand-rolling REST calls.

If you're a large enterprise looking for a commercial-grade prompt
management platform, this probably isn't it — there are vendors for that
(we list a few in [the FAQ](community/faq/#alternatives)).

## What's in the box {#architecture}

A self-hostable stack with a web UI, a REST API, and SDKs:

- Web UI for browsing, searching, and rating skills.
- REST API (OpenAPI-documented) for creating, versioning, and pulling
  skills programmatically.
- Hybrid search: vector (Sentence-BERT over Qdrant) + BM25 keyword, with
  weights you can tune per request.
- Semantic versioning per skill, with an audit trail of who changed what.
- Skill dependencies with cycle detection and semver constraints.
- Typed Python SDK and typed TypeScript SDK.
- JWT auth, role-based access, per-IP rate limiting, and an audit log.
- Docker Compose setup that boots the whole stack on one machine.

The architecture breakdown is in [architecture/](architecture/), and the
component decisions are recorded as ADRs under [adr/](adr/).

## Quick start

The fastest path is Docker:

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL
cp .env.example .env
docker compose up -d
```

| What          | Where                       |
|---------------|-----------------------------|
| Web UI        | http://localhost:3000       |
| Backend API   | http://localhost:8000       |
| API docs      | http://localhost:8000/docs  |
| ReDoc         | http://localhost:8000/redoc |

The first user you create becomes the admin. The full walk-through is in
[getting-started/quickstart/](getting-started/quickstart/). If you'd
rather go step-by-step, [installation](getting-started/installation/)
goes deeper.

## 5-minute tour

Once the stack is up, the shortest useful loop looks like this:

```python
from skill_sdk import SkillClient

client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="hunter2")

results = client.skills.search(q="summarize a long article", limit=5)
for r in results:
    print(f"{r.score:.2f}  {r.skill.name}")
```

```typescript
import { SkillClient } from "@skill-library/sdk";

const client = new SkillClient({ baseUrl: "http://localhost:8000" });
await client.login({ email: "you@example.com", password: "hunter2" });

const results = await client.skills.search({ q: "summarize a long article", limit: 5 });
for (const r of results) {
  console.log(`${r.score.toFixed(2)}  ${r.skill.name}`);
}
```

The same loop with raw HTTP is in
[examples/rest/skills.http](https://github.com/badhope/AI-SKILL/blob/main/examples/rest/skills.http).
A Postman collection is at
[examples/postman/](https://github.com/badhope/AI-SKILL/tree/main/examples/postman/).

## What works, what doesn't

The short version (the long version is in [the roadmap](community/roadmap/)):

**Works well in 1.0.0**

- Skill CRUD, versioning, dependencies, ratings.
- Hybrid search on catalogs up to a few thousand skills.
- Per-IP rate limiting with Redis (degrades gracefully if Redis is down).
- Per-request locale resolution and localized error messages (en / zh).
- Docker Compose for a single-host install.

**Still rough**

- Analytics dashboard is in-memory and per-process. Run more than one
  backend replica and the numbers will be inconsistent.
- No SSO, no team-level isolation.
- The TypeScript SDK's types are hand-rolled, not generated from OpenAPI.

## Where to look next

| If you want to …                                  | Go to                                       |
|---------------------------------------------------|---------------------------------------------|
| Get it running in 5 minutes                       | [Quick start](getting-started/quickstart/)  |
| Understand how the pieces fit                     | [Architecture](architecture/)               |
| Put it on a real server                           | [Deployment](deployment/)                   |
| Run it day-to-day (logs, backups, security)       | [Operations](operations/)                   |
| Read the SDK reference                             | [Python SDK](sdks/python/) · [TypeScript SDK](sdks/typescript/) |
| Find runnable code                                | [Examples](examples/)                       |
| See what we changed                               | [Changelog](community/changelog/)           |
| Report a bug or request a feature                 | [Issue tracker](https://github.com/badhope/AI-SKILL/issues) |
| Help translate the docs into another language     | [Contributing → translation](community/contributing/#translation) |

## Contributing

Contributions are welcome. Please skim
[community/contributing/](community/contributing/) first — it's short and
covers the branch naming, commit style, and the test commands we expect
to be green before a PR.

Good places to start:

- [`good first issue`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
  — small, well-scoped, and someone will review fast.
- Translations. The docs and the UI are bilingual (en / zh). Adding a new
  language is mostly a `docs/<locale>/` copy and a one-line change to
  `docs/mkdocs.yml`. See
  [Contributing → translation](community/contributing/#translation).
- Issues tagged
  [`help wanted`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
  for things we'd love a second pair of eyes on.

## License

MIT — see [LICENSE](https://github.com/badhope/AI-SKILL/blob/main/LICENSE).
