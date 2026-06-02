import os
import secrets
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.skill import Category, User

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

INITIAL_CATEGORIES = [
    {"name": "AI", "slug": "ai", "description": "人工智能相关技能", "icon": "cpu", "sort_order": 1},
    {"name": "Web Development", "slug": "web-dev", "description": "Web 开发相关技能", "icon": "globe", "sort_order": 2},
    {"name": "Data Science", "slug": "data-science", "description": "数据科学相关技能", "icon": "bar-chart", "sort_order": 3},
    {"name": "DevOps", "slug": "devops", "description": "开发运维相关技能", "icon": "settings", "sort_order": 4},
    {"name": "Mobile", "slug": "mobile", "description": "移动端开发相关技能", "icon": "smartphone", "sort_order": 5},
    {"name": "Database", "slug": "database", "description": "数据库相关技能", "icon": "database", "sort_order": 6},
]

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@ai-skill.local")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def _ensure_admin_password() -> Optional[str]:
    """
    Resolve the admin password from environment.

    Security policy:
      - The admin password MUST be supplied via the ``ADMIN_PASSWORD`` env var.
      - In development mode (DEBUG=true), if no password is supplied we generate
        a strong random one and log it once so the developer can use it.
      - In production mode (DEBUG=false), if no password is supplied we skip
        admin seeding entirely and emit a CRITICAL log line. The operator must
        run ``python -m app.scripts.create_admin`` to bootstrap the first admin.
    """
    if ADMIN_PASSWORD:
        return ADMIN_PASSWORD

    from app.core.config import settings

    if settings.DEBUG:
        generated = secrets.token_urlsafe(24)
        logger.warning(
            "ADMIN_PASSWORD not set; generated a one-time random password for development. "
            "Set ADMIN_PASSWORD env var explicitly to control the value.",
            admin_email=ADMIN_EMAIL,
            admin_username=ADMIN_USERNAME,
        )
        return generated

    logger.critical(
        "ADMIN_PASSWORD environment variable is not set. "
        "Skipping admin user seeding. "
        "Create the first admin via: python -m app.scripts.create_admin"
    )
    return None


async def _seed_categories(db: AsyncSession) -> None:
    result = await db.execute(select(Category).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Categories already exist, skipping category seeding")
        return

    for cat_data in INITIAL_CATEGORIES:
        category = Category(
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data["description"],
            icon=cat_data["icon"],
            sort_order=cat_data["sort_order"],
            is_active=True,
        )
        db.add(category)

    await db.commit()
    logger.info("Seeded initial categories", count=len(INITIAL_CATEGORIES))


async def _seed_admin_user(db: AsyncSession) -> None:
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Users already exist, skipping admin user seeding")
        return

    password = _ensure_admin_password()
    if password is None:
        return

    admin_user = User(
        email=ADMIN_EMAIL,
        username=ADMIN_USERNAME,
        full_name="System Administrator",
        hashed_password=pwd_context.hash(password),
        is_active=True,
        is_superuser=True,
    )
    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)
    logger.info("Seeded initial admin user", email=ADMIN_EMAIL, username=ADMIN_USERNAME)


async def seed_initial_data(db: AsyncSession) -> None:
    try:
        await _seed_categories(db)
        await _seed_admin_user(db)
    except Exception as e:
        logger.error("Failed to seed initial data", error=str(e))
        raise
