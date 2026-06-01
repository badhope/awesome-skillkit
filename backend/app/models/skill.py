import enum
import uuid as uuid_lib
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Index,
    Uuid,
    func,
    JSON,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ComplexityEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class StatusEnum(str, enum.Enum):
    draft = "draft"
    published = "published"
    deprecated = "deprecated"
    archived = "archived"


skill_tag_association = Table(
    "skill_tag_association",
    Base.metadata,
    Column("skill_id", Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_skill_tag_skill_id", "skill_id"),
    Index("ix_skill_tag_tag_id", "tag_id"),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    skills: Mapped[List["Skill"]] = relationship("Skill", lazy="selectin", back_populates="author")
    skill_versions: Mapped[List["SkillVersion"]] = relationship("SkillVersion", lazy="selectin", back_populates="created_by")
    ratings: Mapped[List["SkillRating"]] = relationship("SkillRating", lazy="selectin", back_populates="user")
    compositions: Mapped[List["SkillComposition"]] = relationship("SkillComposition", lazy="selectin", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[uuid_lib.UUID]] = mapped_column(Uuid, ForeignKey("categories.id", ondelete="SET NULL"))
    icon: Mapped[Optional[str]] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], lazy="selectin", back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", lazy="selectin", back_populates="parent")
    skills: Mapped[List["Skill"]] = relationship("Skill", lazy="selectin", back_populates="category")

    __table_args__ = (
        Index("idx_category_slug", "slug"),
        Index("idx_category_parent", "parent_id"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(7))
    description: Mapped[Optional[str]] = mapped_column(Text)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skills: Mapped[List["Skill"]] = relationship("Skill", secondary=skill_tag_association, lazy="selectin", back_populates="tags")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    category_id: Mapped[Optional[uuid_lib.UUID]] = mapped_column(Uuid, ForeignKey("categories.id", ondelete="SET NULL"))
    author_id: Mapped[Optional[uuid_lib.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    complexity: Mapped[ComplexityEnum] = mapped_column(Enum(ComplexityEnum, name="complexity_enum"), default=ComplexityEnum.intermediate)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum, name="status_enum"), default=StatusEnum.published)
    license: Mapped[Optional[str]] = mapped_column(String(100))
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    category: Mapped[Optional["Category"]] = relationship("Category", lazy="selectin", back_populates="skills")
    author: Mapped[Optional["User"]] = relationship("User", lazy="selectin", back_populates="skills")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=skill_tag_association, lazy="selectin", back_populates="skills")
    versions: Mapped[List["SkillVersion"]] = relationship("SkillVersion", lazy="selectin", back_populates="skill", order_by="SkillVersion.created_at.desc()", passive_deletes=True)
    dependencies: Mapped[List["SkillDependency"]] = relationship(
        "SkillDependency", foreign_keys="SkillDependency.skill_id", lazy="selectin", back_populates="skill"
    )
    dependents: Mapped[List["SkillDependency"]] = relationship(
        "SkillDependency", foreign_keys="SkillDependency.depends_on_skill_id", lazy="selectin", back_populates="depends_on_skill"
    )
    ratings: Mapped[List["SkillRating"]] = relationship("SkillRating", lazy="selectin", back_populates="skill")
    usage_logs: Mapped[List["SkillUsageLog"]] = relationship("SkillUsageLog", lazy="selectin", back_populates="skill")

    __table_args__ = (
        Index("idx_skill_slug", "slug"),
        Index("idx_skill_category", "category_id"),
        Index("idx_skill_author", "author_id"),
        Index("idx_skill_featured", "is_featured"),
        Index("idx_skill_status", "status"),
        Index("idx_skill_complexity", "complexity"),
    )


class SkillVersion(Base):
    __tablename__ = "skill_versions"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    changelog: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_id: Mapped[Optional[uuid_lib.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))

    skill: Mapped["Skill"] = relationship("Skill", lazy="selectin", back_populates="versions")
    created_by: Mapped[Optional["User"]] = relationship("User", lazy="selectin", back_populates="skill_versions")

    __table_args__ = (
        UniqueConstraint("skill_id", "version", name="uq_skill_version"),
        Index("idx_skill_version_skill", "skill_id"),
    )


class SkillDependency(Base):
    __tablename__ = "skill_dependencies"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    depends_on_skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    version_constraint: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skill: Mapped["Skill"] = relationship("Skill", foreign_keys=[skill_id], lazy="selectin", back_populates="dependencies")
    depends_on_skill: Mapped["Skill"] = relationship("Skill", foreign_keys=[depends_on_skill_id], lazy="selectin", back_populates="dependents")

    __table_args__ = (
        UniqueConstraint("skill_id", "depends_on_skill_id", name="uq_skill_dependency"),
        Index("idx_skill_dependency_skill", "skill_id"),
        Index("idx_skill_dependency_depends_on", "depends_on_skill_id"),
    )


class SkillRating(Base):
    __tablename__ = "skill_ratings"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    user_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    skill: Mapped["Skill"] = relationship("Skill", lazy="selectin", back_populates="ratings")
    user: Mapped["User"] = relationship("User", lazy="selectin", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("skill_id", "user_id", name="uq_skill_user_rating"),
        Index("idx_skill_rating_skill", "skill_id"),
        Index("idx_skill_rating_user", "user_id"),
    )


class SkillUsageLog(Base):
    __tablename__ = "skill_usage_logs"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    user_id: Mapped[Optional[uuid_lib.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(50), nullable=False, default="download")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skill: Mapped["Skill"] = relationship("Skill", lazy="selectin", back_populates="usage_logs")

    __table_args__ = (
        Index("idx_skill_usage_log_skill", "skill_id"),
        Index("idx_skill_usage_log_user", "user_id"),
        Index("idx_skill_usage_log_created", "created_at"),
    )


class SkillComposition(Base):
    __tablename__ = "skill_compositions"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship("User", lazy="selectin", back_populates="compositions")
    items: Mapped[List["SkillCompositionItem"]] = relationship(
        "SkillCompositionItem", lazy="selectin", back_populates="composition", order_by="SkillCompositionItem.sort_order"
    )

    __table_args__ = (
        Index("idx_skill_composition_owner", "owner_id"),
        Index("idx_skill_composition_slug", "slug"),
    )


class SkillCompositionItem(Base):
    __tablename__ = "skill_composition_items"

    id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_lib.uuid4)
    composition_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skill_compositions.id", ondelete="CASCADE"))
    skill_id: Mapped[uuid_lib.UUID] = mapped_column(Uuid, ForeignKey("skills.id", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    composition: Mapped["SkillComposition"] = relationship("SkillComposition", lazy="selectin", back_populates="items")
    skill: Mapped["Skill"] = relationship("Skill")

    __table_args__ = (
        UniqueConstraint("composition_id", "skill_id", name="uq_composition_skill"),
        Index("idx_comp_item_composition", "composition_id"),
        Index("idx_comp_item_skill", "skill_id"),
    )