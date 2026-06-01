import asyncio
import uuid as uuid_lib
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator, Dict, Optional, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import numpy
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import sys

mock_vs = MagicMock()
mock_vs_module = MagicMock()
mock_vs_module.VectorSearchService = MagicMock(return_value=mock_vs)
mock_vs_module.BM25Scorer = MagicMock()
mock_vs.index_skill = AsyncMock(return_value="mock-index-id")
mock_vs.index_skills_batch = AsyncMock(return_value=["mock-id-1"])
mock_vs.search_skills = AsyncMock(return_value=[])
mock_vs.find_similar_skills = AsyncMock(return_value=[])
mock_vs.delete_skill_index = AsyncMock(return_value=True)
mock_vs.hybrid_search = AsyncMock(return_value=[])
mock_vs.get_search_suggestions = AsyncMock(return_value=[])
mock_vs.get_collection_info = AsyncMock(return_value={
    "name": "skills", "vectors_count": 0, "vector_size": 384, "distance": "Cosine"
})

sys.modules["sentence_transformers"] = MagicMock()
sys.modules["app.services.vector_search"] = mock_vs_module

from app.api.v1.router import api_router

from app.core.config import Settings, get_settings
from app.core.deps import get_current_active_user, get_current_superuser, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.skill import Base, Category, Skill, Tag, User

SYNC_DATABASE_URL = "sqlite:///./test.db"
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

_test_engine = None
_TestSessionLocal = None
_sync_engine = None
_SyncSessionLocal = None


def _get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            SYNC_DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(_sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

    return _sync_engine


def _get_sync_sessionmaker():
    global _SyncSessionLocal
    if _SyncSessionLocal is None:
        _SyncSessionLocal = sessionmaker(
            _get_sync_engine(),
            class_=Session,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _SyncSessionLocal


def _get_test_engine():
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
        )
    return _test_engine


def _get_test_sessionmaker():
    global _TestSessionLocal
    if _TestSessionLocal is None:
        _TestSessionLocal = async_sessionmaker(
            _get_test_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _TestSessionLocal


@pytest.fixture(scope="function")
def sync_db() -> Generator[Session, None, None]:
    engine = _get_sync_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    sessionmaker_ = _get_sync_sessionmaker()
    session = sessionmaker_()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_user_sync(sync_db: Session) -> dict:
    user = User(
        id=uuid_lib.UUID("a0000000-0000-0000-0000-000000000001"),
        email="testuser@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_superuser=False,
        full_name="Test User",
    )
    sync_db.add(user)
    sync_db.commit()
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "password": "TestPass123!",
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "full_name": user.full_name,
    }


@pytest.fixture(scope="function")
def test_category_sync(sync_db: Session) -> dict:
    category = Category(
        id=uuid_lib.UUID("c0000000-0000-0000-0000-000000000001"),
        name="Code Generation",
        slug="code-generation",
        description="Skills for generating code",
        icon="code",
        sort_order=0,
        is_active=True,
    )
    sync_db.add(category)
    sync_db.commit()
    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon": category.icon,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


@pytest.fixture(scope="function")
def test_tag_sync(sync_db: Session) -> dict:
    tag = Tag(
        id=uuid_lib.UUID("d0000000-0000-0000-0000-000000000001"),
        name="python",
        color="#3776AB",
        description="Python related skills",
        usage_count=0,
    )
    sync_db.add(tag)
    sync_db.commit()
    return {
        "id": str(tag.id),
        "name": tag.name,
        "color": tag.color,
        "description": tag.description,
        "usage_count": tag.usage_count,
    }


@pytest.fixture(scope="function")
def test_skill_sync(
    sync_db: Session, test_user_sync: dict, test_category_sync: dict, test_tag_sync: dict
) -> dict:
    skill = Skill(
        id=uuid_lib.UUID("e0000000-0000-0000-0000-000000000001"),
        name="Python Code Generator",
        slug="python-code-generator",
        description="Generates Python code from natural language",
        version="1.0.0",
        category_id=uuid_lib.UUID(test_category_sync["id"]),
        author_id=uuid_lib.UUID(test_user_sync["id"]),
        complexity="intermediate",
        status="published",
        license="MIT",
        source_url="https://github.com/example/python-gen",
        is_public=True,
        is_featured=True,
        download_count=100,
        view_count=500,
        usage_count=200,
        rating_avg=4.5,
        rating_count=10,
        content={"prompt": "Generate Python code for: "},
        extra_metadata={"framework": "fastapi"},
    )
    sync_db.add(skill)
    sync_db.flush()

    tag = sync_db.get(Tag, uuid_lib.UUID(test_tag_sync["id"]))
    if tag:
        skill.tags.append(tag)

    sync_db.commit()
    return {
        "id": str(skill.id),
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "version": skill.version,
        "category_id": test_category_sync["id"],
        "author_id": test_user_sync["id"],
        "complexity": skill.complexity.value if hasattr(skill.complexity, "value") else skill.complexity,
        "status": skill.status.value if hasattr(skill.status, "value") else skill.status,
        "license": skill.license,
        "source_url": skill.source_url,
        "is_public": skill.is_public,
        "is_featured": skill.is_featured,
        "download_count": skill.download_count,
        "view_count": skill.view_count,
        "usage_count": skill.usage_count,
        "rating_avg": skill.rating_avg,
        "rating_count": skill.rating_count,
        "content": skill.content,
        "extra_metadata": skill.extra_metadata,
    }


@pytest.fixture(scope="function")
def test_second_skill_sync(
    sync_db: Session, test_user_sync: dict, test_category_sync: dict
) -> dict:
    skill = Skill(
        id=uuid_lib.UUID("e0000000-0000-0000-0000-000000000002"),
        name="TypeScript Code Generator",
        slug="typescript-code-generator",
        description="Generates TypeScript code",
        version="1.0.0",
        category_id=uuid_lib.UUID(test_category_sync["id"]),
        author_id=uuid_lib.UUID(test_user_sync["id"]),
        complexity="beginner",
        status="published",
        license="Apache-2.0",
        is_public=True,
        is_featured=False,
        download_count=50,
        view_count=200,
        usage_count=80,
        rating_avg=3.8,
        rating_count=5,
        content={"prompt": "Generate TS code for: "},
        extra_metadata={},
    )
    sync_db.add(skill)
    sync_db.commit()
    return {
        "id": str(skill.id),
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "version": skill.version,
        "category_id": test_category_sync["id"],
        "author_id": test_user_sync["id"],
        "complexity": skill.complexity.value if hasattr(skill.complexity, "value") else skill.complexity,
        "status": skill.status.value if hasattr(skill.status, "value") else skill.status,
        "license": skill.license,
        "is_public": skill.is_public,
        "is_featured": skill.is_featured,
        "download_count": skill.download_count,
        "view_count": skill.view_count,
        "usage_count": skill.usage_count,
        "rating_avg": skill.rating_avg,
        "rating_count": skill.rating_count,
        "content": skill.content,
        "extra_metadata": skill.extra_metadata,
    }


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    engine = _get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = _get_test_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> dict:
    from app.models.skill import User

    user = User(
        id=uuid_lib.UUID("a0000000-0000-0000-0000-000000000001"),
        email="testuser@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_superuser=False,
        full_name="Test User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "password": "TestPass123!",
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "full_name": user.full_name,
    }


@pytest_asyncio.fixture(scope="function")
async def test_superuser(test_db: AsyncSession) -> dict:
    from app.models.skill import User

    user = User(
        id=uuid_lib.UUID("b0000000-0000-0000-0000-000000000001"),
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPass123!"),
        is_active=True,
        is_superuser=True,
        full_name="Admin User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "password": "AdminPass123!",
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "full_name": user.full_name,
    }


@pytest_asyncio.fixture(scope="function")
async def test_token(test_user: dict) -> str:
    return create_access_token(
        subject=test_user["id"],
        expires_delta=timedelta(minutes=30),
    )


@pytest_asyncio.fixture(scope="function")
async def test_superuser_token(test_superuser: dict) -> str:
    return create_access_token(
        subject=test_superuser["id"],
        expires_delta=timedelta(minutes=30),
    )


@pytest_asyncio.fixture(scope="function")
async def test_category(test_db: AsyncSession) -> dict:
    from app.models.skill import Category

    category = Category(
        id=uuid_lib.UUID("c0000000-0000-0000-0000-000000000001"),
        name="Code Generation",
        slug="code-generation",
        description="Skills for generating code",
        icon="code",
        sort_order=0,
        is_active=True,
    )
    test_db.add(category)
    await test_db.commit()
    await test_db.refresh(category)
    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon": category.icon,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


@pytest_asyncio.fixture(scope="function")
async def test_child_category(test_db: AsyncSession, test_category: dict) -> dict:
    from app.models.skill import Category

    child = Category(
        id=uuid_lib.UUID("c0000000-0000-0000-0000-000000000002"),
        name="Python Generation",
        slug="python-generation",
        description="Python code generation skills",
        parent_id=uuid_lib.UUID(test_category["id"]),
        icon="python",
        sort_order=1,
        is_active=True,
    )
    test_db.add(child)
    await test_db.commit()
    await test_db.refresh(child)
    return {
        "id": str(child.id),
        "name": child.name,
        "slug": child.slug,
        "description": child.description,
        "parent_id": test_category["id"],
        "icon": child.icon,
        "sort_order": child.sort_order,
        "is_active": child.is_active,
    }


@pytest_asyncio.fixture(scope="function")
async def test_tag(test_db: AsyncSession) -> dict:
    from app.models.skill import Tag

    tag = Tag(
        id=uuid_lib.UUID("d0000000-0000-0000-0000-000000000001"),
        name="python",
        color="#3776AB",
        description="Python related skills",
        usage_count=0,
    )
    test_db.add(tag)
    await test_db.commit()
    await test_db.refresh(tag)
    return {
        "id": str(tag.id),
        "name": tag.name,
        "color": tag.color,
        "description": tag.description,
        "usage_count": tag.usage_count,
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill(
    test_db: AsyncSession, test_user: dict, test_category: dict, test_tag: dict
) -> dict:
    from app.models.skill import Skill, Tag, skill_tag_association

    skill = Skill(
        id=uuid_lib.UUID("e0000000-0000-0000-0000-000000000001"),
        name="Python Code Generator",
        slug="python-code-generator",
        description="Generates Python code from natural language",
        version="1.0.0",
        category_id=uuid_lib.UUID(test_category["id"]),
        author_id=uuid_lib.UUID(test_user["id"]),
        complexity="intermediate",
        status="published",
        license="MIT",
        source_url="https://github.com/example/python-gen",
        is_public=True,
        is_featured=True,
        download_count=100,
        view_count=500,
        usage_count=200,
        rating_avg=4.5,
        rating_count=10,
        content={"prompt": "Generate Python code for: "},
        extra_metadata={"framework": "fastapi"},
    )
    test_db.add(skill)
    await test_db.flush()

    tag_result = await test_db.get(Tag, uuid_lib.UUID(test_tag["id"]))
    if tag_result:
        await test_db.execute(
            skill_tag_association.insert().values(
                skill_id=skill.id, tag_id=tag_result.id
            )
        )

    await test_db.commit()
    await test_db.refresh(skill)
    return {
        "id": str(skill.id),
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "version": skill.version,
        "category_id": test_category["id"],
        "author_id": test_user["id"],
        "complexity": skill.complexity.value if hasattr(skill.complexity, "value") else skill.complexity,
        "status": skill.status.value if hasattr(skill.status, "value") else skill.status,
        "license": skill.license,
        "source_url": skill.source_url,
        "is_public": skill.is_public,
        "is_featured": skill.is_featured,
        "download_count": skill.download_count,
        "view_count": skill.view_count,
        "usage_count": skill.usage_count,
        "rating_avg": skill.rating_avg,
        "rating_count": skill.rating_count,
        "content": skill.content,
        "extra_metadata": skill.extra_metadata,
    }


@pytest_asyncio.fixture(scope="function")
async def test_second_skill(
    test_db: AsyncSession, test_user: dict, test_category: dict
) -> dict:
    from app.models.skill import Skill

    skill = Skill(
        id=uuid_lib.UUID("e0000000-0000-0000-0000-000000000002"),
        name="TypeScript Code Generator",
        slug="typescript-code-generator",
        description="Generates TypeScript code",
        version="1.0.0",
        category_id=uuid_lib.UUID(test_category["id"]),
        author_id=uuid_lib.UUID(test_user["id"]),
        complexity="beginner",
        status="published",
        license="Apache-2.0",
        is_public=True,
        is_featured=False,
        download_count=50,
        view_count=200,
        usage_count=80,
        rating_avg=3.8,
        rating_count=5,
        content={"prompt": "Generate TS code for: "},
        extra_metadata={},
    )
    test_db.add(skill)
    await test_db.commit()
    await test_db.refresh(skill)
    return {
        "id": str(skill.id),
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "version": skill.version,
        "category_id": test_category["id"],
        "author_id": test_user["id"],
        "complexity": skill.complexity.value if hasattr(skill.complexity, "value") else skill.complexity,
        "status": skill.status.value if hasattr(skill.status, "value") else skill.status,
        "license": skill.license,
        "is_public": skill.is_public,
        "is_featured": skill.is_featured,
        "download_count": skill.download_count,
        "view_count": skill.view_count,
        "usage_count": skill.usage_count,
        "rating_avg": skill.rating_avg,
        "rating_count": skill.rating_count,
        "content": skill.content,
        "extra_metadata": skill.extra_metadata,
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill_version(
    test_db: AsyncSession, test_skill: dict, test_user: dict
) -> dict:
    from app.models.skill import SkillVersion

    version = SkillVersion(
        id=uuid_lib.UUID("f0000000-0000-0000-0000-000000000001"),
        skill_id=uuid_lib.UUID(test_skill["id"]),
        version="2.0.0",
        content={"prompt": "Generate optimized Python code for: "},
        changelog="Improved prompt template",
        created_by_id=uuid_lib.UUID(test_user["id"]),
    )
    test_db.add(version)
    await test_db.commit()
    await test_db.refresh(version)
    return {
        "id": str(version.id),
        "skill_id": test_skill["id"],
        "version": version.version,
        "content": version.content,
        "changelog": version.changelog,
        "created_by_id": test_user["id"],
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill_dependency(
    test_db: AsyncSession, test_skill: dict, test_second_skill: dict
) -> dict:
    from app.models.skill import SkillDependency

    dep = SkillDependency(
        id=uuid_lib.UUID("10000000-0000-0000-0000-000000000001"),
        skill_id=uuid_lib.UUID(test_skill["id"]),
        depends_on_skill_id=uuid_lib.UUID(test_second_skill["id"]),
        version_constraint=">=1.0.0",
    )
    test_db.add(dep)
    await test_db.commit()
    await test_db.refresh(dep)
    return {
        "id": str(dep.id),
        "skill_id": test_skill["id"],
        "depends_on_skill_id": test_second_skill["id"],
        "version_constraint": dep.version_constraint,
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill_rating(
    test_db: AsyncSession, test_skill: dict, test_user: dict
) -> dict:
    from app.models.skill import SkillRating

    rating = SkillRating(
        id=uuid_lib.UUID("20000000-0000-0000-0000-000000000001"),
        skill_id=uuid_lib.UUID(test_skill["id"]),
        user_id=uuid_lib.UUID(test_user["id"]),
        rating=5,
        comment="Excellent skill!",
    )
    test_db.add(rating)
    await test_db.commit()
    await test_db.refresh(rating)
    return {
        "id": str(rating.id),
        "skill_id": test_skill["id"],
        "user_id": test_user["id"],
        "rating": rating.rating,
        "comment": rating.comment,
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill_usage_log(
    test_db: AsyncSession, test_skill: dict, test_user: dict
) -> dict:
    from app.models.skill import SkillUsageLog

    log = SkillUsageLog(
        id=uuid_lib.UUID("30000000-0000-0000-0000-000000000001"),
        skill_id=uuid_lib.UUID(test_skill["id"]),
        user_id=uuid_lib.UUID(test_user["id"]),
        action="download",
    )
    test_db.add(log)
    await test_db.commit()
    await test_db.refresh(log)
    return {
        "id": str(log.id),
        "skill_id": test_skill["id"],
        "user_id": test_user["id"],
        "action": log.action,
    }


@pytest_asyncio.fixture(scope="function")
async def test_skill_composition(
    test_db: AsyncSession, test_user: dict, test_skill: dict, test_second_skill: dict
) -> dict:
    from app.models.skill import SkillComposition, SkillCompositionItem

    comp = SkillComposition(
        id=uuid_lib.UUID("40000000-0000-0000-0000-000000000001"),
        name="My Workflow",
        slug="my-workflow",
        description="A test composition",
        owner_id=uuid_lib.UUID(test_user["id"]),
        is_public=True,
        extra_metadata={"mode": "sequential"},
    )
    test_db.add(comp)
    await test_db.flush()

    item1 = SkillCompositionItem(
        composition_id=comp.id,
        skill_id=uuid_lib.UUID(test_skill["id"]),
        sort_order=0,
        notes="First step",
    )
    item2 = SkillCompositionItem(
        composition_id=comp.id,
        skill_id=uuid_lib.UUID(test_second_skill["id"]),
        sort_order=1,
        notes="Second step",
    )
    test_db.add(item1)
    test_db.add(item2)
    await test_db.commit()
    await test_db.refresh(comp)
    return {
        "id": str(comp.id),
        "name": comp.name,
        "slug": comp.slug,
        "description": comp.description,
        "owner_id": test_user["id"],
        "is_public": comp.is_public,
        "extra_metadata": comp.extra_metadata,
    }


def _get_test_db_override(test_db_session: AsyncSession):
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    return override_get_db


def _get_sync_db_override(sync_session: Session):
    async def override_get_db() -> AsyncGenerator[Session, None]:
        yield sync_session

    return override_get_db


def _mock_vector_service():
    mock = MagicMock()
    mock.index_skill = AsyncMock(return_value="mock-index-id")
    mock.index_skills_batch = AsyncMock(return_value=["mock-id-1", "mock-id-2"])
    mock.search_skills = AsyncMock(return_value=[])
    mock.find_similar_skills = AsyncMock(return_value=[])
    mock.delete_skill_index = AsyncMock(return_value=True)
    mock.hybrid_search = AsyncMock(return_value=[])
    mock.get_search_suggestions = AsyncMock(return_value=[])
    mock.get_collection_info = AsyncMock(return_value={
        "name": "skills", "vectors_count": 0, "vector_size": 384, "distance": "Cosine"
    })
    return mock


def _mock_get_vector_service():
    return _mock_vector_service()


@pytest_asyncio.fixture(scope="function")
async def test_app(test_db: AsyncSession) -> FastAPI:
    from app.core import deps as core_deps
    from app.api.v1 import skills as skills_module

    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")

    app.dependency_overrides[get_db] = _get_test_db_override(test_db)
    app.dependency_overrides[skills_module._get_vector_service] = _mock_get_vector_service

    return app


@pytest_asyncio.fixture(scope="function")
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_client_auth(
    test_app: FastAPI, test_token: str
) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {test_token}"},
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_client_superuser(
    test_app: FastAPI, test_superuser_token: str
) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {test_superuser_token}"},
    ) as client:
        yield client