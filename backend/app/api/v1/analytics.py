from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.skill import (
    Category,
    Skill,
    SkillRating,
    SkillUsageLog,
    Tag,
    User,
)
from app.schemas.skill import (
    AnalyticsDashboardResponse,
    CategoryDistribution,
    CategoryDistributionResponse,
    DashboardStats,
    PopularSkillResponse,
    SkillUsageTrend,
    SkillUsageTrendResponse,
    TrendingTag,
    TrendingTagResponse,
)

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsDashboardResponse:
    total_skills_result = await db.execute(select(func.count(Skill.id)))
    total_skills = total_skills_result.scalar() or 0

    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    total_categories_result = await db.execute(
        select(func.count(Category.id)).where(Category.is_active == True)
    )
    total_categories = total_categories_result.scalar() or 0

    total_usage_result = await db.execute(select(func.count(SkillUsageLog.id)))
    total_usage = total_usage_result.scalar() or 0

    total_downloads_result = await db.execute(
        select(func.sum(Skill.download_count))
    )
    total_downloads = total_downloads_result.scalar() or 0

    total_ratings_result = await db.execute(select(func.count(SkillRating.id)))
    total_ratings = total_ratings_result.scalar() or 0

    avg_rating_result = await db.execute(select(func.avg(Skill.rating_avg)))
    avg_rating = avg_rating_result.scalar() or 0.0

    stats = DashboardStats(
        total_skills=total_skills,
        total_users=total_users,
        total_categories=total_categories,
        total_usage=total_usage,
        total_downloads=int(total_downloads),
        total_ratings=total_ratings,
        avg_rating=round(float(avg_rating), 2),
    )

    popular_result = await db.execute(
        select(Skill, Category.name.label("category_name"))
        .outerjoin(Category, Skill.category_id == Category.id)
        .where(Skill.status == "published")
        .order_by(Skill.download_count.desc())
        .limit(5)
    )
    popular_rows = popular_result.all()
    popular_skills = [
        PopularSkillResponse(
            id=row[0].id,
            name=row[0].name,
            slug=row[0].slug,
            description=row[0].description,
            download_count=row[0].download_count,
            usage_count=row[0].usage_count,
            rating_avg=row[0].rating_avg,
            rating_count=row[0].rating_count,
            category_name=row[1],
        )
        for row in popular_rows
    ]

    recent_threshold = datetime.utcnow() - timedelta(days=30)
    tag_usage_subq = (
        select(
            Tag.name,
            Tag.usage_count,
            func.count(SkillUsageLog.id).label("recent_usage"),
        )
        .select_from(Tag)
        .join(Tag.skills)
        .join(SkillUsageLog, SkillUsageLog.skill_id == Skill.id)
        .where(SkillUsageLog.created_at >= recent_threshold)
        .group_by(Tag.name, Tag.usage_count)
        .order_by(func.count(SkillUsageLog.id).desc())
        .limit(10)
    )
    tag_rows = (await db.execute(tag_usage_subq)).all()
    trending_tags = [
        TrendingTag(name=row[0], usage_count=row[1], recent_usage=row[2])
        for row in tag_rows
    ]

    return AnalyticsDashboardResponse(
        stats=stats,
        popular_skills=popular_skills,
        trending_tags=trending_tags,
    )


@router.get("/skills/usage", response_model=SkillUsageTrendResponse)
async def get_skill_usage_trends(
    days: int = Query(30, ge=1, le=365, description="天数范围"),
    db: AsyncSession = Depends(get_db),
) -> SkillUsageTrendResponse:
    start_date = datetime.utcnow() - timedelta(days=days)

    trend_data = await db.execute(
        select(
            func.date(SkillUsageLog.created_at).label("date"),
            func.count(SkillUsageLog.id).label("count"),
        )
        .where(SkillUsageLog.created_at >= start_date)
        .group_by(func.date(SkillUsageLog.created_at))
        .order_by(text("date"))
    )
    rows = trend_data.all()

    trend = [
        SkillUsageTrend(date=str(row[0]), count=row[1])
        for row in rows
    ]

    return SkillUsageTrendResponse(
        trend=trend,
        period=f"last_{days}_days",
    )


@router.get("/skills/popular", response_model=List[PopularSkillResponse])
async def get_popular_skills_analytics(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[PopularSkillResponse]:
    result = await db.execute(
        select(Skill, Category.name.label("category_name"))
        .outerjoin(Category, Skill.category_id == Category.id)
        .where(Skill.status == "published")
        .order_by(Skill.download_count.desc())
        .limit(limit)
    )
    rows = result.all()

    return [
        PopularSkillResponse(
            id=row[0].id,
            name=row[0].name,
            slug=row[0].slug,
            description=row[0].description,
            download_count=row[0].download_count,
            usage_count=row[0].usage_count,
            rating_avg=row[0].rating_avg,
            rating_count=row[0].rating_count,
            category_name=row[1],
        )
        for row in rows
    ]


@router.get("/categories/distribution", response_model=CategoryDistributionResponse)
async def get_categories_distribution(
    db: AsyncSession = Depends(get_db),
) -> CategoryDistributionResponse:
    result = await db.execute(
        select(
            Category.name,
            Category.slug,
            func.count(Skill.id).label("count"),
        )
        .outerjoin(Skill, and_(Skill.category_id == Category.id, Skill.status == "published"))
        .where(Category.is_active == True)
        .group_by(Category.id, Category.name, Category.slug)
        .order_by(func.count(Skill.id).desc())
    )
    rows = result.all()

    distribution = [
        CategoryDistribution(
            category_name=row[0],
            category_slug=row[1],
            count=row[2],
        )
        for row in rows
    ]
    total = sum(d.count for d in distribution)

    return CategoryDistributionResponse(
        distribution=distribution,
        total=total,
    )


@router.get("/tags/trending", response_model=TrendingTagResponse)
async def get_trending_tags(
    days: int = Query(30, ge=1, le=90, description="天数范围"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TrendingTagResponse:
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Tag.name,
            Tag.usage_count,
            func.count(SkillUsageLog.id).label("recent_usage"),
        )
        .select_from(Tag)
        .join(Tag.skills)
        .join(SkillUsageLog, SkillUsageLog.skill_id == Skill.id)
        .where(SkillUsageLog.created_at >= start_date)
        .group_by(Tag.name, Tag.usage_count)
        .order_by(func.count(SkillUsageLog.id).desc())
        .limit(limit)
    )
    rows = result.all()

    tags = [
        TrendingTag(name=row[0], usage_count=row[1], recent_usage=row[2])
        for row in rows
    ]

    return TrendingTagResponse(tags=tags)