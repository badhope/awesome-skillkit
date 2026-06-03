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
[![PRs](https://img.shields.io/github/issues-pr/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/pulls)
[📖 Docs](https://badhope.github.io/AI-SKILL/) ·
[🚀 Quick start](#quick-start) ·
[🧱 Architecture](docs/en/architecture.md) ·
[📦 Deployment](docs/en/deployment.md) ·
[❓ FAQ](FAQ.md) ·
[🛠️ Troubleshooting](TROUBLESHOOTING.md) ·
[🗺️ Roadmap](ROADMAP.md)

[English](./README.md) · [简体中文](./README.zh.md)

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
(we list a few in [the FAQ](FAQ.md#alternatives)).

## What you get

A self-hostable stack with a web UI, a REST API, and SDKs. Nothing more
than what's listed in [docs/en/architecture.md](docs/en/architecture.md).

- A web UI for browsing, searching, and rating skills.
- A REST API (OpenAPI-documented) for creating, versioning, and pulling
  skills programmatically.
- Hybrid search: vector (Sentence-BERT over Qdrant) + BM25 keyword, with
  weights you can tune per request.
- Semantic versioning per skill, with an audit trail of who changed what.
- Skill dependencies with cycle detection and semver constraints.
- A typed Python SDK and a typed TypeScript SDK.
- JWT auth, role-based access, per-IP rate limiting, and an audit log.
- A Docker Compose setup that boots the whole stack on one machine.

## Quick start

The fastest path is Docker:

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL
cp .env.example .env
docker compose up -d
```

Then:

| What          | Where                                    |
|---------------|------------------------------------------|
| Web UI        | http://localhost:3000                    |
| Backend API   | http://localhost:8000                    |
| API docs      | http://localhost:8000/docs               |
| ReDoc         | http://localhost:8000/redoc              |

The first user you create becomes the admin. See
[docs/en/deployment.md → first admin](docs/en/deployment.md#first-admin) for the
CLI bootstrap if you'd rather not click through the signup form.

If you want to run it without Docker, the manual setup is in
[docs/en/development.md → manual install](docs/en/development.md#manual-install).
You need Python 3.12+, Node 20+, PostgreSQL 16+, and Redis 7+. Qdrant is
optional for local dev — there's an in-memory fallback.

## 5-minute tour

Once the stack is up, the shortest useful loop looks like this:

```python
# Python SDK
from skill_sdk import SkillClient

client = SkillClient(base_url="http://localhost:8000")
client.login(email="you@example.com", password="hunter2")

# Find skills by meaning, not just by exact name
results = client.skills.search(q="summarize a long article", limit=5)
for r in results:
    print(f"{r.score:.2f}  {r.skill.name}")
```

```typescript
// TypeScript SDK
import { SkillClient } from "@skill-library/sdk";

const client = new SkillClient({ baseUrl: "http://localhost:8000" });
await client.login({ email: "you@example.com", password: "hunter2" });

const results = await client.skills.search({ q: "summarize a long article", limit: 5 });
for (const r of results) {
  console.log(`${r.score.toFixed(2)}  ${r.skill.name}`);
}
```

The same loop with raw HTTP is in
[examples/rest/skills.http](examples/rest/skills.http). A Postman
collection is at [examples/postman/](examples/postman/).

## What works, what doesn't

We try to keep this honest in [the roadmap](ROADMAP.md), but the short
version:

**Works well in 1.0.0**

- Skill CRUD, versioning, dependencies, ratings.
- Hybrid search on catalogs up to a few thousand skills.
- Per-IP rate limiting with Redis (degrades gracefully if Redis is down).
- Per-request locale resolution and localized error messages (en / zh).
- Docker Compose for a single-host install.

**Still rough**

- The analytics dashboard is in-memory and per-process. Run more than one
  backend replica and the numbers will be inconsistent. See
  [ROADMAP § 1.1.0](ROADMAP.md#110).
- No SSO, no team-level isolation. If you need either, see the alternatives
  in the [FAQ](FAQ.md#alternatives).
- The TypeScript SDK's types are hand-rolled, not generated from the
  OpenAPI schema. There's a [tracking issue](https://github.com/badhope/AI-SKILL/issues)
  for switching to a generated client.

## Contributing

Contributions are welcome. Please skim
[CONTRIBUTING.md](CONTRIBUTING.md) first — it's short and covers the
branch naming, commit style, and the test commands we expect to be green
before a PR.

Good places to start:

- [`good first issue`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) —
  small, well-scoped, and someone will review fast.
- Translations. The docs and the UI are bilingual (en / zh). Adding a new
  language is mostly a `docs/<locale>/` copy and a one-line change to
  `docs/mkdocs.yml`. See [CONTRIBUTING → translation](CONTRIBUTING.md#translation).
- Issues tagged
  [`help wanted`](https://github.com/badhope/AI-SKILL/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
  for things we'd love a second pair of eyes on.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- The search stack leans heavily on [Qdrant](https://qdrant.tech/) and
  [Sentence-Transformers](https://www.sbert.net/). Both have been a joy to
  integrate.
- The web UI is built on [Next.js](https://nextjs.org/) and
  [shadcn/ui](https://ui.shadcn.com/).
- The backend is on [FastAPI](https://fastapi.tiangolo.com/) and
  [SQLAlchemy 2](https://www.sqlalchemy.org/).

If you ship something with this, we'd love to hear about it. Open a
[Show and Tell discussion](https://github.com/badhope/AI-SKILL/discussions/categories/show-and-tell)
or a PR adding your project to the wiki.
