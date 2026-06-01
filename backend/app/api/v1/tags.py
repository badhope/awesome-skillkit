from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_active_user, get_current_superuser
from app.core.pagination import PaginationParams
from app.db import get_db
from app.models.skill import Skill, Tag
from app.schemas.skill import (
    SkillBriefResponse,
    TagCreate,
    TagDetailResponse,
    TagListResponse,
    TagResponse,
)

router = APIRouter()


@router.get("", response_model=TagListResponse)
async def list_tags(
    search: Optional[str] = Query(None, description="搜索标签名"),
    sort_by: str = Query("usage_count", description="排序字段"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TagListResponse:
    query = select(Tag)

    if search:
        query = query.where(Tag.name.ilike(f"%{search}%"))

    sort_column = getattr(Tag, sort_by, Tag.usage_count)
    query = query.order_by(sort_column.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)

    result = await db.execute(query)
    tags = result.scalars().all()

    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in tags],
        total=total,
    )


@router.get("/popular", response_model=List[TagResponse])
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[TagResponse]:
    query = (
        select(Tag)
        .order_by(Tag.usage_count.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    tags = result.scalars().all()
    return [TagResponse.model_validate(t) for t in tags]


@router.get("/{name}", response_model=TagDetailResponse)
async def get_tag(
    name: str,
    db: AsyncSession = Depends(get_db),
) -> TagDetailResponse:
    result = await db.execute(
        select(Tag)
        .where(Tag.name == name)
        .options(selectinload(Tag.skills))
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    response = TagDetailResponse.model_validate(tag)
    response.skills = [
        SkillBriefResponse.model_validate(s)
        for s in tag.skills
        if hasattr(s, "status") and getattr(s, "status", "published") == "published"
    ]
    return response


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    existing = await db.execute(select(Tag).where(Tag.name == tag_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists",
        )

    tag = Tag(**tag_in.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagResponse.model_validate(tag)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    name: str,
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    await db.delete(tag)
    await db.commit()