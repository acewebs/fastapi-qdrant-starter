import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_api_key
from app.db.session import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentItemResponse,
    DocumentListResponse,
    DocumentResponse,
)
from app.services.document import (
    create_document,
    delete_document,
    get_document,
    list_documents,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=DocumentListResponse)
async def list_documents_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_documents(db, skip=skip, limit=limit)
    return DocumentListResponse(items=[DocumentResponse.model_validate(i) for i in items], total=total)


@router.post("", response_model=DocumentItemResponse, status_code=201)
async def create_document_route(data: DocumentCreate, db: AsyncSession = Depends(get_db)):
    document = await create_document(db, data)
    return DocumentItemResponse(item=DocumentResponse.model_validate(document))


@router.get("/{document_id}", response_model=DocumentItemResponse)
async def get_document_route(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentItemResponse(item=DocumentResponse.model_validate(document))


@router.delete("/{document_id}", status_code=204)
async def delete_document_route(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await delete_document(db, document)
