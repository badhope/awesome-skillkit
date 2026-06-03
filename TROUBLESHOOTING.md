# AI-SKILL — Troubleshooting

> Looking for the long-form troubleshooting guide? See
> [docs/troubleshooting.md](docs/troubleshooting.md). This page is
> the short version for the README.

## The stack will not start

| Symptom | Fix |
|---|---|
| `port already allocated` | Free the port: `sudo lsof -i :8000` and kill the process, or remap in `docker-compose.yml` |
| `JWT_SECRET_KEY environment variable is required in production` | Set `JWT_SECRET_KEY="$(openssl rand -hex 32)"` in `.env` |
| `ADMIN_PASSWORD environment variable is not set` | Set `ADMIN_PASSWORD="$(openssl rand -base64 18)"` in `.env`, or run `make create-admin` |
| `relation "users" does not exist` | Migrations missing: `docker compose exec backend poetry run alembic upgrade head` |

## The frontend is blank

- Open the browser dev-tools → Network tab → look for failed requests
- Confirm `VITE_API_BASE_URL` points to the backend
- Confirm CORS: `BACKEND_CORS_ORIGINS` in `.env` includes the frontend origin

## Search returns nothing

- Verify Qdrant: `curl http://localhost:6333/collections`
- Verify the embedding model dimension matches the index dimension
- Check backend logs for `QdrantException`

## I forgot the admin password

Reset it via SQL — see [docs/troubleshooting.md](docs/troubleshooting.md#forgot-the-admin-password).

## Logs

```bash
make logs                          # all services
docker compose logs -f backend     # backend only
```

## Still stuck?

1. Check [docs/en/troubleshooting.md](docs/en/troubleshooting.md)
2. Search [existing issues](https://github.com/badhope/AI-SKILL/issues)
3. Open a [new bug report](.github/ISSUE_TEMPLATE/bug_report.md)
   with the output of `make health-check` and `docker compose logs`
