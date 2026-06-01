import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="标签名称",
        examples=["python", "代码审查", "安全"],
    )
    color: Optional[str] = Field(
        None,
        min_length=7,
        max_length=7,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="标签颜色（十六进制颜色码）",
        examples=["#FF5733", "#3498DB"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="标签描述",
        examples=["与 Python 编程语言相关的所有技能标签"],
    )


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: uuid.UUID = Field(
        ...,
        description="标签 UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    usage_count: int = Field(
        default=0,
        description="标签被使用的次数",
    )
    created_at: datetime = Field(
        ...,
        description="创建时间",
    )

    model_config = {"from_attributes": True}


class TagWithSkillCount(TagResponse):
    skill_count: int = Field(
        default=0,
        description="关联的技能数量",
    )