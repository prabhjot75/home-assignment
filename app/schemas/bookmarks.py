from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class TagResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class BookmarkBase(BaseModel):
    url: str = Field(..., description="Valid bookmark destination URL")
    title: str = Field(..., min_length=1, max_length=200, description="Title is required and must be under 200 characters.")
    description: Optional[str] = Field(None, max_length=500, description="Description must be under 500 characters.")

    @field_validator('url')
    @classmethod
    def check_valid_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must use an HTTP or HTTPS scheme')
        return v

class BookmarkCreate(BookmarkBase):
    tags: List[str] = Field(default=[], description="List of unique tag names")

class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

class PaginatedBookmarks(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[BookmarkResponse]

class TopTagStats(BaseModel):
    name: str
    count: int

class MonthStats(BaseModel):
    month: str
    count: int

class StatisticsResponse(BaseModel):
    total_bookmarks: int
    total_tags: int
    top_tags: List[TopTagStats]
    bookmarks_per_month: List[MonthStats]