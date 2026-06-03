# 新增一个 API 端点

一个完整的示例。假设我们要新增
`GET /api/v1/skills/{slug}/history`，返回某个技能的版本历史。

## 1. Schema

在 `backend/app/schemas/skill.py` 中新增 Pydantic 响应模型：

```python
class SkillHistoryEntry(BaseModel):
    version: str
    changelog: str
    created_at: datetime
    created_by: str | None = None
```

## 2. Service

新建 `backend/app/services/skill_history.py` 实现数据访问：

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

在 `backend/app/api/v1/skills.py` 中挂载端点：

```python
from app.services.skill_history import get_history


@router.get("/{slug}/history", response_model=list[SkillHistoryEntry])
async def get_skill_history(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[SkillVersion]:
    return await get_history(db, slug)
```

## 4. 测试

在 `tests/unit/test_skill_history.py` 中新增单元测试：

```python
import pytest
from app.services.skill_history import get_history


@pytest.mark.asyncio
async def test_get_history_returns_recent_versions_first(db_session, sample_skill):
    versions = await get_history(db_session, slug=sample_skill.slug)
    assert len(versions) >= 1
    assert versions[0].created_at >= versions[-1].created_at
```

并在 `tests/integration/test_skills_api.py` 中新增集成测试：

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

## 5. 文档

OpenAPI Schema 由代码自动生成。请在 README 的「API 总览」表格中
登记新端点，并附上 Swagger UI 的完整 Schema 链接。

## 6. 运行 Linter 与测试

```bash
make lint
make typecheck
make test
```

## 假如改动了不兼容的接口？

- 若契约不兼容，应在路由前缀中升级 API 版本（`/api/v1/...` →
  `/api/v2/...`）
- 在 `CHANGELOG.md` 中记录迁移说明
- 旧端点至少保留一个发布周期，并附 `Deprecation` 头与 `Sunset` 日期

## 接下来去哪里

- [新增一个前端页面](adding-page.md) —— 配套指南
- [数据库迁移](migrations.md) —— 当端点需要 schema 变更时
- [测试](testing.md) —— 单元、集成、冒烟测试
