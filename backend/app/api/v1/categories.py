from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_superuser
from app.db import get_db
from app.models.skill import Category, Skill
from app.schemas.skill import (
    CategoryCreate,
    CategoryDetailResponse,
    CategoryListResponse,
    CategoryResponse,
    CategoryTreeNode,
    CategoryUpdate,
    SkillBriefResponse,
)

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    flat: bool = Query(False, description="平铺列表而非树形结构"),
    parent_id: Optional[UUID] = Query(None, description="按父分类过滤"),
    db: AsyncSession = Depends(get_db),
) -> List[CategoryResponse]:
    query = select(Category).where(Category.is_active == True)
    if parent_id is not None:
        query = query.where(Category.parent_id == parent_id)
    elif not flat:
        query = query.where(Category.parent_id.is_(None))
    query = query.order_by(Category.sort_order.asc(), Category.name.asc())

    result = await db.execute(query)
    categories = result.scalars().all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/tree", response_model=List[CategoryTreeNode])
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
) -> List[CategoryTreeNode]:
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .options(selectinload(Category.children))
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )
    all_categories = result.scalars().all()

    category_skill_counts = {}
    count_result = await db.execute(
        select(Skill.category_id, func.count(Skill.id))
        .where(Skill.category_id.isnot(None))
        .group_by(Skill.category_id)
    )
    for row in count_result:
        category_skill_counts[str(row[0])] = row[1]

    def build_tree(parent_id: Optional[UUID] = None) -> List[CategoryTreeNode]:
        nodes = []
        for cat in all_categories:
            if cat.parent_id == parent_id or (parent_id is None and cat.parent_id is None):
                cat_id_str = str(cat.id)
                node = CategoryTreeNode(
                    id=cat.id,
                    name=cat.name,
                    slug=cat.slug,
                    description=cat.description,
                    icon=cat.icon,
                    sort_order=cat.sort_order,
                    is_active=cat.is_active,
                    parent_id=cat.parent_id,
                    skill_count=category_skill_counts.get(cat_id_str, 0),
                    children=[],
                )
                children = build_tree(cat.id)
                node.children = children
                for child in children:
                    node.skill_count += child.skill_count
                nodes.append(node)
        return nodes

    return build_tree()


@router.get("/{slug}", response_model=CategoryDetailResponse)
async def get_category(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CategoryDetailResponse:
    result = await db.execute(
        select(Category)
        .where(Category.slug == slug)
        .options(selectinload(Category.children))
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    skills_result = await db.execute(
        select(Skill)
        .where(Skill.category_id == category.id, Skill.status == "published")
        .order_by(Skill.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    skills = skills_result.scalars().all()

    response = CategoryDetailResponse.model_validate(category)
    response.skills = [SkillBriefResponse.model_validate(s) for s in skills]
    response.children = [CategoryResponse.model_validate(c) for c in category.children]
    return response


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    existing = await db.execute(select(Category).where(Category.slug == category_in.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists",
        )

    if category_in.parent_id:
        parent = await db.get(Category, category_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.put("/{slug}", response_model=CategoryResponse)
async def update_category(
    slug: str,
    category_in: CategoryUpdate,
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    update_data = category_in.model_dump(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] == category.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category cannot be its own parent",
        )

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    slug: str,
    current_user=Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Category).where(Category.slug == slug))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    skill_count = await db.execute(
        select(func.count(Skill.id)).where(Skill.category_id == category.id)
    )
    if skill_count.scalar() > 0:
        await db.execute(
            select(Skill).where(Skill.category_id == category.id)
        )
        from sqlalchemy import update
        await db.execute(update(Skill).where(Skill.category_id == category.id).values(category_id=None))

    child_result = await db.execute(
        select(Category).where(Category.parent_id == category.id)
    )
    children = child_result.scalars().all()
    for child in children:
        child.parent_id = None

    await db.delete(category)
    await db.commit()