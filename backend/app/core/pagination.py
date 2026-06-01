from __future__ import annotations

from math import ceil
from typing import ClassVar, Generic, List, Literal, Optional, TypeVar

from fastapi import Depends
from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量，1-100")
    sort: Optional[str] = Field(default=None, description="排序字段")
    order: Literal["asc", "desc"] = Field(default="desc", description="排序方向")

    Depends: ClassVar = Depends()


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return ceil(self.total / self.page_size)
