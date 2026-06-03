from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_superuser
from app.db import get_db
from app.models.skill import Skill, User
from app.schemas.skill import (
    SkillResponse,
    UserListResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    search: str = Query(None, description="搜索用户名或邮箱"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    query = select(User)

    if search:
        query = query.where(
            User.username.ilike(f"%{escape_like(search)}%", escape="\\")
            | User.email.ilike(f"%{escape_like(search)}%", escape="\\")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_validate(user)


@router.get("/{username}/skills", response_model=List[SkillResponse])
async def get_user_skills(
    username: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Skill)
        .where(Skill.author_id == user.id)
        .options(selectinload(Skill.category), selectinload(Skill.tags), selectinload(Skill.author))
        .order_by(Skill.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    skills = result.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.put("/{username}", response_model=UserResponse)
async def update_user(
    username: str,
    user_in: UserUpdate,
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # The `User` SQLAlchemy model has no `metadata` / `metadata_`
    # column, and the `metadata` attribute on a DeclarativeBase class
    # resolves to the internal `MetaData()` registry. Drop the field
    # silently if a caller sent it — there's nothing to persist and
    # setting it on the instance would shadow the registry for no
    # reason.
    update_data = user_in.model_dump(exclude_unset=True)
    update_data.pop("metadata_", None)

    if "email" in update_data:
        existing = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    if "username" in update_data:
        existing = await db.execute(
            select(User).where(User.username == update_data["username"], User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)
