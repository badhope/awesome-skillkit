"""Database engine and session helpers.

Single source of truth for the async SQLAlchemy engine, the session
factory, and the `get_db` FastAPI dependency. The previous
`app/db/session.py` shim was removed in this refactor — re-import
`engine` / `async_session_factory` / `get_db` from this module.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Common declarative base for all ORM models."""


def _build_engine() -> AsyncEngine:
    """Build the async engine with pool settings sourced from config.

    `pool_size`, `pool_timeout`, `pool_recycle` and `pool_pre_ping` are
    only applied when the URL points to a real DB (not SQLite) — SQLite
    uses `StaticPool` and ignores these arguments.
    """
    kwargs: dict[str, object] = {"echo": settings.DEBUG, "future": True}
    if not settings.DATABASE_URL.startswith("sqlite"):
        kwargs.update(
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            pool_pre_ping=True,
        )
    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine: AsyncEngine = _build_engine()
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
# Backwards-compatible alias — older call sites still import this name.
AsyncSessionLocal = async_session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a transactional session.

    On success the session is committed (no-op if the endpoint already
    committed). On exception we roll back and re-raise so the
    ErrorHandler middleware can render the response.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
