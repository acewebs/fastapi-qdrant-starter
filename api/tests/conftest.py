from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import qdrant as qdrant_module
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services import embeddings as embeddings_module

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def fake_qdrant(monkeypatch):
    client = AsyncMock()
    client.upsert = AsyncMock()
    client.delete = AsyncMock()
    client.query_points = AsyncMock(return_value=AsyncMock(points=[]))
    client.collection_exists = AsyncMock(return_value=True)
    client.create_collection = AsyncMock()
    client.close = AsyncMock()
    monkeypatch.setattr(qdrant_module, "_client", client)
    monkeypatch.setattr(qdrant_module, "init_qdrant", AsyncMock())
    monkeypatch.setattr(qdrant_module, "close_qdrant", AsyncMock())
    return client


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    async def embed_text(_text: str) -> list[float]:
        return [0.0] * 384

    async def embed_texts(texts: list[str]) -> list[list[float]]:
        return [[0.0] * 384 for _ in texts]

    monkeypatch.setattr(embeddings_module, "embed_text", embed_text)
    monkeypatch.setattr(embeddings_module, "embed_texts", embed_texts)
    monkeypatch.setattr("app.services.document.embed_text", embed_text)
    monkeypatch.setattr("app.services.search.embed_text", embed_text)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
