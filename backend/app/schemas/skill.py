from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    color: Optional[str] = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: Optional[str] = None


class TagResponse(TagBase):
    id: UUID
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    items: List[TagResponse]
    total: int


class TagDetailResponse(TagResponse):
    skills: List["SkillBriefResponse"] = []

    model_config = {"from_attributes": True}


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    slug: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[UUID] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    slug: str
    parent_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryTreeNode(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int
    is_active: bool
    parent_id: Optional[UUID] = None
    skill_count: int = 0
    children: List["CategoryTreeNode"] = []

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    items: List[CategoryResponse]
    total: int


class CategoryDetailResponse(CategoryResponse):
    skills: List["SkillBriefResponse"] = []
    children: List[CategoryResponse] = []


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
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: str = "1.0.0"
    category_slug: Optional[str] = None
    complexity: Optional[str] = "intermediate"
    status: Optional[str] = "published"
    license: Optional[str] = None
    source_url: Optional[str] = None
    is_public: bool = True
    is_featured: bool = False
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
    total_pages: int = 0

    def model_post_init(self, __context) -> None:
        if self.total_pages == 0 and self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size


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


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=150)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=150)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserUpdateMe(UserUpdate):
    pass


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserBriefResponse(BaseModel):
    id: UUID
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    id: UUID
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


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
    total_pages: int = 0

    def model_post_init(self, __context) -> None:
        if self.total_pages == 0 and self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size


class DashboardStats(BaseModel):
    total_skills: int
    total_users: int
    total_categories: int
    total_usage: int
    total_downloads: int
    total_ratings: int
    avg_rating: float


class SkillUsageTrend(BaseModel):
    date: str
    count: int


class SkillUsageTrendResponse(BaseModel):
    trend: List[SkillUsageTrend]
    period: str


class CategoryDistribution(BaseModel):
    category_name: str
    category_slug: str
    count: int


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