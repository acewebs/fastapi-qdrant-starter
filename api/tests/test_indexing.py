import pytest

from app.core.config import settings


@pytest.fixture
def small_chunks(monkeypatch):
    monkeypatch.setattr(settings, "CHUNK_MAX_LENGTH", 120)
    monkeypatch.setattr(settings, "CHUNK_OVERLAP", 20)


@pytest.mark.asyncio
async def test_long_document_is_indexed_as_several_points(client, fake_qdrant, small_chunks):
    body = {"title": "Long", "content": "\n\n".join("paragraph " + str(i) + " " + "w" * 90 for i in range(5))}
    response = await client.post("/api/v1/documents", json=body)
    assert response.status_code == 201

    points = fake_qdrant.upsert.await_args.kwargs["points"]
    assert len(points) > 1
    assert {p.payload["document_id"] for p in points} == {response.json()["item"]["id"]}
    assert [p.payload["chunk_index"] for p in points] == list(range(len(points)))
    assert all(p.payload["title"] == "Long" for p in points)
    assert all(len(p.payload["text"]) <= 120 for p in points)


@pytest.mark.asyncio
async def test_reindexing_the_same_document_reuses_point_ids(client, fake_qdrant, small_chunks):
    from app.services.document import _chunk_id

    body = {"title": "Stable", "content": "x" * 400}
    response = await client.post("/api/v1/documents", json=body)
    document_id = response.json()["item"]["id"]

    points = fake_qdrant.upsert.await_args.kwargs["points"]
    assert [p.id for p in points] == [_chunk_id(document_id, i) for i in range(len(points))]


@pytest.mark.asyncio
async def test_batch_embeds_every_chunk_in_one_call(client, fake_qdrant, monkeypatch):
    calls = []

    async def counting_embed_texts(texts):
        calls.append(len(texts))
        return [[0.0] * 384 for _ in texts]

    monkeypatch.setattr("app.services.document.embed_texts", counting_embed_texts)

    items = [{"title": "Doc " + str(i), "content": "short body " + str(i)} for i in range(5)]
    response = await client.post("/api/v1/documents/batch", json={"items": items})
    assert response.status_code == 201
    assert response.json()["count"] == 5
    assert calls == [5]
    assert len(fake_qdrant.upsert.await_args.kwargs["points"]) == 5


@pytest.mark.asyncio
async def test_batch_rejects_an_empty_list(client):
    assert (await client.post("/api/v1/documents/batch", json={"items": []})).status_code == 422


@pytest.mark.asyncio
async def test_delete_removes_every_chunk_by_filter(client, fake_qdrant):
    created = await client.post("/api/v1/documents", json={"title": "Gone", "content": "body"})
    document_id = created.json()["item"]["id"]

    response = await client.delete("/api/v1/documents/" + document_id)
    assert response.status_code == 204

    selector = fake_qdrant.delete.await_args.kwargs["points_selector"]
    condition = selector.must[0]
    assert condition.key == "document_id"
    assert condition.match.value == document_id
