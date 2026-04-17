import logging
import uuid

from qdrant_client.http.models import PointStruct
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.qdrant import get_qdrant
from app.models import Document
from app.schemas.document import DocumentCreate
from app.services.embeddings import embed_text

logger = logging.getLogger(__name__)


async def create_document(db: AsyncSession, data: DocumentCreate) -> Document:
    document = Document(**data.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document)

    vector = await embed_text(_vector_text(document))
    client = get_qdrant()
    await client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=str(document.id),
                vector=vector,
                payload={
                    "title": document.title,
                    "content": document.content,
                    "source": document.source,
                    "tags": document.tags,
                },
            )
        ],
    )
    logger.info("Indexed document %s into Qdrant", document.id)
    return document


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    return await db.get(Document, document_id)


async def list_documents(db: AsyncSession, skip: int = 0, limit: int = 50) -> tuple[list[Document], int]:
    total_result = await db.execute(select(func.count(Document.id)))
    total = total_result.scalar_one()

    result = await db.execute(select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit))
    items = list(result.scalars().all())
    return items, total


async def delete_document(db: AsyncSession, document: Document) -> None:
    client = get_qdrant()
    await client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=[str(document.id)],
    )
    await db.delete(document)
    await db.commit()


def _vector_text(document: Document) -> str:
    return f"{document.title}\n\n{document.content}"
