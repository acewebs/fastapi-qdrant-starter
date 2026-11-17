from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.core.config import settings

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


@router.get("/app")
async def app_info():
    return {
        "name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "version": "1.0.0",
        "embed_engine": settings.embed_engine,
        "embedding_model": settings.embedding_model,
        "embedding_dim": settings.embedding_dimensions,
        "qdrant_collection": settings.QDRANT_COLLECTION,
    }
