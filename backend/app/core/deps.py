"""FastAPI auth dependencies.

The `get_current_user` dependency accepts a JWT from EITHER:
  - the `Authorization: Bearer <token>` header (good for API clients, tests)
  - the `access_token` HttpOnly cookie (the default for browser users)

This dual-source approach lets us phase out the localStorage-stored
token without breaking existing API clients in one shot.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.i18n import localized_http_exception
from app.core.security import ACCESS_TOKEN_COOKIE, decode_token
from app.db import get_db
from app.models.skill import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False
)


def _extract_token(request: Request, header_token: Optional[str]) -> Optional[str]:
    """Header wins if present (curl, server-to-server), otherwise
    fall back to the HttpOnly cookie (browser)."""
    if header_token:
        return header_token
    return request.cookies.get(ACCESS_TOKEN_COOKIE)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    token = _extract_token(request, header_token)
    if token is None:
        raise localized_http_exception(
            request,
            status.HTTP_401_UNAUTHORIZED,
            "Not authenticated.",
            extra_headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
        user_id: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if user_id is None or token_type != "access":
            raise localized_http_exception(
                request,
                status.HTTP_401_UNAUTHORIZED,
                "Invalid authentication credentials.",
                extra_headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise localized_http_exception(
            request,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication credentials.",
            extra_headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
    except (ValueError, TypeError):
        raise localized_http_exception(
            request,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication credentials.",
            extra_headers={"WWW-Authenticate": "Bearer"},
        )
    user = result.scalar_one_or_none()

    if user is None:
        raise localized_http_exception(
            request,
            status.HTTP_401_UNAUTHORIZED,
            "User not found.",
            extra_headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise localized_http_exception(
            request, status.HTTP_403_FORBIDDEN, "Inactive user."
        )
    return user


async def get_current_active_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise localized_http_exception(
            request, status.HTTP_403_FORBIDDEN, "Inactive user."
        )
    return current_user


async def get_current_superuser(
    request: Request,
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise localized_http_exception(
            request, status.HTTP_403_FORBIDDEN, "Not enough permissions."
        )
    return current_user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    header_token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    token = _extract_token(request, header_token)
    if token is None:
        return None
    try:
        payload = decode_token(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            return None
        try:
            result = await db.execute(
                select(User).where(User.id == UUID(user_id))
            )
        except (ValueError, TypeError):
            return None
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None
    except (JWTError, ValidationError):
        return None
