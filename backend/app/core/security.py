"""Password hashing, JWT issuance/verification, and cookie helpers.

This is the single source of truth for credential operations. Other
modules should import from here instead of re-implementing the same
logic (which was a long-standing duplication bug — three different
`create_access_token` implementations existed, each with subtly
different bug-fixes applied).
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import UUID, uuid4

from fastapi import Response
from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Note: a single CryptContext instance is shared across the whole app
# (auth API, seed script, admin-bootstrap script). Previously each
# module created its own, which meant the deprecated="auto" upgrade
# only ever triggered in the module that *issued* the hash, not in
# the one that *verified* it.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cookie names — frontend reads `httpOnly` so it doesn't even need
# to know these, but we keep them stable for ops/debugging.
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

# Sensible defaults for the cookie attributes. In production we want
# Secure + SameSite=Lax; in dev (localhost http) we relax Secure so
# the browser still accepts the cookie.
COOKIE_SECURE = not settings.DEBUG
COOKIE_SAMESITE = "lax"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _build_claims(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta],
    token_type: str,
) -> dict[str, Any]:
    """Compose the JWT claim set. `iat` + `jti` are always present
    so we can later add a redis-backed revoke list without changing
    the on-the-wire format."""
    now = datetime.now(timezone.utc)
    if expires_delta is None:
        if token_type == "access":
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return {
        "sub": str(subject),
        "exp": now + expires_delta,
        "iat": now,
        "jti": uuid4().hex,
        "type": token_type,
    }


def create_access_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    claims = _build_claims(subject, expires_delta, "access")
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None,
) -> str:
    claims = _build_claims(subject, expires_delta, "refresh")
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode + verify a JWT. Raises `jose.JWTError` on any failure.

    The router layer wraps this in its own `localized_http_exception`
    so error messages come out in the request's locale; the raw
    exception is intentionally not i18n-aware so log entries stay
    grep-friendly."""
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Attach JWTs as HttpOnly cookies. JS can't read these, which
    kills the XSS -> token-steal attack chain that comes with storing
    tokens in `localStorage`."""
    access_max = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=access_max,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=refresh_max,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=f"{settings.API_PREFIX}/auth",  # only sent to /auth
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path=f"{settings.API_PREFIX}/auth")


__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "set_auth_cookies",
    "clear_auth_cookies",
    "ACCESS_TOKEN_COOKIE",
    "REFRESH_TOKEN_COOKIE",
]
