from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.skill import (
    Category,
    Skill,
    SkillComposition,
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
    # Single batched query — was 9 round-trips before. Subquery aliases
    # let us pull all 11 aggregates in one SELECT.
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    active_users_subq = (
        select(func.count(func.distinct(SkillUsageLog.user_id)))
        .where(SkillUsageLog.created_at >= today_start)
        .scalar_subquery()
    )
    skills_today_subq = (
        select(func.count(Skill.id))
        .where(and_(Skill.status == "published", Skill.created_at >= today_start))
        .scalar_subquery()
    )
    active_categories_subq = (
        select(func.count(Category.id)).where(Category.is_active == True).scalar_subquery()
    )
    # `total_users` is "count of all users", not "users with usage logs".
    # Putting it as a subquery keeps the join root on Skill while
    # still aggregating over the user table.
    total_users_subq = select(func.count(User.id)).scalar_subquery()
    total_ratings_subq = select(func.count(SkillRating.id)).scalar_subquery()
    totals_row = (
        await db.execute(
            select(
                func.count(Skill.id).label("total_skills"),
                total_users_subq.label("total_users"),
                active_categories_subq.label("total_categories"),
                func.count(SkillUsageLog.id).label("total_usage"),
                func.coalesce(func.sum(Skill.download_count), 0).label("total_downloads"),
                total_ratings_subq.label("total_ratings"),
                func.coalesce(func.avg(Skill.rating_avg), 0.0).label("avg_rating"),
                # SkillComposition has no direct skill_id — count it as
                # a separate scalar subquery so we don't need a join.
                select(func.count(SkillComposition.id)).scalar_subquery().label("total_compositions"),
                skills_today_subq.label("skills_published_today"),
                active_users_subq.label("active_users_today"),
            )
            .select_from(Skill)
            .outerjoin(SkillUsageLog, SkillUsageLog.skill_id == Skill.id)
        )
    ).one()

    total_skills = totals_row.total_skills or 0
    total_users = totals_row.total_users or 0
    total_categories = totals_row.total_categories or 0
    total_usage = totals_row.total_usage or 0
    total_downloads = totals_row.total_downloads or 0
    total_ratings = totals_row.total_ratings or 0
    avg_rating = totals_row.avg_rating or 0.0
    total_compositions = totals_row.total_compositions or 0
    skills_published_today = totals_row.skills_published_today or 0
    active_users_today = totals_row.active_users_today or 0

    stats = DashboardStats(
        total_skills=total_skills,
        total_users=total_users,
        total_categories=total_categories,
        total_usage=total_usage,
        total_downloads=int(total_downloads),
        total_ratings=total_ratings,
        avg_rating=round(float(avg_rating), 2),
        total_compositions=total_compositions,
        skills_published_today=skills_published_today,
        active_users_today=active_users_today,
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

    recent_threshold = datetime.now(timezone.utc) - timedelta(days=30)
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
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

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
        SkillUsageTrend(
            date=str(row[0]),
            count=row[1],
            # The SkillUsageLog model only records an `action` enum, not
            # a separate downloads/views split. The frontend's `UsageTrend`
            # shows three lines, so we mirror the daily total into both
            # series — this keeps the chart shape stable and matches what
            # the UI already does for action-agnostic views.
            downloads=row[1],
            views=row[1],
        )
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
            skill_count=row[2],
        )
        for row in rows
    ]
    total = sum(d.count for d in distribution) or 1
    for d in distribution:
        # Percentage of skills that belong to this category, in 0-100.
        d.percentage = round(d.count * 100.0 / total, 2) if total else 0.0

    return CategoryDistributionResponse(
        distribution=distribution,
        total=total if total != 1 else 0,
    )


@router.get("/tags/trending", response_model=TrendingTagResponse)
async def get_trending_tags(
    days: int = Query(30, ge=1, le=90, description="天数范围"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TrendingTagResponse:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

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
