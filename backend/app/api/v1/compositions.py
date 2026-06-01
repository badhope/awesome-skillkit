from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_active_user
from app.db import get_db
from app.models.skill import Skill, SkillComposition, SkillCompositionItem, User
from app.schemas.skill import (
    CompositionCreate,
    CompositionDetailResponse,
    CompositionItemCreate,
    CompositionItemResponse,
    CompositionListResponse,
    CompositionResponse,
    CompositionUpdate,
)

router = APIRouter()


@router.get("", response_model=CompositionListResponse)
async def list_compositions(
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CompositionListResponse:
    query = select(SkillComposition).where(SkillComposition.is_public == True)

    if search:
        query = query.where(
            SkillComposition.name.ilike(f"%{search}%")
            | SkillComposition.description.ilike(f"%{search}%")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        query.options(selectinload(SkillComposition.owner))
        .order_by(SkillComposition.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    compositions = result.scalars().all()

    return CompositionListResponse(
        items=[CompositionResponse.model_validate(c) for c in compositions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=CompositionDetailResponse)
async def get_composition(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> CompositionDetailResponse:
    result = await db.execute(
        select(SkillComposition)
        .where(SkillComposition.slug == slug)
        .options(
            selectinload(SkillComposition.owner),
            selectinload(SkillComposition.items).selectinload(SkillCompositionItem.skill),
        )
    )
    composition = result.scalar_one_or_none()
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition not found",
        )

    return CompositionDetailResponse.model_validate(composition)


@router.post("", response_model=CompositionResponse, status_code=status.HTTP_201_CREATED)
async def create_composition(
    comp_in: CompositionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CompositionResponse:
    existing = await db.execute(
        select(SkillComposition).where(SkillComposition.slug == comp_in.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Composition with this slug already exists",
        )

    composition = SkillComposition(
        **comp_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(composition)
    await db.commit()
    await db.refresh(composition)
    await db.refresh(composition, ["owner"])

    return CompositionResponse.model_validate(composition)


@router.put("/{slug}", response_model=CompositionResponse)
async def update_composition(
    slug: str,
    comp_in: CompositionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CompositionResponse:
    result = await db.execute(
        select(SkillComposition)
        .where(SkillComposition.slug == slug)
        .options(selectinload(SkillComposition.owner))
    )
    composition = result.scalar_one_or_none()
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition not found",
        )

    if composition.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    update_data = comp_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(composition, field, value)

    await db.commit()
    await db.refresh(composition)

    return CompositionResponse.model_validate(composition)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_composition(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(SkillComposition).where(SkillComposition.slug == slug)
    )
    composition = result.scalar_one_or_none()
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition not found",
        )

    if composition.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    await db.delete(composition)
    await db.commit()


@router.post("/{slug}/items", response_model=CompositionItemResponse, status_code=status.HTTP_201_CREATED)
async def add_composition_item(
    slug: str,
    item_in: CompositionItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CompositionItemResponse:
    result = await db.execute(
        select(SkillComposition).where(SkillComposition.slug == slug)
    )
    composition = result.scalar_one_or_none()
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition not found",
        )

    if composition.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    skill_result = await db.execute(
        select(Skill).where(Skill.slug == item_in.skill_slug)
    )
    skill = skill_result.scalar_one_or_none()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    existing_item = await db.execute(
        select(SkillCompositionItem).where(
            and_(
                SkillCompositionItem.composition_id == composition.id,
                SkillCompositionItem.skill_id == skill.id,
            )
        )
    )
    if existing_item.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already in composition",
        )

    item = SkillCompositionItem(
        composition_id=composition.id,
        skill_id=skill.id,
        sort_order=item_in.sort_order,
        notes=item_in.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    await db.refresh(item, ["skill"])

    return CompositionItemResponse.model_validate(item)


@router.delete("/{slug}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_composition_item(
    slug: str,
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(SkillComposition).where(SkillComposition.slug == slug)
    )
    composition = result.scalar_one_or_none()
    if not composition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition not found",
        )

    if composition.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    item_result = await db.execute(
        select(SkillCompositionItem).where(
            and_(
                SkillCompositionItem.id == item_id,
                SkillCompositionItem.composition_id == composition.id,
            )
        )
    )
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Composition item not found",
        )

    await db.delete(item)
    await db.commit()