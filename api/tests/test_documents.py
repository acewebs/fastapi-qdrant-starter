import pytest


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_document(client, fake_qdrant):
    response = await client.post(
        "/api/v1/documents",
        json={
            "title": "Hello",
            "content": "Some content to index",
            "tags": ["greeting"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["item"]["title"] == "Hello"
    assert data["item"]["tags"] == ["greeting"]
    assert "id" in data["item"]
    fake_qdrant.upsert.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_document_validation(client):
    response = await client.post("/api/v1/documents", json={"title": "", "content": "x"})
    assert response.status_code == 422

    response = await client.post("/api/v1/documents", json={"title": "x"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_document(client):
    create = await client.post(
        "/api/v1/documents", json={"title": "Find Me", "content": "body"}
    )
    document_id = create.json()["item"]["id"]

    response = await client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["item"]["title"] == "Find Me"


@pytest.mark.asyncio
async def test_get_document_not_found(client):
    response = await client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client, fake_qdrant):
    create = await client.post(
        "/api/v1/documents", json={"title": "Delete Me", "content": "body"}
    )
    document_id = create.json()["item"]["id"]

    response = await client.delete(f"/api/v1/documents/{document_id}")
    assert response.status_code == 204
    fake_qdrant.delete.assert_awaited_once()

    response = await client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search(client, fake_qdrant):
    class FakePoint:
        def __init__(self):
            self.id = "00000000-0000-0000-0000-000000000001"
            self.score = 0.91
            self.payload = {
                "title": "Matched",
                "content": "body",
                "source": None,
                "tags": ["x"],
            }

    fake_qdrant.query_points.return_value = type("R", (), {"points": [FakePoint()]})()

    response = await client.post(
        "/api/v1/search",
        json={"query": "hello", "limit": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "hello"
    assert len(data["hits"]) == 1
    assert data["hits"][0]["title"] == "Matched"
    assert data["hits"][0]["score"] == 0.91
