import asyncio
import logging
from functools import lru_cache

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _fastembed_model():
    from fastembed import TextEmbedding

    logger.info("Loading fastembed model %s", settings.EMBEDDING_MODEL)
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def _fastembed_sync(texts: list[str]) -> list[list[float]]:
    model = _fastembed_model()
    return [vec.tolist() for vec in model.embed(texts)]


async def _embed_fastembed(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(_fastembed_sync, texts)


async def _embed_openai(texts: list[str]) -> list[list[float]]:
    if not settings.EMBED_ENGINE_KEY:
        raise RuntimeError("EMBED_ENGINE=openai requires EMBED_ENGINE_KEY")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.EMBED_ENGINE_KEY}"},
            json={"model": settings.EMBEDDING_MODEL, "input": texts},
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    engine = settings.EMBED_ENGINE.lower()
    if engine == "openai":
        return await _embed_openai(texts)
    if engine == "fastembed":
        return await _embed_fastembed(texts)
    raise RuntimeError(f"Unknown EMBED_ENGINE: {settings.EMBED_ENGINE!r} (expected 'fastembed' or 'openai')")


async def embed_text(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
