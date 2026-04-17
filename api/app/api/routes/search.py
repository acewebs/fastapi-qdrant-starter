from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search import search_documents

router = APIRouter(prefix="/api/v1/search", tags=["search"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=SearchResponse)
async def search_route(data: SearchRequest) -> SearchResponse:
    return await search_documents(data)
