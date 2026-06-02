# Adding an API endpoint

A worked example. Suppose we want to add
`GET /api/v1/skills/{slug}/history` that returns the version history
of a skill.

## 1. Schema

Add a Pydantic response model in
`backend/app/schemas/skill.py`:

```python
class SkillHistoryEntry(BaseModel):
    version: str
    changelog: str
    created_at: datetime
    created_by: str | None = None
```

## 2. Service

Implement the data access in a new file
`backend/app/services/skill_history.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill, SkillVersion


async def get_history(db: AsyncSession, slug: str) -> list[SkillVersion]:
    skill = (await db.execute(select(Skill).where(Skill.slug == slug))).scalar_one_or_none()
    if skill is None:
        raise SkillNotFound(slug=slug)

    rows = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill.id)
            .order_by(SkillVersion.created_at.desc())
        )
    ).scalars().all()
    return list(rows)
```

## 3. Router

Add the endpoint in `backend/app/api/v1/skills.py`:

```python
from app.services.skill_history import get_history


@router.get("/{slug}/history", response_model=list[SkillHistoryEntry])
async def get_skill_history(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[SkillVersion]:
    return await get_history(db, slug)
```

## 4. Test

Add a unit test in `tests/unit/test_skill_history.py`:

```python
import pytest
from app.services.skill_history import get_history


@pytest.mark.asyncio
async def test_get_history_returns_recent_versions_first(db_session, sample_skill):
    versions = await get_history(db_session, slug=sample_skill.slug)
    assert len(versions) >= 1
    assert versions[0].created_at >= versions[-1].created_at
```

And an integration test in `tests/integration/test_skills_api.py`:

```python
async def test_get_skill_history_endpoint(client, auth_token, sample_skill):
    response = await client.get(
        f"/api/v1/skills/{sample_skill.slug}/history",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert "version" in body[0]
```

## 5. Docs

The OpenAPI schema is generated automatically. Update the README's
"API Overview" table to list the new endpoint and link to the
Swagger UI for the full schema.

## 6. Run the linters and tests

```bash
make lint
make typecheck
make test
```

## What if the change is breaking?

- Bump the API version in the route prefix (`/api/v1/...` →
  `/api/v2/...`) if the contract changes incompatibly
- Document the migration in `CHANGELOG.md`
- Keep the old endpoint alive for one release with a
  `Deprecation` header and a `Sunset` date

## Where to go from here

- [Adding a frontend page](adding-page.md) — companion guide
- [Database migrations](migrations.md) — when your endpoint needs a
  schema change
- [Testing](testing.md) — unit, integration, and smoke tests
