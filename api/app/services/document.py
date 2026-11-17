import logging
import uuid

from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.qdrant import get_qdrant
from app.models import Document
from app.schemas.document import DocumentCreate
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

logger = logging.getLogger(__name__)

CHUNK_ID_NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00c04fc964ff")


async def create_document(db: AsyncSession, data: DocumentCreate) -> Document:
    documents = await create_documents(db, [data])
    return documents[0]


async def create_documents(db: AsyncSession, items: list[DocumentCreate]) -> list[Document]:
    documents = [Document(**item.model_dump()) for item in items]
    db.add_all(documents)
    await db.commit()
    for document in documents:
        await db.refresh(document)

    chunked = [(document, chunk_text(document.content)) for document in documents]
    texts = [f"{document.title}\n\n{chunk}" for document, chunks in chunked for chunk in chunks]
    if not texts:
        return documents

    vectors = await embed_texts(texts)
    points = []
    cursor = 0
    for document, chunks in chunked:
        for index, chunk in enumerate(chunks):
            points.append(
                PointStruct(
                    id=_chunk_id(document.id, index),
                    vector=vectors[cursor],
                    payload={
                        "document_id": str(document.id),
                        "chunk_index": index,
                        "text": chunk,
                        "title": document.title,
                        "source": document.source,
                        "tags": document.tags,
                    },
                )
            )
            cursor += 1

    await get_qdrant().upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    logger.info("Indexed %d document(s) as %d chunk(s) into Qdrant", len(documents), len(points))
    return documents


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    return await db.get(Document, document_id)


async def list_documents(db: AsyncSession, skip: int = 0, limit: int = 50) -> tuple[list[Document], int]:
    total_result = await db.execute(select(func.count(Document.id)))
    total = total_result.scalar_one()

    result = await db.execute(select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit))
    items = list(result.scalars().all())
    return items, total


async def delete_document(db: AsyncSession, document: Document) -> None:
    await get_qdrant().delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=str(document.id)))],
        ),
    )
    await db.delete(document)
    await db.commit()


def _chunk_id(document_id: uuid.UUID, index: int) -> str:
    return str(uuid.uuid5(CHUNK_ID_NAMESPACE, f"{document_id}:{index}"))
