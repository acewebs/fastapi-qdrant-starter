import logging
import uuid

from qdrant_client.http.models import Condition, FieldCondition, Filter, MatchAny

from app.core.config import settings
from app.core.qdrant import get_qdrant
from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.services.embeddings import embed_text

logger = logging.getLogger(__name__)


async def search_documents(data: SearchRequest) -> SearchResponse:
    vector = await embed_text(data.query)

    conditions: list[Condition] = []
    if data.tags:
        conditions.append(FieldCondition(key="tags", match=MatchAny(any=data.tags)))
    if data.sources:
        conditions.append(FieldCondition(key="source", match=MatchAny(any=data.sources)))

    results = await get_qdrant().query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=vector,
        limit=data.limit,
        query_filter=Filter(must=conditions) if conditions else None,
        with_payload=True,
    )

    hits = []
    for point in results.points:
        payload = point.payload or {}
        document_id = payload.get("document_id")
        if not document_id:
            logger.warning("Skipping point %s with no document_id; reindex this collection", point.id)
            continue
        hits.append(
            SearchHit(
                document_id=uuid.UUID(document_id),
                chunk_index=payload.get("chunk_index", 0),
                score=point.score,
                title=payload.get("title", ""),
                content=payload.get("text", ""),
                source=payload.get("source"),
                tags=payload.get("tags", []),
            )
        )
    return SearchResponse(query=data.query, hits=hits)
