import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        description="用户邮箱地址",
        examples=["user@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=150,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="用户名",
        examples=["alice_dev"],
    )
    is_active: bool = Field(
        default=True,
        description="账户是否激活",
    )
    is_superuser: bool = Field(
        default=False,
        description="是否为超级用户",
    )
    metadata_: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="metadata",
        description="用户额外元数据",
        examples=[{"department": "engineering", "role": "senior"}],
    )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="用户密码",
        examples=["SecureP@ssw0rd!"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="显示名（可选）",
        examples=["Alice Wang"],
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        import re

        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", v):
            raise ValueError("密码必须包含至少一个特殊字符")
        return v


class UserUpdate(BaseModel):
    """Admin-facing full user update. Unlike `UserUpdateMe` (which is
    limited to display fields), this schema lets a superuser flip
    `is_active` / `is_superuser` and edit the profile too.

    NOTE: the `metadata` field that used to live here was removed
    — the `User` SQLAlchemy model has no `metadata` column, so the
    request would be accepted silently and the value dropped on the
    floor. Use a dedicated `user_metadata` column if we ever need
    one; the alias below would just shadow the internal
    `Base.metadata` registry and not persist anything.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="用户邮箱地址",
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="用户名",
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="显示名",
    )
    avatar_url: Optional[str] = Field(
        None,
        max_length=500,
        description="头像 URL",
    )
    bio: Optional[str] = Field(
        None,
        max_length=2000,
        description="个人简介",
    )
    is_active: Optional[bool] = Field(
        None,
        description="账户是否激活",
    )
    is_superuser: Optional[bool] = Field(
        None,
        description="是否为超级用户",
    )


class UserResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="用户 UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    email: str = Field(
        ...,
        description="用户邮箱地址",
    )
    username: str = Field(
        ...,
        description="用户名",
    )
    is_active: bool = Field(
        ...,
        description="账户是否激活",
    )
    is_superuser: bool = Field(
        ...,
        description="是否为超级用户",
    )
    role: str = Field(
        default="user",
        description="角色：user / moderator / admin",
    )
    is_verified: bool = Field(
        default=False,
        description="邮箱是否已验证",
    )
    full_name: Optional[str] = Field(
        default=None,
        description="显示名",
    )
    avatar_url: Optional[str] = Field(
        default=None,
        description="头像 URL",
    )
    bio: Optional[str] = Field(
        default=None,
        description="个人简介",
    )
    # NOTE: UserResponse intentionally omits the `metadata` field. The
    # SQLAlchemy `User` model does not have a `metadata` column; the
    # `metadata` attribute on a SQLAlchemy `DeclarativeBase` subclass
    # resolves to the internal `MetaData()` registry, which pydantic
    # cannot coerce to dict. If we ever need a JSON metadata column on
    # users, add it explicitly as `user_metadata` (mapped_column with
    # column name `user_metadata`) and expose it here under that name.
    created_at: datetime = Field(
        ...,
        description="注册时间",
    )
    updated_at: datetime = Field(
        ...,
        description="最后更新时间",
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="用户邮箱地址",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="用户密码",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT 访问令牌",
    )
    refresh_token: str = Field(
        ...,
        description="JWT 刷新令牌",
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
    )
    expires_in: int = Field(
        ...,
        description="访问令牌过期时间（秒）",
        examples=[3600],
    )


class TokenRefresh(BaseModel):
    refresh_token: str = Field(
        ...,
        min_length=1,
        description="刷新令牌",
    )


class PasswordChange(BaseModel):
    current_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="当前密码",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密码",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        import re

        if not re.search(r"[A-Z]", v):
            raise ValueError("新密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("新密码必须包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("新密码必须包含至少一个数字")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", v):
            raise ValueError("新密码必须包含至少一个特殊字符")
        return v


class PasswordReset(BaseModel):
    email: EmailStr = Field(
        ...,
        description="接收重置链接的邮箱地址",
    )
