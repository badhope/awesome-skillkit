# AI-SKILL — Development Guide

This page is for contributors who want to extend AI-SKILL. It covers
the local workflow, conventions, and how to test your changes before
opening a pull request.

If you are new to the project, also read
[Contributing](community/contributing.md) and the
[architecture document](architecture.md).

---

## 1. Local setup

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

# One-shot bootstrap (installs deps, generates secrets, installs hooks)
make first-run

# Start the stack
make dev
```

Verify:

```bash
curl -sf http://localhost:8000/health
open http://localhost:3000
```

---

## 2. Project layout

```
AI-SKILL/
├── backend/              FastAPI service
├── frontend/             Next.js 15 PWA
├── sdk/
│   ├── python/           Python client
│   └── typescript/       TypeScript client
├── docs/                 Architecture, deployment, troubleshooting
├── examples/             API + SDK usage examples
├── scripts/              Operational scripts
├── .github/              Issue templates, PR template, CI, CODEOWNERS
└── Makefile              Common commands
```

---

## 3. Conventions

### 3.1 Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

| Type        | When                                                  |
|-------------|-------------------------------------------------------|
| `feat`      | New feature                                           |
| `fix`       | Bug fix                                               |
| `docs`      | Documentation only                                    |
| `refactor`  | No behavior change                                    |
| `perf`      | Performance improvement                               |
| `test`      | Adding or fixing tests                                |
| `build`     | Build system, CI, dependencies                        |
| `chore`     | Tooling, config, no production code change            |
| `security`  | Vulnerability fix or hardening                         |

Example:

```
feat(skills): add PATCH /skills/{slug}/metadata endpoint

* Replaces two PUT calls with one for incremental metadata updates
* Backwards compatible — existing PUT path still works
* Adds integration test in tests/integration/test_skills_api.py

Closes #142
```

### 3.2 Branch naming

`<type>/<short-kebab-case-description>`

Examples:
- `feat/composition-graph`
- `fix/auth-refresh-loop`
- `docs/add-architecture-diagram`

### 3.3 Python style

- **Formatter**: `ruff format` (100 cols)
- **Linter**: `ruff check` (rules: E, F, I, B, UP, N, SIM, C4, RET, TCH)
- **Type checker**: `mypy` in `--ignore-missing-imports` mode

Before pushing:

```bash
cd backend
poetry run ruff format app/ tests/
poetry run ruff check --fix app/ tests/
poetry run mypy app/ --ignore-missing-imports
poetry run pytest
```

### 3.4 TypeScript style

- **Formatter**: `prettier` (100 cols, single quotes, trailing commas)
- **Linter**: `eslint` with `eslint-config-next`
- **Type checker**: `tsc --noEmit`

Before pushing:

```bash
cd frontend
npm run lint
npm run typecheck
npm test
```

---

## 4. Adding a new API endpoint

This is a worked example. Suppose we want to add
`GET /api/v1/skills/{slug}/history`.

1. **Schema** — add a Pydantic response model in
   `backend/app/schemas/skill.py`:

   ```python
   class SkillHistoryEntry(BaseModel):
       version: str
       changelog: str
       created_at: datetime
   ```

2. **Service** — implement the data access in
   `backend/app/services/skill_history.py`:

   ```python
   async def get_history(db: AsyncSession, slug: str) -> list[SkillHistoryEntry]:
       ...
   ```

3. **Router** — add the endpoint in
   `backend/app/api/v1/skills.py`:

   ```python
   @router.get("/{slug}/history", response_model=list[SkillHistoryEntry])
   async def get_skill_history(slug: str, db: AsyncSession = Depends(get_db)):
       return await get_history(db, slug)
   ```

4. **Test** — add a unit test in `tests/unit/` and an integration
   test in `tests/integration/`.

5. **Docs** — the OpenAPI schema is generated automatically. Update
   the README's "API Overview" table to list the new endpoint.

---

## 5. Adding a new frontend page

Pages live in `frontend/src/app/<route>/page.tsx`. The App Router
uses file-based routing.

```tsx
// frontend/src/app/skills/[slug]/history/page.tsx
import { SkillHistoryList } from '@/components/SkillHistoryList';

export default function Page({ params }: { params: { slug: string } }) {
  return <SkillHistoryList slug={params.slug} />;
}
```

Conventions:

- Server components by default; mark `'use client'` only when needed
- Use TanStack Query for data fetching on the client
- Use the i18n hook for any user-facing string
- Add a translation key in `frontend/src/lib/i18n/translations.ts`
- Add a test in `frontend/src/__tests__/`

---

## 6. Adding a new SDK method

1. **Implement** the method in `sdk/<lang>/skill_sdk/`
2. **Type** the request/response in `types.py` / `types.ts`
3. **Test** it against a local server (`make dev`)
4. **Document** it in `sdk/<lang>/README.md` with a usage example
5. **Bump** the version in `pyproject.toml` / `package.json` (patch for
   additions, minor for breaking changes)

---

## 7. Database changes

Always go through Alembic. Never `CREATE TABLE` by hand.

```bash
# After editing a model
cd backend
poetry run alembic revision --autogenerate -m "add skill_history table"
# Review the generated migration under alembic/versions/
poetry run alembic upgrade head
poetry run alembic downgrade -1   # smoke-test the downgrade
```

For purely additive changes (new nullable column, new table), the
generated migration is usually fine. For anything destructive
(drop column, change type), write the migration by hand and add
explicit `op.execute(...)` data backfills.

---

## 8. Testing

### 8.1 Backend

```bash
cd backend
poetry run pytest -x                # stop on first failure
poetry run pytest --cov=app          # with coverage
poetry run pytest tests/integration  # integration only
poetry run pytest tests/unit        # unit only
```

The integration tests require Postgres and Redis. They are wired up
in `tests/conftest.py` to use the local services.

### 8.2 Frontend

```bash
cd frontend
npm test                  # run once
npm test -- --watch       # watch mode
npm run test:coverage     # with coverage
```

### 8.3 SDKs

```bash
# Python
cd sdk/python
poetry run pytest skill_sdk/

# TypeScript
cd sdk/typescript
npm test
```

### 8.4 Manual smoke test

Before opening a PR, walk through:

1. `make dev` boots cleanly
2. Frontend renders without console errors
3. `POST /auth/register` works
4. `POST /auth/login` returns a token
5. `GET /skills` returns the seeded list
6. `GET /skills/search?q=react` returns relevant results
7. `GET /health/ready` returns 200

---

## 9. Pull request checklist

See [`.github/PULL_REQUEST_TEMPLATE.md`](https://github.com/badhope/AI-SKILL/blob/main/.github/PULL_REQUEST_TEMPLATE.md).
The short version:

- [ ] Tests added or updated
- [ ] Linters clean (`make lint`)
- [ ] Type-checkers clean (`make typecheck`)
- [ ] Docs updated (README, docs/, docstrings)
- [ ] Changelog touched (if user-visible)
- [ ] No secrets, no `.env` files
- [ ] At least one reviewer (CODEOWNERS will assign automatically)

---

## 10. Release process

1. Bump the version in `backend/pyproject.toml`, `frontend/package.json`,
   `sdk/python/pyproject.toml`, and `sdk/typescript/package.json`.
2. Update `CHANGELOG.md` — move unreleased items under a dated section.
3. Open a PR titled `chore(release): vX.Y.Z`.
4. After merge, tag and push:

   ```bash
   git tag -s -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. The `deploy.yml` workflow builds and publishes Docker images with
   the tag.
6. Create a GitHub Release from the tag (the workflow will help).
