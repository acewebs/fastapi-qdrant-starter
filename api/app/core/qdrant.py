import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncQdrantClient | None = None


async def init_qdrant() -> None:
    global _client
    _client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    await _ensure_collection()


async def close_qdrant() -> None:
    global _client
    if _client:
        await _client.close()
        _client = None


def get_qdrant() -> AsyncQdrantClient:
    if _client is None:
        raise RuntimeError("Qdrant client not initialized")
    return _client


async def _ensure_collection() -> None:
    client = get_qdrant()
    exists = await client.collection_exists(settings.QDRANT_COLLECTION)
    if exists:
        logger.info("Qdrant collection %s already exists", settings.QDRANT_COLLECTION)
        return
    await client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=settings.EMBEDDING_DIM, distance=Distance.COSINE),
    )
    logger.info("Created Qdrant collection %s (dim=%d)", settings.QDRANT_COLLECTION, settings.EMBEDDING_DIM)
