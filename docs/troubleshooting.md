# AI-SKILL — Troubleshooting

If you are stuck, scan this page first. If it does not help, open a
[Q&A discussion](https://github.com/badhope/AI-SKILL/discussions) or
a [bug report](../.github/ISSUE_TEMPLATE/bug_report.md).

---

## The stack will not start

### `docker compose up` exits with "port is already allocated"

Something else on your host is using port 3000, 5432, 6379, 6333, or
8000. Find and stop it:

```bash
sudo lsof -i :5432
sudo lsof -i :8000
```

Or change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"   # expose Postgres on 5433 instead
```

### `JWT_SECRET_KEY environment variable is required in production`

`DEBUG=false` and `JWT_SECRET_KEY` is empty or shorter than 32 chars.
Generate one:

```bash
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\"" >> .env
```

Then restart: `docker compose up -d`.

### `ADMIN_PASSWORD environment variable is not set`

Same issue, different variable. The application refuses to create a
default admin in production. Either:

```bash
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

or run the dedicated CLI to bootstrap a superuser:

```bash
ADMIN_PASSWORD="$(openssl rand -base64 18)" \
ADMIN_EMAIL="ops@your-domain.com" \
ADMIN_USERNAME="ops" \
docker compose exec backend python -m app.scripts.create_admin
```

### `alembic.util.exc.CommandError: Can't locate revision identified by '...'`

The `alembic_version` row references a revision that is not in the
migrations directory. This usually means a partial `git pull` or
a custom migration was removed. Recover with:

```bash
docker compose exec backend poetry run alembic stamp head
```

---

## Database errors

### `asyncpg.exceptions.UniqueViolationError`

You tried to create a duplicate (e.g. user with an email that already
exists). The API returns `409 Conflict`. If this is unexpected, look
for stale seed data:

```bash
docker compose exec -T postgres psql -U skill_user skill_db \
  -c "SELECT email FROM users;"
```

### `psycopg2.OperationalError: could not connect to server`

The backend cannot reach Postgres. Check:

```bash
docker compose ps postgres
docker compose logs postgres
```

If the database is up but the backend still cannot connect, verify the
`DATABASE_URL` host. Inside Compose it must be `postgres`, not
`localhost`.

### `relation "users" does not exist`

Migrations have not run. Apply them:

```bash
docker compose exec backend poetry run alembic upgrade head
```

---

## Frontend issues

### `Failed to fetch` in the browser console

The API is unreachable from the browser. Open
<http://localhost:8000/health> in a tab — if that loads, the backend
is fine and the issue is CORS or `VITE_API_BASE_URL`.

Check that the env var in `frontend/.env.local` matches where the
backend is actually serving:

```bash
echo $VITE_API_BASE_URL
# should be http://localhost:8000/api/v1 in dev
```

### Pages are blank after `npm run build`

Most likely an SSR-time error. Check the build log and the runtime
logs:

```bash
npm run build 2>&1 | tee build.log
docker compose logs frontend
```

### `Module not found: Can't resolve '@ai-skill/sdk'`

The local TypeScript SDK package is not linked. From the SDK
directory:

```bash
cd sdk/typescript
npm run build
npm link
cd ../../frontend
npm link @ai-skill/sdk
```

Or install the published version:

```bash
npm install @ai-skill/sdk
```

---

## Vector search returns no results

### Empty results for an obvious query

The Qdrant collection may not exist yet, or the embedding model
dimension is wrong. Check:

```bash
curl http://localhost:6333/collections/skills
```

If the collection is missing, restart the backend — it creates the
collection on startup. If the dimension is wrong, you have a model
mismatch. Either:

- Set `EMBEDDING_MODEL` to the same model used for indexing
- Reindex after changing the model

### `QdrantException: Not found: Collection skills doesn't exist`

The collection is missing. Force a recreate:

```bash
docker compose exec backend python -c "
import asyncio
from app.services.vector_search import get_qdrant
async def main():
    q = await get_qdrant()
    await q.recreate_collection('skills', vectors_count=768)
asyncio.run(main())
"
```

---

## Performance

### Slow search

1. Check that the HNSW index is built (`status: green` in the Qdrant dashboard)
2. Reduce `EMBEDDING_DIMENSION` if you switch to a smaller model
3. Add a Redis cache in front of the most common queries
4. Profile the backend:

```bash
docker compose exec backend py-spy dump --pid 1
```

### High memory on the backend

The embedding model is loaded lazily. To free memory:

```bash
docker compose restart backend
```

For a permanent fix, set `EMBEDDING_MODEL=` to an empty string and
run the embedding service in a separate worker.

### Postgres is slow

Check indexes:

```sql
\d skills
```

Run `VACUUM ANALYZE` periodically:

```sql
VACUUM ANALYZE skills;
```

---

## Authentication

### "Invalid token" right after login

Most likely the system clock is off on the backend or the client.
JWT validation is time-sensitive.

```bash
docker compose exec backend date
date
```

### "User is not active"

The account was deactivated. Re-activate via SQL:

```sql
UPDATE users SET is_active = true WHERE email = 'you@example.com';
```

### Forgot the admin password

Reset it:

```bash
docker compose exec backend python -c "
import asyncio
from app.db.session import async_session_factory
from app.models.skill import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def reset():
    async with async_session_factory() as db:
        u = (await db.execute(select(User).where(User.email == 'admin@ai-skill.local'))).scalar_one()
        u.hashed_password = get_password_hash('NEW_PASSWORD_HERE')
        await db.commit()
        print('Password reset for', u.email)

asyncio.run(reset())
"
```

---

## CI is failing

### `ruff` reports many errors on first run

Run the auto-fixer:

```bash
cd backend && poetry run ruff check --fix app/
cd sdk/python && poetry run ruff check --fix skill_sdk/
```

### `mypy` complains about missing imports

Add the package to `[tool.mypy]` overrides in `pyproject.toml`, or
add `# type: ignore[import-untyped]` at the import site.

### `npm test` is timing out

The frontend tests share a database. Make sure the test database is
isolated:

```bash
docker compose exec -T postgres \
  psql -U skill_user -c "CREATE DATABASE skill_test_db;"
```

---

## Logs

### Where are the logs?

```bash
docker compose logs backend   | tail -200
docker compose logs frontend  | tail -200
docker compose logs postgres  | tail -200
docker compose logs qdrant    | tail -200
```

### Enable debug logging

```bash
# .env
LOG_LEVEL=DEBUG
```

Then `docker compose restart backend`.

---

## Still stuck?

1. Search [existing issues](https://github.com/badhope/AI-SKILL/issues)
2. Search [Discussions / Q&A](https://github.com/badhope/AI-SKILL/discussions/categories/q-a)
3. Open a [new issue](../.github/ISSUE_TEMPLATE/bug_report.md) with
   the output of `make health-check` and `docker compose logs backend`
