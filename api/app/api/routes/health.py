import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.qdrant import get_qdrant
from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


async def _health(db: AsyncSession) -> dict[str, str]:
    checks = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.warning("Health check: database unreachable: %s", exc)
        checks["database"] = "unreachable"
    try:
        await get_qdrant().get_collections()
        checks["qdrant"] = "ok"
    except Exception as exc:
        logger.warning("Health check: qdrant unreachable: %s", exc)
        checks["qdrant"] = "unreachable"

    if any(value != "ok" for value in checks.values()):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"status": "degraded", **checks})
    return {"status": "ok", **checks}


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await _health(db)


@router.get("/api/health")
async def health_check_api(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await _health(db)
