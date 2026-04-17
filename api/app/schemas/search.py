import uuid

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=50)
    tags: list[str] | None = None


class SearchHit(BaseModel):
    id: uuid.UUID
    score: float
    title: str
    content: str
    source: str | None
    tags: list[str]


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]
