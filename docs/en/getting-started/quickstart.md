# Quick start

This page gets you from a fresh install to a working skill in the
catalog in 5 minutes.

## 1. Make sure the stack is up

```bash
docker compose ps
# Both backend and frontend should be in the "running" state
```

If anything is not running:

```bash
docker compose up -d
docker compose logs -f backend
```

## 2. Log in

Open <http://localhost:3000> in a browser. Click **Log in** →
**Register** and create an account. (If you skipped step 1 of
[Installation](installation.md), you can also bootstrap a superuser
via `docker compose exec backend python -m app.scripts.create_admin`
and log in with those credentials.)

## 3. Find your frontend category slug

The skill you are about to create needs a `category_slug`. The
simplest way to find it is via the API (returns a flat JSON
array, ordered by `sort_order`):

```bash
curl -s http://localhost:8000/api/v1/categories | jq
```

You will see something like:

```json
[
  { "id": "8d2e…", "slug": "frontend", "name": "Frontend", … },
  { "id": "f3a4…", "slug": "backend",  "name": "Backend",  … },
  …
]
```

Copy the `slug` of the **Frontend** category.

## 4. Create a skill via the API

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"you","password":"hunter2"}' | jq -r .access_token)

curl -s -X POST http://localhost:8000/api/v1/skills \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "React useMemo deep-dive",
    "slug": "react-usememo-deep-dive",
    "description": "A practical guide to React useMemo with examples",
    "category_slug": "frontend",
    "tags": ["react", "performance"],
    "version": "1.0.0",
    "is_public": true,
    "content": {
      "summary": "useMemo lets you cache the result of an expensive calculation between renders…",
      "examples": []
    }
  }' | jq
```

A 201 response means the skill was created. The platform indexes it
asynchronously into Qdrant for semantic search.

## 5. See it in the UI

Refresh <http://localhost:3000>. Your new skill should appear at the
top of the **Frontend** category page, and searching for "useMemo"
should rank it highly.

## 6. Search it semantically

The search endpoint is `GET` and takes the query as a URL
parameter (`q`); it returns a flat JSON array ranked by score:

```bash
curl -s "http://localhost:8000/api/v1/skills/search?q=cache+expensive+react&limit=5" | jq
```

You should see your skill at the top with a high score, even though
your skill's text does not contain the literal words "cache" or
"expensive".

## Where to go from here

- [Examples](../examples/) — REST, Python, and TypeScript
  SDK recipes
- [Architecture](../architecture.md) — understand the moving parts
- [Deployment](../deployment.md) — promote to production
