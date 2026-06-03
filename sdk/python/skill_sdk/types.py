from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class SkillDict:
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    version: str
    complexity: Optional[str]
    status: Optional[str]
    license: Optional[str]
    source_url: Optional[str]
    is_public: bool
    is_featured: bool
    download_count: int
    view_count: int
    usage_count: int
    rating_avg: float
    rating_count: int
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: Optional[CategoryDict] = None
    tags: List[TagDict] = field(default_factory=list)
    author: Optional[UserBriefDict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    versions: List[SkillVersionDict] = field(default_factory=list)
    dependencies: List[SkillDependencyDict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            complexity=data.get("complexity"),
            status=data.get("status"),
            license=data.get("license"),
            source_url=data.get("source_url"),
            is_public=data.get("is_public", True),
            is_featured=data.get("is_featured", False),
            download_count=data.get("download_count", 0),
            view_count=data.get("view_count", 0),
            usage_count=data.get("usage_count", 0),
            rating_avg=data.get("rating_avg", 0.0),
            rating_count=data.get("rating_count", 0),
            content=data.get("content", {}),
            metadata=data.get("metadata", {}),
            category=CategoryDict.from_dict(data["category"]) if data.get("category") else None,
            tags=[TagDict.from_dict(t) for t in data.get("tags", [])],
            author=UserBriefDict.from_dict(data["author"]) if data.get("author") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            versions=[SkillVersionDict.from_dict(v) for v in data.get("versions", [])],
            dependencies=[SkillDependencyDict.from_dict(d) for d in data.get("dependencies", [])],
        )


@dataclass
class SkillBriefDict:
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    version: str
    complexity: Optional[str]
    rating_avg: float
    rating_count: int
    download_count: int
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillBriefDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            complexity=data.get("complexity"),
            rating_avg=data.get("rating_avg", 0.0),
            rating_count=data.get("rating_count", 0),
            download_count=data.get("download_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )


@dataclass
class CategoryDict:
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    sort_order: int
    parent_id: Optional[UUID] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skill_count: int = 0
    children: List[CategoryDict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CategoryDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            icon=data.get("icon"),
            sort_order=data.get("sort_order", 0),
            parent_id=UUID(data["parent_id"]) if data.get("parent_id") else None,
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            skill_count=data.get("skill_count", 0),
            children=[cls.from_dict(c) for c in data.get("children", [])],
        )


@dataclass
class TagDict:
    id: UUID
    name: str
    color: Optional[str]
    description: Optional[str]
    usage_count: int
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TagDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            color=data.get("color"),
            description=data.get("description"),
            usage_count=data.get("usage_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )


@dataclass
class SkillVersionDict:
    id: UUID
    version: str
    changelog: Optional[str]
    created_at: Optional[datetime] = None
    created_by: Optional[UserBriefDict] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillVersionDict:
        return cls(
            id=UUID(data["id"]),
            version=data["version"],
            changelog=data.get("changelog"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            created_by=UserBriefDict.from_dict(data["created_by"]) if data.get("created_by") else None,
        )


@dataclass
class SkillDependencyDict:
    id: UUID
    depends_on_skill_id: UUID
    version_constraint: Optional[str]
    depends_on_skill: Optional[SkillBriefDict] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillDependencyDict:
        return cls(
            id=UUID(data["id"]),
            depends_on_skill_id=UUID(data["depends_on_skill_id"]),
            version_constraint=data.get("version_constraint"),
            depends_on_skill=SkillBriefDict.from_dict(data["depends_on_skill"]) if data.get("depends_on_skill") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )


@dataclass
class UserBriefDict:
    id: UUID
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserBriefDict:
        return cls(
            id=UUID(data["id"]),
            username=data["username"],
            full_name=data.get("full_name"),
            avatar_url=data.get("avatar_url"),
        )


@dataclass
class UserDict:
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserDict:
        return cls(
            id=UUID(data["id"]),
            email=data["email"],
            username=data["username"],
            full_name=data.get("full_name"),
            avatar_url=data.get("avatar_url"),
            bio=data.get("bio"),
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class TokenDict:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TokenDict:
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
        )


@dataclass
class SkillSearchResultDict:
    skill_id: str
    name: str
    description: Optional[str]
    score: float
    category_id: Optional[str]
    tags: List[str]
    version: str
    author: Optional[str]
    usage_count: int
    rating: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillSearchResultDict:
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            description=data.get("description"),
            score=data["score"],
            category_id=data.get("category_id"),
            tags=data.get("tags", []),
            version=data.get("version", ""),
            author=data.get("author"),
            usage_count=data.get("usage_count", 0),
            rating=data.get("rating", 0.0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class PaginatedResult:
    items: List[Any]
    total: int
    page: int
    page_size: int


@dataclass
class AnalyticsDashboardDict:
    stats: DashboardStatsDict
    popular_skills: List[PopularSkillDict] = field(default_factory=list)
    trending_tags: List[TrendingTagDict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AnalyticsDashboardDict:
        return cls(
            stats=DashboardStatsDict.from_dict(data["stats"]),
            popular_skills=[PopularSkillDict.from_dict(s) for s in data.get("popular_skills", [])],
            trending_tags=[TrendingTagDict.from_dict(t) for t in data.get("trending_tags", [])],
        )


@dataclass
class DashboardStatsDict:
    total_skills: int
    total_users: int
    total_categories: int
    total_usage: int
    total_downloads: int
    total_ratings: int
    avg_rating: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DashboardStatsDict:
        return cls(
            total_skills=data["total_skills"],
            total_users=data["total_users"],
            total_categories=data["total_categories"],
            total_usage=data["total_usage"],
            total_downloads=data["total_downloads"],
            total_ratings=data["total_ratings"],
            avg_rating=data["avg_rating"],
        )


@dataclass
class PopularSkillDict:
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    download_count: int
    usage_count: int
    rating_avg: float
    rating_count: int
    category_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PopularSkillDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            download_count=data.get("download_count", 0),
            usage_count=data.get("usage_count", 0),
            rating_avg=data.get("rating_avg", 0.0),
            rating_count=data.get("rating_count", 0),
            category_name=data.get("category_name"),
        )


@dataclass
class TrendingTagDict:
    name: str
    usage_count: int
    recent_usage: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TrendingTagDict:
        return cls(
            name=data["name"],
            usage_count=data.get("usage_count", 0),
            recent_usage=data.get("recent_usage", 0),
        )


@dataclass
class SkillUsageTrendDict:
    date: str
    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillUsageTrendDict:
        return cls(date=data["date"], count=data["count"])


@dataclass
class CompositionDict:
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    is_public: bool
    metadata: Dict[str, Any]
    owner: Optional[UserBriefDict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[CompositionItemDict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompositionDict:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            is_public=data.get("is_public", False),
            metadata=data.get("metadata", {}),
            owner=UserBriefDict.from_dict(data["owner"]) if data.get("owner") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            items=[CompositionItemDict.from_dict(i) for i in data.get("items", [])],
        )


@dataclass
class CompositionItemDict:
    id: UUID
    sort_order: int
    notes: Optional[str]
    skill: Optional[SkillBriefDict] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompositionItemDict:
        return cls(
            id=UUID(data["id"]),
            sort_order=data.get("sort_order", 0),
            notes=data.get("notes"),
            skill=SkillBriefDict.from_dict(data["skill"]) if data.get("skill") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )
