import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/health", "/api/health"])
async def test_health(client, path):
    response = await client.get(path)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "qdrant": "ok"}


@pytest.mark.asyncio
async def test_health_reports_unreachable_qdrant(client, fake_qdrant):
    fake_qdrant.get_collections.side_effect = RuntimeError("connection refused")
    response = await client.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"]["qdrant"] == "unreachable"


@pytest.mark.asyncio
async def test_app_info_requires_key(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "API_KEY", "secret-test-key")
    assert (await client.get("/api/v1/app")).status_code == 401

    response = await client.get("/api/v1/app", headers={"X-API-Key": "secret-test-key"})
    assert response.status_code == 200
    data = response.json()
    assert data["embed_engine"] == "fastembed"
    assert data["embedding_dim"] == 384
