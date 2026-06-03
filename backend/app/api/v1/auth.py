from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_event
from app.core.config import settings
from app.core.deps import get_current_active_user
from app.core.i18n import _, localized_http_exception
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    set_auth_cookies,
    verify_password,
)
from app.db import get_db
from app.models.skill import User
from app.schemas.skill import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPasswordChange,
    UserResponse,
    UserUpdateMe,
)

router = APIRouter()

# Single hand-picked list — used by both the API and the admin bootstrap
# script (was previously inconsistent between the two — #15).
WEAK_PASSWORDS = {
    "password",
    "12345678",
    "123456789",
    "qwerty",
    "abc123",
    "password1",
    "11111111",
    "admin",
    "admin1234",
    "changeme",
    "letmein",
    "welcome",
    "iloveyou",
}


def _get_client_ip(request: Optional[Request]) -> Optional[str]:
    if request is None or request.client is None:
        return None
    return request.client.host


def _is_password_strong(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if password.lower() in WEAK_PASSWORDS:
        return False
    return True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    existing_email = await db.execute(select(User).where(User.email == user_in.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = await db.execute(select(User).where(User.username == user_in.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    if not _is_password_strong(user_in.password):
        log_event(
            event="register_weak_password",
            user_id=None,
            ip=_get_client_ip(request),
            email=user_in.email,
            username=user_in.username,
            outcome="rejected",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too weak. Must be at least 8 characters with uppercase, lowercase, and digit.",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log_event(
        event="register_success",
        user_id=str(user.id),
        ip=_get_client_ip(request),
        email=user.email,
        username=user.username,
        outcome="success",
    )

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()
    client_ip = _get_client_ip(request)

    if not user or not verify_password(login_data.password, user.hashed_password):
        # FIXME: no per-account lockout yet. The rate-limit middleware throttles
        # by IP, but a targeted attack against a single account from a botnet
        # would slip past. Plan is to count consecutive failures on the user
        # row and lock for 15min after 10 in a row. Tracked in #142.
        log_event(
            event="login_failure",
            user_id=None,
            ip=client_ip,
            attempted_username=login_data.username,
            outcome="failure",
        )
        raise localized_http_exception(
            request, status.HTTP_401_UNAUTHORIZED, "Invalid username or password."
        )

    if not user.is_active:
        log_event(
            event="login_inactive_user",
            user_id=str(user.id),
            ip=client_ip,
            attempted_username=login_data.username,
            outcome="failure",
        )
        raise localized_http_exception(
            request, status.HTTP_403_FORBIDDEN, "Inactive user."
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # Set HttpOnly cookies. We still return the tokens in the response
    # body so non-browser clients (curl, mobile) can keep working.
    set_auth_cookies(response, access_token, refresh_token)

    log_event(
        event="login_success",
        user_id=str(user.id),
        ip=client_ip,
        username=user.username,
        outcome="success",
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Rotate the access token.

    The refresh token may come from EITHER the request body (old API
    clients) OR the HttpOnly cookie. We accept both to keep the
    transition non-breaking."""
    body = None
    try:
        body = await request.json()
    except Exception:
        body = None
    refresh_str: Optional[str] = None
    if isinstance(body, dict):
        refresh_str = body.get("refresh_token")
    if not refresh_str:
        refresh_str = request.cookies.get("refresh_token")
    if not refresh_str:
        raise localized_http_exception(
            request, status.HTTP_401_UNAUTHORIZED, "Missing refresh token."
        )

    try:
        payload = decode_token(refresh_str)
        if payload.get("type") != "refresh":
            raise localized_http_exception(
                request, status.HTTP_401_UNAUTHORIZED, "Invalid refresh token."
            )
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise localized_http_exception(
                request, status.HTTP_401_UNAUTHORIZED, "Invalid refresh token."
            )
        user_id = UUID(user_id_str)
    except JWTError:
        raise localized_http_exception(
            request, status.HTTP_401_UNAUTHORIZED, "Invalid refresh token."
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise localized_http_exception(
            request, status.HTTP_401_UNAUTHORIZED, "User not found or inactive."
        )

    new_access = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))
    set_auth_cookies(response, new_access, new_refresh)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    log_event(
        event="logout_success",
        user_id=str(current_user.id),
        ip=_get_client_ip(request),
        username=current_user.username,
        outcome="success",
    )
    clear_auth_cookies(response)
    locale = getattr(request.state, "locale", "en")
    return {"message": _("Successfully logged out.", locale)}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdateMe,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    update_data = user_in.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    if "username" in update_data:
        existing = await db.execute(
            select(User).where(User.username == update_data["username"], User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserPasswordChange,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise localized_http_exception(
            request, status.HTTP_400_BAD_REQUEST, "Current password is incorrect."
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    locale = getattr(request.state, "locale", "en")
    return {"message": _("Password changed successfully", locale)}
