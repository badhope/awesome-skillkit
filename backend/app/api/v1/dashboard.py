"""Dashboard router.

Mirrors the analytics endpoints under `/v1/dashboard/*` so the frontend
can hit a stable URL family without depending on the analytics module
shape. Handlers delegate to the analytics module so we don't duplicate
SQL. The only endpoint that lives here exclusively is `recent-usage`,
which the analytics module doesn't expose and which the dashboard needs.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import analytics
from app.db import get_db
from app.models.skill import Skill, SkillUsageLog, User
from app.schemas.skill import (
    AnalyticsDashboardResponse,
    CategoryDistributionResponse,
    PopularSkillResponse,
    RecentUsageRecord,
    SkillUsageTrendResponse,
)

router = APIRouter()


@router.get("/stats", response_model=AnalyticsDashboardResponse)
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsDashboardResponse:
    """Same payload as `/v1/analytics/dashboard`. Kept as a thin
    delegate so the dashboard URL stays stable for the FE team."""
    return await analytics.get_dashboard_stats(db=db)


@router.get("/usage-trends", response_model=SkillUsageTrendResponse)
async def dashboard_usage_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> SkillUsageTrendResponse:
    return await analytics.get_skill_usage_trends(days=days, db=db)


@router.get("/category-distribution", response_model=CategoryDistributionResponse)
async def dashboard_category_distribution(
    db: AsyncSession = Depends(get_db),
) -> CategoryDistributionResponse:
    return await analytics.get_categories_distribution(db=db)


@router.get("/popular-skills", response_model=List[PopularSkillResponse])
async def dashboard_popular_skills(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> List[PopularSkillResponse]:
    return await analytics.get_popular_skills_analytics(limit=limit, db=db)


@router.get("/recent-usage", response_model=List[RecentUsageRecord])
async def dashboard_recent_usage(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[RecentUsageRecord]:
    """Latest usage log rows joined to the skill and (optionally) the user.
    Returns a denormalised shape the dashboard can render directly.
    """
    result = await db.execute(
        select(SkillUsageLog, Skill, User)
        .join(Skill, SkillUsageLog.skill_id == Skill.id)
        .outerjoin(User, SkillUsageLog.user_id == User.id)
        .order_by(SkillUsageLog.created_at.desc())
        .limit(limit)
    )
    records: List[RecentUsageRecord] = []
    for log, skill, user in result.all():
        records.append(
            RecentUsageRecord(
                id=str(log.id),
                skill_id=str(skill.id),
                skill_name=skill.name,
                skill_slug=skill.slug,
                user_id=str(user.id) if user else None,
                username=user.username if user else None,
                action=log.action,
                created_at=log.created_at,
            )
        )
    return records
