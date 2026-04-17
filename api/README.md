# API Service (FastAPI + Qdrant)

REST API backend for the vector-search starter template.

## What it does

- Exposes endpoints to index documents and run semantic search
- Stores document metadata in PostgreSQL (via async SQLAlchemy)
- Stores embeddings in Qdrant (via the async client)
- Generates embeddings via a pluggable engine — fastembed (local) or the OpenAI API
- Runs database migrations with Alembic

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/app` | App info |
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/documents` | Index a new document |
| GET | `/api/v1/documents/{id}` | Get document by id |
| DELETE | `/api/v1/documents/{id}` | Delete document (DB + Qdrant) |
| POST | `/api/v1/search` | Semantic search |

Full request/response formats: [../docs/api-reference.md](../docs/api-reference.md).

## Layout

```
app/
├── api/routes/       # HTTP endpoints
├── core/             # config, Qdrant client lifecycle
├── db/               # SQLAlchemy engine + session
├── services/         # document, search, embeddings
├── schemas/          # Pydantic request/response models
└── shared/models/    # SQLAlchemy models
```

## See also

- [../docs/development.md](../docs/development.md) — running locally, tests, migrations
- [../docs/embeddings.md](../docs/embeddings.md) — picking and switching the embedder
- [../docs/deployment.md](../docs/deployment.md) — Railway deployment
