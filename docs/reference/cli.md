# CLI

The backend ships a small set of command-line tools. They live in
`backend/app/scripts/` and are run as Python modules.

## `python -m app.scripts.create_admin`

Interactive bootstrap of the first superuser.

```bash
ADMIN_PASSWORD='<strong>' \
ADMIN_EMAIL='ops@example.com' \
ADMIN_USERNAME='ops' \
python -m app.scripts.create_admin
```

If `ADMIN_PASSWORD` is not set, the script prompts for it (and
confirms it). It refuses to:

- Use a password shorter than 12 characters
- Use a common weak password (`password`, `admin`, `changeme`, etc.)
- Overwrite an existing user with the same email or username

## `skill-cli index rebuild`

Reindex every public skill in the Qdrant collection. Run this
when you change `EMBEDDING_MODEL` or after a manual database
fix-up.

```bash
cd backend
poetry run python -m app.cli index rebuild --yes
```

| Flag       | Default | Purpose                            |
|------------|---------|------------------------------------|
| `--yes`    | false   | Skip the interactive confirmation  |

The command is **idempotent** — re-running it rebuilds the
collection in place; the existing points are removed before the
new ones are written.

## `python -m app.core.seed`

Idempotent seed of categories, tags, and (optionally) the first
admin. Called automatically on backend startup; rarely run by hand.

```bash
python -m app.core.seed
```

In production, the admin seeding step is skipped unless
`ADMIN_PASSWORD` is set.

## `python scripts/health_check.py`

Hit the running backend and its dependencies and print a status
report. Useful in deploy pipelines and as a post-mortem tool.

```bash
python scripts/health_check.py
# or, with the Makefile:
make health-check
```

| Check         | What it does                                |
|---------------|---------------------------------------------|
| PostgreSQL    | Connects to `DATABASE_URL` and runs `SELECT version()` |
| Redis         | Connects to `REDIS_URL` and runs `PING`     |
| Qdrant        | Calls `GET ${QDRANT_URL}/health` (or `/collections` as a fallback) |
| API           | Calls `GET ${API_URL}/health` and reads `app_name` / `version` |

Exit codes:

- `0` — all checks pass
- `1` — at least one check failed

## `skill-cli` (in-process Typer app)

`backend/app/cli/main.py` exposes a `skill-cli` for routine
operator tasks that does not require HTTP. It is the canonical
CLI for this project; the scripts above are kept for one-off
bootstrapping and external probing.

```bash
cd backend
poetry run python -m app.cli --help
```

The currently-registered subcommands are:

| Command                 | Purpose                                            |
|-------------------------|----------------------------------------------------|
| `version`               | Print `APP_NAME` and `APP_VERSION`                 |
| `skills`                | Skill CRUD / listing / reindex                      |
| `categories`            | Category management                                 |
| `tags`                  | Tag management                                      |
| `search`                | One-off semantic search against Qdrant              |
| `import` / `export`     | Skill-pack round-trip                               |
| `index`                 | Rebuild / inspect the Qdrant index                 |
| `cache`                 | Flush / inspect the Redis cache                     |

## `make` recipes

The most common workflows are also exposed as Make targets. Run
`make help` for the full list.

```bash
make help               # list all targets
make dev                # bring the stack up
make test               # run all tests
make db-upgrade         # apply migrations
make db-revision msg=…  # create a new migration
make secrets-scan       # grep for hardcoded credentials
```

## Where to go from here

- [Makefile](https://github.com/badhope/AI-SKILL/blob/main/Makefile) — the full list of targets
- [Backup & restore](../operations/backup.md)
