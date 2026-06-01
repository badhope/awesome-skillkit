import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="分类名称",
        examples=["代码审查", "测试", "文档生成"],
    )
    slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="分类唯一标识符",
        examples=["code-review", "testing", "documentation"],
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="分类描述",
        examples=["用于代码审查和静态分析相关的技能"],
    )
    parent_id: Optional[uuid.UUID] = Field(
        None,
        description="父分类的 UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    icon: Optional[str] = Field(
        None,
        max_length=100,
        description="分类图标（图标名称或 SVG 内容）",
        examples=["code-review", "mdi:shield-check"],
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="排序序号",
    )


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="分类名称",
    )
    slug: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="分类唯一标识符",
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="分类描述",
    )
    parent_id: Optional[uuid.UUID] = Field(
        None,
        description="父分类的 UUID",
    )
    icon: Optional[str] = Field(
        None,
        max_length=100,
        description="分类图标",
    )
    sort_order: Optional[int] = Field(
        None,
        ge=0,
        description="排序序号",
    )


class CategoryResponse(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="分类 UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(
        ...,
        description="分类名称",
    )
    slug: str = Field(
        ...,
        description="分类唯一标识符",
    )
    description: Optional[str] = Field(
        None,
        description="分类描述",
    )
    parent_id: Optional[uuid.UUID] = Field(
        None,
        description="父分类的 UUID",
    )
    icon: Optional[str] = Field(
        None,
        description="分类图标",
    )
    sort_order: int = Field(
        ...,
        description="排序序号",
    )
    created_at: datetime = Field(
        ...,
        description="创建时间",
    )
    updated_at: datetime = Field(
        ...,
        description="最后更新时间",
    )

    model_config = {"from_attributes": True}


class CategoryTreeResponse(CategoryResponse):
    children: List["CategoryTreeResponse"] = Field(
        default_factory=list,
        description="子分类列表（递归结构）",
    )


class CategoryWithSkillCount(CategoryResponse):
    skill_count: int = Field(
        default=0,
        description="分类下的技能数量",
    )
    children: List["CategoryWithSkillCount"] = Field(
        default_factory=list,
        description="子分类列表（含技能数量）",
    )