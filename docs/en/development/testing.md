# Testing

The test suite is split into three layers. Each layer has a
different scope and runs at a different point in the CI pipeline.

## Layer 1 — Unit tests

Pure functions, no I/O. Fast, hermetic, run on every PR.

```bash
cd backend && poetry run pytest tests/unit
cd frontend && npm test
cd sdk/python && poetry run pytest
cd sdk/typescript && npm test
```

**Backend convention**: name the file `test_<module>.py` and put it
under `tests/unit/`. Use `pytest-asyncio` for `async def` tests.

**Frontend convention**: name the file `<Component>.test.tsx` and
co-locate it with the component.

**SDK convention**: name the file `test_<module>.py` / `.test.ts` in
the SDK's `tests/` directory.

## Layer 2 — Integration tests

Exercise a slice of the system through real services. Slower, need
Postgres + Redis + Qdrant.

```bash
cd backend && poetry run pytest tests/integration
```

**Setup**: the CI workflow spins up Postgres, Redis, and Qdrant as
service containers. Locally, you can either:

- Run the same services with `docker compose up -d postgres redis
  qdrant` and then `pytest tests/integration`
- Use the `tests/docker-compose.yml` helper that scopes the ports

**Fixtures**: shared fixtures live in `tests/conftest.py`. They
create a clean schema per test (via Alembic), a transactional
session, and a test client.

## Layer 3 — End-to-end tests

Exercise the whole stack. The slowest, run only on the main branch
and release tags.

For now, the E2E suite is a small set of smoke tests:

```bash
# In CI: bring up the stack, run the smoke tests, tear down
make health-check
make test-e2e
```

## Coverage

Coverage is generated per layer:

```bash
make test-coverage
```

The output is:

- `backend/coverage.xml` — Cobertura XML, uploaded to Codecov
- `frontend/coverage/` — HTML report

Coverage is a *signal*, not a *goal*. The CI workflow fails the
build if coverage drops by more than 1% in a PR.

## Conventions

### Backend

- One assertion concept per test
- Use `pytest.mark.asyncio` for `async def` tests
- Use `pytest.raises(ExpectedException)` for error-path tests
- Avoid `time.sleep`; use `freezegun` for time travel, `httpx.MockTransport`
  for HTTP mocking
- Use factories (`factory_boy`) for model creation, not hand-built
  dicts

### Frontend

- Use `@testing-library/react` (not `enzyme`)
- Test behaviour, not implementation details
- Mock network calls with `msw`
- One render per test
- Use `findBy*` for async, `getBy*` for sync

### SDKs

- Mock the HTTP transport (use `httpx.MockTransport` in Python,
  `msw` in TypeScript)
- Cover both the happy path and every error code

## Running a single test

```bash
# Backend
cd backend && poetry run pytest tests/unit/test_skill.py::test_create

# Frontend
cd frontend && npm test -- SkillCard

# Python SDK
cd sdk/python && poetry run pytest skill_sdk/test_client.py

# TypeScript SDK
cd sdk/typescript && npm test -- SkillClient
```

## Where to go from here

- [Adding an API endpoint](adding-endpoint.md) — has example tests
- [Adding a frontend page](adding-page.md) — has example tests
- [Release process](release.md) — what tests must pass before a
  release
