# ruff: noqa: I001
#
# `from __future__ import annotations` MUST be the first non-docstring
# statement in the file (Python compiler requirement), so it cannot
# share an import block with the rest of the imports. Disable the
# import-ordering rule locally — this is the only file in the project
# where it's needed.
"""Skill-related Pydantic schemas.

This module historically grew to also hold User, Tag, Category, Token,
Composition, Analytics, etc. definitions. The other dedicated modules
under `app.schemas.*` are the single source of truth for those domains
now; we re-export the symbols below for backward compatibility with the
dozens of call sites that still do `from app.schemas.skill import
UserUpdate` etc.

Anything *new* that arrives here should be a real skill-specific shape
(SkillCreate, SkillResponse, SkillSearchResult, …) and not duplicate
what already lives in the user / tag / category / analytics modules.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# Re-export the canonical User / Auth / Token / Login schemas.
# `app.schemas.skill` is the historical entry point for dozens of call
# sites, so every symbol that lived here before the refactor must
# remain importable from this module. The dedicated modules under
# `app.schemas.user` / `.tag` / `.category` are the single source of
# truth — this is just a barrel.
from app.schemas.category import (  # noqa: F401
    CategoryBase,
    CategoryCreate,
    CategoryResponse,
    CategoryTreeResponse as CategoryTreeNode,
    CategoryUpdate,
    CategoryWithSkillCount,
)
from app.schemas.tag import TagBase, TagCreate, TagResponse, TagWithSkillCount  # noqa: F401
from app.schemas.user import (  # noqa: F401
    PasswordChange as UserPasswordChange,
    PasswordReset,
    TokenResponse,
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

# ---------------------------------------------------------------------------
# Skill-specific schemas
# ---------------------------------------------------------------------------


class SkillBriefResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    version: str
    complexity: Optional[str] = None
    rating_avg: float
    rating_count: int
    download_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillVersionResponse(BaseModel):
    id: UUID
    version: str
    changelog: Optional[str] = None
    created_at: datetime
    created_by: Optional["UserBriefResponse"] = None

    model_config = {"from_attributes": True}


class SkillDependencyResponse(BaseModel):
    id: UUID
    depends_on_skill_id: UUID
    version_constraint: Optional[str] = None
    depends_on_skill: SkillBriefResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    version: str = "1.0.0"
    category_slug: Optional[str] = None
    complexity: Optional[str] = "intermediate"
    status: Optional[str] = "published"
    license: Optional[str] = None
    source_url: Optional[str] = None
    is_public: bool = True
    is_featured: bool = False
    # `content` follows the convention documented in
    # `app.core.content_i18n`. The two accepted shapes are a flat
    # dict (returned to every locale as-is) or a dict with
    # `default_locale` + `translations` (sliced per `?locale=`).
    content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = []


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[str] = None
    category_slug: Optional[str] = None
    complexity: Optional[str] = None
    status: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    content: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    tags: Optional[List[str]] = None


class SkillResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    version: str
    complexity: Optional[str] = None
    status: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None
    is_public: bool
    is_featured: bool
    download_count: int
    view_count: int
    usage_count: int
    rating_avg: float
    rating_count: int
    # `content` is sliced to the request's resolved locale by the
    # list/detail endpoints (see `app.core.content_i18n`). Pass
    # `?locale=all` to get the full translations map for editing.
    content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="extra_metadata")
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    author: Optional["UserBriefResponse"] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class SkillDetailResponse(SkillResponse):
    versions: List[SkillVersionResponse] = []
    dependencies: List[SkillDependencyResponse] = []


class SkillListResponse(BaseModel):
    items: List[SkillResponse]
    total: int
    page: int
    page_size: int


class SkillSearchResult(BaseModel):
    skill_id: str
    name: str
    description: Optional[str] = None
    score: float
    category_id: Optional[str] = None
    tags: List[str] = []
    version: str
    author: Optional[str] = None
    usage_count: int
    rating: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SkillVersionCreate(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    content: Dict[str, Any]
    changelog: Optional[str] = None


class SkillDependencyCreate(BaseModel):
    depends_on_skill_slug: str
    version_constraint: Optional[str] = None


class SkillRatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class SkillRatingResponse(BaseModel):
    id: UUID
    rating: int
    comment: Optional[str] = None
    user: "UserBriefResponse"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillUsageCreate(BaseModel):
    action: str = "download"


class SkillUsageResponse(BaseModel):
    id: UUID
    skill_id: UUID
    user_id: Optional[UUID] = None
    action: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillSimilarResponse(BaseModel):
    skill_id: str
    name: str
    description: Optional[str] = None
    score: float
    tags: List[str] = []
    version: str
    author: Optional[str] = None
    rating: float


class RecentUsageRecord(BaseModel):
    """One row of the dashboard's 'recent usage' panel. The frontend
    expects a richer shape than the raw `SkillUsageLog`, so we project
    a few related fields and stringify UUIDs (the FE side uses string ids
    uniformly)."""
    id: str
    skill_id: str
    skill_name: str
    skill_slug: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Tag / Category list + detail wrappers (kept here for back-compat)
# ---------------------------------------------------------------------------


class TagUpdate(BaseModel):
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: Optional[str] = None


class TagListResponse(BaseModel):
    items: List[TagResponse]
    total: int


class TagDetailResponse(TagResponse):
    skills: List["SkillBriefResponse"] = []

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    items: List[CategoryResponse]
    total: int


class CategoryDetailResponse(CategoryResponse):
    skills: List["SkillBriefResponse"] = []
    children: List[CategoryResponse] = []


# ---------------------------------------------------------------------------
# User wrappers (kept here for back-compat; the canonical models live in
# `app.schemas.user`).
# ---------------------------------------------------------------------------


class UserUpdateMe(BaseModel):
    """Self-service profile update. Use this for `/users/me` style
    endpoints where the current user edits their own row — never another
    user's. Lets the frontend set display name / avatar / bio without
    granting any privilege-escalation fields (no is_superuser, no
    is_active)."""
    email: Optional[EmailStr] = Field(
        None, description="新邮箱（可选，传入会触发唯一性校验）"
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="新用户名（可选，传入会触发唯一性校验）",
    )
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=2000)


class LoginRequest(BaseModel):
    """Username + password login.

    `app.schemas.user.UserLogin` is the canonical email+password model
    (used for OAuth-style flows), but the existing auth router still
    accepts `username` for backwards-compat with the v1 mobile clients.
    Keep this around until the mobile team migrates to email-based login
    (tracked in #144)."""
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh token rotation payload. `app.schemas.user.TokenRefresh`
    is the same shape — this is just an alias that keeps `from
    app.schemas.skill import RefreshRequest` working."""
    refresh_token: str = Field(..., min_length=1)


class UserBriefResponse(BaseModel):
    id: UUID
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Compositions
# ---------------------------------------------------------------------------


class CompositionItemBase(BaseModel):
    skill_slug: str
    sort_order: int = 0
    notes: Optional[str] = None


class CompositionItemCreate(CompositionItemBase):
    pass


class CompositionItemUpdate(BaseModel):
    sort_order: Optional[int] = None
    notes: Optional[str] = None


class CompositionItemResponse(BaseModel):
    id: UUID
    sort_order: int
    notes: Optional[str] = None
    skill: SkillBriefResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class CompositionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict, validation_alias="extra_metadata")


class CompositionCreate(CompositionBase):
    slug: str = Field(..., min_length=1, max_length=255)


class CompositionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class CompositionResponse(CompositionBase):
    id: UUID
    slug: str
    owner: UserBriefResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class CompositionDetailResponse(CompositionResponse):
    items: List[CompositionItemResponse] = []


class CompositionListResponse(BaseModel):
    items: List[CompositionResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Analytics / dashboard
# ---------------------------------------------------------------------------


class DashboardStats(BaseModel):
    total_skills: int
    total_users: int
    total_categories: int
    total_usage: int
    total_downloads: int
    total_ratings: int
    avg_rating: float
    # Frontend compatibility: extra counters it expects on the dashboard.
    total_compositions: int = 0
    skills_published_today: int = 0
    active_users_today: int = 0


class SkillUsageTrend(BaseModel):
    date: str
    count: int
    # Frontend compatibility: usage trend in the UI shows downloads
    # and views alongside the total. When the underlying log row
    # doesn't have a separate `action`, we mirror `count` into both.
    downloads: int = 0
    views: int = 0


class SkillUsageTrendResponse(BaseModel):
    trend: List[SkillUsageTrend]
    period: str


class CategoryDistribution(BaseModel):
    category_name: str
    category_slug: str
    count: int
    # Frontend compatibility: the UI shows `skill_count` and a relative
    # `percentage`. `skill_count` mirrors `count`; `percentage` is the
    # fraction of the total (0-100) computed at serialization time.
    skill_count: int = 0
    percentage: float = 0.0


class CategoryDistributionResponse(BaseModel):
    distribution: List[CategoryDistribution]
    total: int


class TrendingTag(BaseModel):
    name: str
    usage_count: int
    recent_usage: int


class TrendingTagResponse(BaseModel):
    tags: List[TrendingTag]


class PopularSkillResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    download_count: int
    usage_count: int
    rating_avg: float
    rating_count: int
    category_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TrendingSkillResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    usage_count: int
    recent_usage: int
    rating_avg: float
    category_name: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalyticsDashboardResponse(BaseModel):
    stats: DashboardStats
    popular_skills: List[PopularSkillResponse]
    trending_tags: List[TrendingTag]


# Resolve forward references now that every class is in scope.
SkillDetailResponse.model_rebuild()
SkillResponse.model_rebuild()
SkillVersionResponse.model_rebuild()
SkillRatingResponse.model_rebuild()
TagDetailResponse.model_rebuild()
CategoryDetailResponse.model_rebuild()
UserUpdateMe.model_rebuild()
UserUpdate.model_rebuild()  # in case anything forward-references it
