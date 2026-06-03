# @skill-library/python-sdk

> A typed Python client for the AI-SKILL REST API.
>
> Wraps every endpoint in the [OpenAPI spec](https://github.com/badhope/AI-SKILL/blob/main/openapi.json),
> gives you sessions, retry, and an `async`/`sync` pair.

[![PyPI](https://img.shields.io/pypi/v/skill-sdk)](https://pypi.org/project/skill-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/skill-sdk)](https://pypi.org/project/skill-sdk/)
[![License: MIT](https://img.shields.io/github/license/badhope/AI-SKILL)](https://github.com/badhope/AI-SKILL/blob/main/LICENSE)

[📖 API reference](https://badhope.github.io/AI-SKILL/sdks/python/)
[🐛 Issues](https://github.com/badhope/AI-SKILL/issues)
[💬 Discussions](https://github.com/badhope/AI-SKILL/discussions)

---

## What is this?

This is the official Python client for [AI-SKILL](https://github.com/badhope/AI-SKILL).
If you find yourself writing `requests.post(API + "/v1/skills/search", json=...)`
over and over, this package is for you. It exposes:

- A sync `SkillClient` and an async `AsyncSkillClient`.
- Typed responses (Pydantic v2 models, mirroring the OpenAPI schema).
- Token refresh, exponential backoff, and idempotency-key support.
- A `SkillLocal` mode that loads skills from a local directory — useful for
  tests and CI without spinning up the backend.

## Install

```bash
pip install skill-sdk
```

The package has only two runtime dependencies: `httpx` and `pydantic`. We
pin them loosely; any recent 0.x of httpx and 2.x of pydantic should work.

If you want the `async` client, `httpx` is already a dependency, so no
extras are needed.

## Quick start

```python
from skill_sdk import SkillClient

with SkillClient(base_url="http://localhost:8000") as client:
    client.login(email="you@example.com", password="hunter2")

    skills = client.skills.list(category="code_generation", limit=10)
    for s in skills:
        print(f"{s.name}  v{s.version}  ({s.rating:.1f}★)")

    # Hybrid search — weights default to 0.7 vector / 0.3 keyword,
    # override per-request if you need to A/B.
    hits = client.skills.search(q="summarize a long article", limit=5)
    for h in hits:
        print(f"{h.score:.2f}  {h.skill.name}")
```

`SkillClient` is a context manager — it'll close the underlying
connection pool on exit. For long-lived services, just instantiate it
once and reuse it.

### Async usage

```python
import asyncio
from skill_sdk import AsyncSkillClient

async def main():
    async with AsyncSkillClient(base_url="http://localhost:8000") as client:
        await client.login(email="you@example.com", password="hunter2")
        skills = await client.skills.list(limit=10)
        print(skills)

asyncio.run(main())
```

The async client is built on `httpx.AsyncClient`; you can share a single
instance across many concurrent tasks.

## Local mode (no backend)

For tests, agents running offline, or quick local exploration, you can
load skills straight from a folder:

```python
from skill_sdk import SkillLocal

lib = SkillLocal("./skills")  # each .md file is a skill
for skill in lib.list():
    print(skill.name, skill.version)
print(lib.search("summarize"))
```

`SkillLocal` reads the same frontmatter the backend validates, so what
you ship locally matches what the server stores. This is also the path
we use for our own CI; the SDK's test suite is mostly `SkillLocal` plus
recorded HTTP cassettes.

## Configuration

You can configure the client via env vars (handy in CI) or constructor
arguments (handy in tests):

| Env var                | Argument         | Default                |
|------------------------|------------------|------------------------|
| `SKILL_BASE_URL`       | `base_url`       | `http://localhost:8000`|
| `SKILL_API_KEY`        | `api_key`        | _(none)_               |
| `SKILL_TIMEOUT`        | `timeout`        | `30` (seconds)         |
| `SKILL_MAX_RETRIES`    | `max_retries`    | `3`                    |
| `SKILL_USER_AGENT`     | `user_agent`     | `skill-sdk/<version>`  |

Precedence is: argument > env var > default. `api_key`, if set, is
sent as a `Bearer` token and skips the email/password login.

## Common errors

- `SkillAuthError` — bad credentials or expired refresh token. Catch and
  re-prompt the user; do not retry blindly.
- `SkillNotFoundError` — usually a typo in the skill slug. The error
  includes a list of similar slugs from the server side.
- `SkillRateLimitError` — server-side rate limit hit. The exception
  carries a `retry_after` (seconds); the SDK will not auto-retry those.
- `SkillValidationError` — your request payload is rejected (missing
  field, bad enum, etc.). The exception has a `.details` list.

The full error hierarchy is in
[`skill_sdk.exceptions`](src/skill_sdk/exceptions.py).

## Compatibility

| AI-SKILL | skill-sdk |
|----------|-----------|
| 1.0.x    | 1.0.x     |
| 0.9.x    | 0.9.x     |

We follow the server's SemVer. The 1.x line of the SDK targets 1.x of
the server; the 0.9 line targets 0.9. Don't mix.

## Contributing

The SDK lives in the same monorepo as the server:
[badhope/AI-SKILL/sdk/python](https://github.com/badhope/AI-SKILL/tree/main/sdk/python).
Pull requests should:

1. Pass `make test` (pytest, including the HTTP-cassette suite).
2. Pass `make lint` (ruff + mypy strict).
3. Include a CHANGELOG entry under
   [sdk/python/CHANGELOG.md](CHANGELOG.md).

The OpenAPI schema is the source of truth: if you add an endpoint on
the server, regenerate the Pydantic models with `make codegen` before
opening the PR.

## License

MIT — see [LICENSE](https://github.com/badhope/AI-SKILL/blob/main/LICENSE).
