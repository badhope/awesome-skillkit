#!/usr/bin/env python3
"""
Bootstrap a single superuser.

Usage:
    ADMIN_PASSWORD='<strong>' ADMIN_EMAIL='admin@example.com' \\
        ADMIN_USERNAME=admin \\
        python -m app.scripts.create_admin

This is the recommended way to seed the first administrator after running
``alembic upgrade head``. It refuses to run if a user already exists with
the same email or username, and refuses to run if ``ADMIN_PASSWORD`` is
missing or weak in production.
"""
from __future__ import annotations

import asyncio
import os
import sys
from getpass import getpass

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.db import async_session_factory
from app.models.skill import User

logger = get_logger(__name__)

# Import the canonical weak-password list from the auth router. Keeping
# two copies (here and in `app.api.v1.auth`) meant the two drifted —
# #15 added 5 new entries to the auth list and this script silently
# kept the old set, so an admin could still bootstrap a weak
# password that the API would later refuse to accept.
from app.api.v1.auth import WEAK_PASSWORDS as _AUTH_WEAK_PASSWORDS  # noqa: E402


def _prompt_password_if_missing() -> str:
    password = os.environ.get("ADMIN_PASSWORD")
    if password:
        return password

    if not sys.stdin.isatty():
        raise SystemExit(
            "ADMIN_PASSWORD env var is required when not running in a TTY. "
            "Generate one with `openssl rand -base64 18`."
        )

    while True:
        pw1 = getpass("Admin password: ")
        pw2 = getpass("Confirm password: ")
        if pw1 != pw2:
            print("Passwords do not match; try again.")
            continue
        if len(pw1) < 12:
            print("Password must be at least 12 characters.")
            continue
        if pw1.lower() in _AUTH_WEAK_PASSWORDS:
            print("Password is too common; pick a stronger one.")
            continue
        return pw1


async def main() -> int:
    email = os.environ.get("ADMIN_EMAIL", "admin@ai-skill.local")
    username = os.environ.get("ADMIN_USERNAME", "admin")
    full_name = os.environ.get("ADMIN_FULL_NAME", "System Administrator")

    password = _prompt_password_if_missing()

    async with async_session_factory() as db:
        existing = await db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        if existing.scalar_one_or_none() is not None:
            logger.error("A user with that email or username already exists.")
            return 1

        admin = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        logger.info(
            "Admin user created",
            email=admin.email,
            username=admin.username,
            user_id=str(admin.id),
        )

    if settings.DEBUG:
        print(f"\n  [DEV] admin credentials: {username} / <ADMIN_PASSWORD>")
    else:
        print(
            "\n  [PROD] Admin user created. The password is NOT echoed. "
            "Store it in your secret manager now."
        )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
