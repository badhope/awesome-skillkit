from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_active_user, get_optional_user
from app.core.pagination import PaginationParams
from app.db import get_db
from app.models.skill import (
    Category,
    Skill,
    SkillDependency,
    SkillRating,
    SkillUsageLog,
    SkillVersion,
    StatusEnum,
    Tag,
    User,
)
from app.schemas.skill import (
    SkillCreate,
    SkillDependencyCreate,
    SkillDependencyResponse,
    SkillDetailResponse,
    SkillListResponse,
    SkillRatingCreate,
    SkillRatingResponse,
    SkillResponse,
    SkillSearchResult,
    SkillSimilarResponse,
    SkillUpdate,
    SkillUsageCreate,
    SkillUsageResponse,
    SkillVersionCreate,
    SkillVersionResponse,
)
from app.services.vector_search import VectorSearchService

router = APIRouter()


def _get_vector_service() -> VectorSearchService:
    return VectorSearchService()


@router.get("", response_model=SkillListResponse)
async def list_skills(
    category_slug: Optional[str] = Query(None, description="分类slug"),
    tag: Optional[str] = Query(None, description="标签名"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    complexity: Optional[str] = Query(None, description="难度级别"),
    status: Optional[str] = Query("published", description="状态"),
    sort_by: str = Query("updated_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> SkillListResponse:
    query = select(Skill)

    if status:
        query = query.where(Skill.status == status)
    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)
    if tag:
        query = query.join(Skill.tags).where(Tag.name == tag)
    if complexity:
        query = query.where(Skill.complexity == complexity)
    if search:
        query = query.where(
            or_(
                Skill.name.ilike(f"%{search}%"),
                Skill.description.ilike(f"%{search}%"),
            )
        )

    sort_column = getattr(Skill, sort_by, Skill.updated_at)
    if pagination.order == "asc" or sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    offset = (pagination.page - 1) * pagination.page_size
    query = query.options(
        selectinload(Skill.category),
        selectinload(Skill.tags),
        selectinload(Skill.author),
    ).offset(offset).limit(pagination.page_size)

    result = await db.execute(query)
    skills = result.scalars().all()

    return SkillListResponse(
        items=[SkillResponse.model_validate(s) for s in skills],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/search", response_model=List[SkillSearchResult])
async def search_skills(
    q: str = Query(..., min_length=2, description="搜索查询"),
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[UUID] = Query(None),
    vector_service: VectorSearchService = Depends(_get_vector_service),
) -> List[SkillSearchResult]:
    results = await vector_service.search_skills(
        query=q,
        limit=limit,
        category_id=str(category_id) if category_id else None,
    )
    return [SkillSearchResult(**r) for r in results]


@router.get("/featured", response_model=List[SkillResponse])
async def get_featured_skills(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    query = (
        select(Skill)
        .where(and_(Skill.is_featured == True, Skill.status == StatusEnum.published))
        .options(selectinload(Skill.category), selectinload(Skill.tags), selectinload(Skill.author))
        .order_by(Skill.rating_avg.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    skills = result.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.get("/popular", response_model=List[SkillResponse])
async def get_popular_skills(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    query = (
        select(Skill)
        .where(Skill.status == StatusEnum.published)
        .options(selectinload(Skill.category), selectinload(Skill.tags), selectinload(Skill.author))
        .order_by(Skill.download_count.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    skills = result.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.get("/trending", response_model=List[SkillResponse])
async def get_trending_skills(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[SkillResponse]:
    recent_threshold = datetime.utcnow() - timedelta(days=30)
    usage_subq = (
        select(
            SkillUsageLog.skill_id,
            func.count(SkillUsageLog.id).label("recent_usage"),
        )
        .where(SkillUsageLog.created_at >= recent_threshold)
        .group_by(SkillUsageLog.skill_id)
        .subquery()
    )

    query = (
        select(Skill, func.coalesce(usage_subq.c.recent_usage, 0).label("recent_usage"))
        .outerjoin(usage_subq, Skill.id == usage_subq.c.skill_id)
        .where(Skill.status == StatusEnum.published)
        .options(selectinload(Skill.category), selectinload(Skill.tags), selectinload(Skill.author))
        .order_by(func.coalesce(usage_subq.c.recent_usage, 0).desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    skills = []
    for row in rows:
        skill = row[0]
        skills.append(SkillResponse.model_validate(skill))
    return skills


@router.get("/{slug}", response_model=SkillDetailResponse)
async def get_skill(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> SkillDetailResponse:
    query = (
        select(Skill)
        .where(Skill.slug == slug)
        .options(
            selectinload(Skill.category),
            selectinload(Skill.tags),
            selectinload(Skill.author),
            selectinload(Skill.versions).selectinload(SkillVersion.created_by),
            selectinload(Skill.dependencies).selectinload(SkillDependency.depends_on_skill),
        )
    )
    result = await db.execute(query)
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    skill.view_count += 1
    await db.commit()
    await db.refresh(skill)

    return SkillDetailResponse.model_validate(skill)


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    vector_service: VectorSearchService = Depends(_get_vector_service),
) -> SkillResponse:
    existing = await db.execute(select(Skill).where(Skill.slug == skill_in.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this slug already exists",
        )

    skill = Skill(
        **skill_in.model_dump(exclude={"tags", "category_slug", "complexity", "status", "metadata"}),
        complexity=skill_in.complexity or "intermediate",
        status=skill_in.status or "published",
        author_id=current_user.id,
        extra_metadata=skill_in.metadata,
    )

    if skill_in.category_slug:
        cat_result = await db.execute(select(Category).where(Category.slug == skill_in.category_slug))
        category = cat_result.scalar_one_or_none()
        if category:
            skill.category_id = category.id

    db.add(skill)
    await db.flush()

    if skill_in.tags:
        from app.models.skill import skill_tag_association
        for tag_name in skill_in.tags:
            tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = tag_result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()
            else:
                tag.usage_count += 1
            await db.execute(
                skill_tag_association.insert().values(
                    skill_id=skill.id, tag_id=tag.id
                )
            )

    await db.commit()

    result = await db.execute(
        select(Skill)
        .where(Skill.id == skill.id)
        .options(
            selectinload(Skill.category),
            selectinload(Skill.tags),
            selectinload(Skill.author),
        )
    )
    skill = result.scalar_one()

    await vector_service.index_skill(_skill_to_dict(skill))

    return SkillResponse.model_validate(skill)


@router.put("/{slug}", response_model=SkillResponse)
async def update_skill(
    slug: str,
    skill_in: SkillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    vector_service: VectorSearchService = Depends(_get_vector_service),
) -> SkillResponse:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    update_data = skill_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tags":
            from app.models.skill import skill_tag_association
            await db.execute(
                skill_tag_association.delete().where(
                    skill_tag_association.c.skill_id == skill.id
                )
            )
            for tag_name in value:
                tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
                tag = tag_result.scalar_one_or_none()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    await db.flush()
                else:
                    tag.usage_count += 1
                await db.execute(
                    skill_tag_association.insert().values(
                        skill_id=skill.id, tag_id=tag.id
                    )
                )
        elif field == "category_slug":
            if value:
                cat_result = await db.execute(select(Category).where(Category.slug == value))
                category = cat_result.scalar_one_or_none()
                skill.category_id = category.id if category else None
        elif field == "metadata":
            skill.extra_metadata = value
        else:
            setattr(skill, field, value)

    await db.commit()

    result = await db.execute(
        select(Skill)
        .where(Skill.id == skill.id)
        .options(
            selectinload(Skill.category),
            selectinload(Skill.tags),
            selectinload(Skill.author),
        )
    )
    skill = result.scalar_one()

    await vector_service.index_skill(_skill_to_dict(skill))

    return SkillResponse.model_validate(skill)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    vector_service: VectorSearchService = Depends(_get_vector_service),
) -> None:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    skill_id_str = str(skill.id)
    await db.delete(skill)
    await db.commit()

    await vector_service.delete_skill_index(skill_id_str)


@router.get("/{slug}/versions", response_model=List[SkillVersionResponse])
async def list_versions(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> List[SkillVersionResponse]:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    ver_result = await db.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill.id)
        .options(selectinload(SkillVersion.created_by))
        .order_by(SkillVersion.created_at.desc())
    )
    versions = ver_result.scalars().all()
    return [SkillVersionResponse.model_validate(v) for v in versions]


@router.post("/{slug}/versions", response_model=SkillVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    slug: str,
    version_in: SkillVersionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SkillVersionResponse:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    existing = await db.execute(
        select(SkillVersion).where(
            and_(SkillVersion.skill_id == skill.id, SkillVersion.version == version_in.version)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Version already exists",
        )

    version = SkillVersion(
        skill_id=skill.id,
        version=version_in.version,
        content=version_in.content,
        changelog=version_in.changelog,
        created_by_id=current_user.id,
    )
    db.add(version)

    skill.version = version_in.version
    skill.content = version_in.content

    await db.commit()
    await db.refresh(version)

    return SkillVersionResponse.model_validate(version)


@router.get("/{slug}/dependencies", response_model=List[SkillDependencyResponse])
async def list_dependencies(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> List[SkillDependencyResponse]:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    dep_result = await db.execute(
        select(SkillDependency)
        .where(SkillDependency.skill_id == skill.id)
        .options(selectinload(SkillDependency.depends_on_skill))
        .order_by(SkillDependency.created_at.desc())
    )
    deps = dep_result.scalars().all()
    return [SkillDependencyResponse.model_validate(d) for d in deps]


@router.post("/{slug}/dependencies", response_model=SkillDependencyResponse, status_code=status.HTTP_201_CREATED)
async def add_dependency(
    slug: str,
    dep_in: SkillDependencyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SkillDependencyResponse:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    dep_skill_result = await db.execute(select(Skill).where(Skill.slug == dep_in.depends_on_skill_slug))
    dep_skill = dep_skill_result.scalar_one_or_none()
    if not dep_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency skill not found",
        )

    existing = await db.execute(
        select(SkillDependency).where(
            and_(
                SkillDependency.skill_id == skill.id,
                SkillDependency.depends_on_skill_id == dep_skill.id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dependency already exists",
        )

    dependency = SkillDependency(
        skill_id=skill.id,
        depends_on_skill_id=dep_skill.id,
        version_constraint=dep_in.version_constraint,
    )
    db.add(dependency)
    await db.commit()
    await db.refresh(dependency)

    await db.refresh(dependency, ["depends_on_skill"])

    return SkillDependencyResponse.model_validate(dependency)


@router.delete("/{slug}/dependencies/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_dependency(
    slug: str,
    dep_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    if skill.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    dep_result = await db.execute(
        select(SkillDependency).where(
            and_(SkillDependency.id == dep_id, SkillDependency.skill_id == skill.id)
        )
    )
    dependency = dep_result.scalar_one_or_none()
    if not dependency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dependency not found")

    await db.delete(dependency)
    await db.commit()


@router.get("/{slug}/similar", response_model=List[SkillSimilarResponse])
async def find_similar_skills(
    slug: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    vector_service: VectorSearchService = Depends(_get_vector_service),
) -> List[SkillSimilarResponse]:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    similar = await vector_service.find_similar_skills(str(skill.id), limit=limit)
    return [SkillSimilarResponse(**s) for s in similar]


@router.post("/{slug}/rate", response_model=SkillRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_skill(
    slug: str,
    rating_in: SkillRatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SkillRatingResponse:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    existing_rating = await db.execute(
        select(SkillRating).where(
            and_(SkillRating.skill_id == skill.id, SkillRating.user_id == current_user.id)
        )
    )
    rating_obj = existing_rating.scalar_one_or_none()

    if rating_obj:
        rating_obj.rating = rating_in.rating
        rating_obj.comment = rating_in.comment
    else:
        rating_obj = SkillRating(
            skill_id=skill.id,
            user_id=current_user.id,
            rating=rating_in.rating,
            comment=rating_in.comment,
        )
        db.add(rating_obj)

    await db.flush()

    all_ratings = await db.execute(
        select(func.avg(SkillRating.rating), func.count(SkillRating.id)).where(
            SkillRating.skill_id == skill.id
        )
    )
    avg_rating, rating_count = all_ratings.one()
    skill.rating_avg = float(avg_rating) if avg_rating else 0.0
    skill.rating_count = rating_count or 0

    await db.commit()

    result = await db.execute(
        select(SkillRating)
        .where(SkillRating.id == rating_obj.id)
        .options(selectinload(SkillRating.user))
    )
    rating_obj = result.scalar_one()

    return SkillRatingResponse.model_validate(rating_obj)


@router.post("/{slug}/use", response_model=SkillUsageResponse, status_code=status.HTTP_201_CREATED)
async def log_skill_usage(
    slug: str,
    usage_in: SkillUsageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SkillUsageResponse:
    result = await db.execute(select(Skill).where(Skill.slug == slug))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    usage_log = SkillUsageLog(
        skill_id=skill.id,
        user_id=current_user.id,
        action=usage_in.action,
    )
    db.add(usage_log)

    skill.usage_count += 1
    if usage_in.action == "download":
        skill.download_count += 1

    await db.commit()
    await db.refresh(usage_log)

    return SkillUsageResponse.model_validate(usage_log)


def _skill_to_dict(skill: Skill) -> dict:
    return {
        "id": str(skill.id),
        "name": skill.name,
        "description": skill.description or "",
        "category_id": str(skill.category_id) if skill.category_id else "",
        "tags": [t.name for t in skill.tags] if skill.tags else [],
        "is_public": skill.is_public,
        "version": skill.version,
        "author": skill.author.username if skill.author else "",
        "usage_count": skill.usage_count,
        "rating": skill.rating_avg,
        "content": str(skill.content) if skill.content else "",
        "created_at": skill.created_at.isoformat() if skill.created_at else "",
        "updated_at": skill.updated_at.isoformat() if skill.updated_at else "",
    }