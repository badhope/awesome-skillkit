import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillAnalyticsResponse(BaseModel):
    skill_id: uuid.UUID = Field(
        ...,
        description="技能 UUID",
    )
    skill_name: str = Field(
        ...,
        description="技能名称",
    )
    skill_slug: str = Field(
        ...,
        description="技能唯一标识符",
    )
    total_uses: int = Field(
        default=0,
        description="技能总使用次数",
    )
    successful_uses: int = Field(
        default=0,
        description="成功次数",
    )
    failed_uses: int = Field(
        default=0,
        description="失败次数",
    )
    success_rate: float = Field(
        default=0.0,
        description="成功率（百分比）",
    )
    avg_duration_ms: Optional[float] = Field(
        None,
        description="平均执行耗时（毫秒）",
    )
    rating_avg: float = Field(
        default=0.0,
        description="平均评分",
    )
    rating_count: int = Field(
        default=0,
        description="评分数量",
    )
    download_count: int = Field(
        default=0,
        description="下载次数",
    )
    view_count: int = Field(
        default=0,
        description="查看次数",
    )
    daily_usage: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="每日使用量数据",
        examples=[[{"date": "2026-01-01", "count": 42, "success": 38, "failed": 4}]],
    )
    top_agent_types: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="使用最多的 Agent 类型",
        examples=[[{"agent_type": "code-review-bot", "count": 120}]],
    )


class UsageTrendResponse(BaseModel):
    period_start: datetime = Field(
        ...,
        description="统计周期开始时间",
    )
    period_end: datetime = Field(
        ...,
        description="统计周期结束时间",
    )
    data_points: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="趋势数据点",
        examples=[
            [
                {"date": "2026-01-01", "total_uses": 150, "unique_skills": 25, "unique_users": 40}
            ]
        ],
    )
    total_uses: int = Field(
        default=0,
        description="总使用次数",
    )
    unique_skills_used: int = Field(
        default=0,
        description="被使用的不同技能数量",
    )
    unique_users: int = Field(
        default=0,
        description="执行操作的独立用户数量",
    )
    overall_success_rate: float = Field(
        default=0.0,
        description="总体成功率（百分比）",
    )
    avg_duration_ms: Optional[float] = Field(
        None,
        description="全局平均执行耗时（毫秒）",
    )
    growth_rate: Optional[float] = Field(
        None,
        description="相较于前一周期的增长率（百分比）",
    )


class PopularSkillsResponse(BaseModel):
    period: str = Field(
        ...,
        description="统计周期标识",
        examples=["7d", "30d", "90d", "all"],
    )
    skills: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="热门技能列表（按使用次数降序）",
        examples=[
            [
                {
                    "skill_id": "550e8400-e29b-41d4-a716-446655440000",
                    "skill_name": "Python 代码审查",
                    "skill_slug": "python-code-review",
                    "use_count": 256,
                    "rating_avg": 4.5,
                    "trend": "rising",
                }
            ]
        ],
    )
    total_skills: int = Field(
        default=0,
        description="查询周期内的技能总数",
    )


class CategoryDistributionResponse(BaseModel):
    categories: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="各分类的技能分布数据",
        examples=[
            [
                {
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "category_name": "代码审查",
                    "category_slug": "code-review",
                    "skill_count": 15,
                    "percentage": 25.0,
                    "total_uses": 450,
                    "subcategories": [
                        {
                            "category_id": "660e8400-e29b-41d4-a716-446655440000",
                            "category_name": "Python 审查",
                            "skill_count": 5,
                            "percentage": 8.3,
                            "total_uses": 180,
                        }
                    ],
                }
            ]
        ],
    )
    total_skills: int = Field(
        default=0,
        description="技能总数",
    )
    total_categories: int = Field(
        default=0,
        description="分类总数",
    )


class DashboardStatsResponse(BaseModel):
    total_skills: int = Field(
        default=0,
        description="平台技能总数",
    )
    total_users: int = Field(
        default=0,
        description="平台注册用户总数",
    )
    total_categories: int = Field(
        default=0,
        description="平台分类总数",
    )
    total_tags: int = Field(
        default=0,
        description="平台标签总数",
    )
    total_compositions: int = Field(
        default=0,
        description="平台组合总数",
    )
    total_usage_logs: int = Field(
        default=0,
        description="平台总使用记录数",
    )
    total_downloads: int = Field(
        default=0,
        description="平台总下载次数",
    )
    total_views: int = Field(
        default=0,
        description="平台总查看次数",
    )
    average_rating: float = Field(
        default=0.0,
        description="平台整体平均评分",
    )
    published_skills: int = Field(
        default=0,
        description="已发布技能数量",
    )
    active_users_today: int = Field(
        default=0,
        description="今日活跃用户数",
    )
    usage_today: int = Field(
        default=0,
        description="今日使用量",
    )
    success_rate_today: float = Field(
        default=0.0,
        description="今日成功率",
    )
    top_skills: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="本周热门技能 Top 5",
    )
    top_categories: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="最受欢迎的分类 Top 5",
    )
    recent_activities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="最新活动记录",
    )
