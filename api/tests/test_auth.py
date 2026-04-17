import pytest

from app.core.config import settings


@pytest.fixture
def with_api_key(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-test-key")


@pytest.mark.asyncio
async def test_documents_open_when_no_api_key_set(client):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_documents_rejected_without_header(client, with_api_key):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_documents_rejected_with_wrong_key(client, with_api_key):
    response = await client.get("/api/v1/documents", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_documents_accepted_with_correct_key(client, with_api_key):
    response = await client.get(
        "/api/v1/documents", headers={"X-API-Key": "secret-test-key"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_requires_key(client, with_api_key):
    response = await client.post("/api/v1/search", json={"query": "x"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_always_open(client, with_api_key):
    response = await client.get("/health")
    assert response.status_code == 200
