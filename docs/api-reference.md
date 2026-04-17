# API Reference

Base URL: `http://localhost:8000` (local) or your Railway-generated domain.

Interactive docs: `GET /docs` (Swagger UI).

## Authentication

If the `API_KEY` env var is set on the server, all `/api/v1/documents` and `/api/v1/search` endpoints require an `X-API-Key` header:

```bash
curl -H "X-API-Key: <your-key>" http://localhost:8000/api/v1/documents
```

When `API_KEY` is unset (the local dev default), the API is open — no header needed. `/health` and `/api/v1/app` are always open so platform healthchecks work.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/app` | App info (name, env, engine, collection) |
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/documents` | Index a new document |
| GET | `/api/v1/documents/{id}` | Get document by id |
| DELETE | `/api/v1/documents/{id}` | Delete document (from DB + Qdrant) |
| POST | `/api/v1/search` | Semantic search |

## Index a document

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Intro to Qdrant",
    "content": "Qdrant is a vector database optimized for similarity search.",
    "source": "docs",
    "tags": ["qdrant", "vector"]
  }'
```

Response (`201`):

```json
{
  "item": {
    "id": "0193f8e2-...",
    "title": "Intro to Qdrant",
    "content": "Qdrant is a vector database optimized for similarity search.",
    "source": "docs",
    "tags": ["qdrant", "vector"],
    "created_at": "2026-04-17T12:00:00Z",
    "updated_at": "2026-04-17T12:00:00Z"
  }
}
```

The API persists the document to Postgres, embeds `title + content`, and upserts the vector into Qdrant under the document's UUID.

## Search

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is a vector database", "limit": 5}'
```

Response (`200`):

```json
{
  "query": "what is a vector database",
  "hits": [
    {
      "id": "0193f8e2-...",
      "score": 0.83,
      "title": "Intro to Qdrant",
      "content": "Qdrant is a vector database optimized for similarity search.",
      "source": "docs",
      "tags": ["qdrant", "vector"]
    }
  ]
}
```

Optional `tags` filter narrows results to documents tagged with at least one of the provided tags:

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python web framework", "tags": ["fastapi"], "limit": 5}'
```

## List documents

```bash
curl http://localhost:8000/api/v1/documents?skip=0&limit=50
```

Paginated. `limit` max is 100.

## Get / Delete

```bash
curl http://localhost:8000/api/v1/documents/{id}
curl -X DELETE http://localhost:8000/api/v1/documents/{id}
```

Delete removes the document from Postgres **and** the vector from Qdrant in one call.

## Data model

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID (v7) | Same id is used as the Qdrant point id |
| `title` | string (1–255) | Included in the text that is embedded |
| `content` | text | Included in the text that is embedded |
| `source` | string (optional) | Free-form origin label |
| `tags` | list of strings | Filterable in search |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

Postgres is the source of truth for metadata. Qdrant stores vectors plus a denormalized payload (title, content, source, tags) so search hits can be rendered without a Postgres round-trip.
