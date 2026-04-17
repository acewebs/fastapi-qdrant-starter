import logging

from qdrant_client.http.models import FieldCondition, Filter, MatchAny

from app.core.config import settings
from app.core.qdrant import get_qdrant
from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.services.embeddings import embed_text

logger = logging.getLogger(__name__)


async def search_documents(data: SearchRequest) -> SearchResponse:
    vector = await embed_text(data.query)
    client = get_qdrant()

    query_filter = None
    if data.tags:
        query_filter = Filter(
            must=[FieldCondition(key="tags", match=MatchAny(any=data.tags))],
        )

    results = await client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=vector,
        limit=data.limit,
        query_filter=query_filter,
        with_payload=True,
    )

    hits = [
        SearchHit(
            id=point.id,
            score=point.score,
            title=(point.payload or {}).get("title", ""),
            content=(point.payload or {}).get("content", ""),
            source=(point.payload or {}).get("source"),
            tags=(point.payload or {}).get("tags", []),
        )
        for point in results.points
    ]
    return SearchResponse(query=data.query, hits=hits)
