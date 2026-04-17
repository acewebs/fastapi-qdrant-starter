import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source: str | None = Field(None, max_length=255)
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    source: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentItemResponse(BaseModel):
    item: DocumentResponse


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
