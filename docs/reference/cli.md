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

## `python -m app.scripts.reindex`

Reindex every skill in the Qdrant collection. Run this when you
change `EMBEDDING_MODEL` or after a manual database fix-up.

```bash
python -m app.scripts.reindex [--batch 100] [--resume-from <skill-id>]
```

| Flag                  | Default | Purpose                              |
|-----------------------|---------|--------------------------------------|
| `--batch N`           | 100     | Skills per Qdrant upsert             |
| `--resume-from ID`    | None    | Skip skills with id < ID (for resumable runs) |
| `--dry-run`           | false   | Compute but do not write             |

The script is **idempotent** — re-running it does not create
duplicate Qdrant points.

## `python -m app.core.seed`

Idempotent seed of categories, tags, and (optionally) the first
admin. Called automatically on backend startup; rarely run by hand.

```bash
python -m app.core.seed
```

In production, the admin seeding step is skipped unless
`ADMIN_PASSWORD` is set.

## `python scripts/health_check.py`

Hit the running backend's health endpoints and print a status
report. Useful in deploy pipelines and as a post-mortem tool.

```bash
python scripts/health_check.py --url http://localhost:8000
```

| Check                       | What it does                                |
|-----------------------------|---------------------------------------------|
| `/health`                   | App is alive                                |
| `/health/ready`             | Postgres + Redis + Qdrant are reachable     |
| Database migration head     | Alembic version matches the latest         |
| Qdrant collection present   | The `skills` collection exists             |
| Qdrant collection count     | Number of indexed skills                    |

Exit codes:

- `0` — all checks pass
- `1` — at least one check failed
- `2` — the backend is unreachable

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

- [Makefile](../../Makefile) — the full list of targets
- [Backup & restore](../operations/backup.md)
