# AI-SKILL — Frequently Asked Questions

General questions live here. For a structured troubleshooting page,
see [docs/troubleshooting.md](docs/troubleshooting.md).

---

## What is AI-SKILL?

AI-SKILL is a self-hostable platform for cataloging, discovering, and
composing **AI agent skills** — modular units of capability that an
LLM-based agent can use. A skill is roughly equivalent to a
"plugin" or "tool" in other ecosystems.

The platform ships with a search engine, an analytics dashboard, a
rating system, and a composition builder.

## Why another skill library?

Most existing "skill" or "agent" libraries are:

- **Tied to a single vendor** (Anthropic, OpenAI, Microsoft) — the
  skills cannot be used elsewhere.
- **Closed-source** — you cannot inspect, audit, or extend them.
- **Single-language** — most are Python-only, which locks out
  TypeScript and Go teams.

AI-SKILL is **vendor-neutral**, **open-source**, and **multi-language**.

## Does it include a corpus of skills out of the box?

**No.** A fresh install ships with an empty catalog. The platform is
production-ready; the dataset is intentionally not bundled, so you
control what goes in.

You can populate the library by:

- **Authoring** skills through the web UI
- **Importing** a `skill-pack.zip` from a community registry
- **Programmatically** posting to `POST /api/v1/skills`

## How does it compare to LangChain / LlamaIndex / Hugging Face?

Different scopes:

| System         | What it is                                                |
|----------------|-----------------------------------------------------------|
| LangChain      | Framework to write agents in Python/JS                    |
| LlamaIndex     | Framework for RAG and data connectors                     |
| Hugging Face   | Model + dataset hub + inference API                       |
| **AI-SKILL**   | **A catalog + composition tool for skills you have built**|

AI-SKILL is a complement, not a competitor. You can use LangChain to
*write* skills and AI-SKILL to *catalog* them.

## What model does it use for embeddings?

By default, [`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
(768-dim). The model is configurable via the `EMBEDDING_MODEL` env
var. Other good options:

- `sentence-transformers/all-MiniLM-L6-v2` (384-dim, faster)
- `BAAI/bge-large-en-v1.5` (1024-dim, higher quality)
- `intfloat/multilingual-e5-large` (multilingual)

If you change the model, you must **reindex** the Qdrant collection.

## Can I run it without Qdrant?

Yes — set `QDRANT_URL=""` and the backend will fall back to a
Postgres-only lexical (BM25 / ILIKE) retriever. Search quality is
lower, but the stack is simpler to operate.

## Is the platform production-ready?

The current release is **feature-complete for the documented scope**
and ships with:

- Input validation
- Auth + RBAC
- Rate limiting
- Audit logging
- OWASP security headers
- Fail-fast secret validation
- A `make health-check` target
- Backups documented

It has not been battle-tested at the scale of a billion rows. If
you find a bottleneck, open an issue.

## What license?

[MIT](../LICENSE). Use it, fork it, sell it, no strings attached.

## How do I contribute?

Read [CONTRIBUTING.md](../CONTRIBUTING.md). The short version:

1. Fork + branch
2. Make your change with tests
3. `make lint && make typecheck && make test`
4. Open a PR

## I found a security issue. What now?

**Do not open a public issue.** Follow
[SECURITY.md](../SECURITY.md) — email the security contact or use
GitHub's [private advisory](../../security/advisories/new) form.

## How do I get help?

- [GitHub Discussions / Q&A](../../discussions/categories/q-a) for
  general questions
- [GitHub Issues](../../issues) for bugs and feature requests
- The in-app help icon (top-right of the dashboard) for guided tours
