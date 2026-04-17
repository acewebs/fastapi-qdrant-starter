# FastAPI + Qdrant Starter

A minimal vector-search starter: FastAPI + Qdrant + PostgreSQL, designed for [Railway](https://railway.app) deployment.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/fastapi-qdrant-starter)

## What You Get

- **Indexing API** — `POST /api/v1/documents` persists a document to Postgres and upserts its embedding into Qdrant
- **Semantic search API** — `POST /api/v1/search` embeds the query and returns the most similar documents
- **Pluggable embedder** — local (fastembed) by default, or flip four env vars to use OpenAI
- **Production structure** — async SQLAlchemy, Alembic migrations, dockerized services
- **One command to run** — `./dev/toolbox/run up` starts everything locally

## Architecture

```
[ client ]
     |
   api (FastAPI)           :8000
     |  \
     |   \-> qdrant         :6333   (vectors)
     |
   db (Postgres)            :5432   (document metadata)
```

On `POST /api/v1/documents`: persist to Postgres → embed title+content → upsert vector into Qdrant.
On `POST /api/v1/search`: embed query → ANN search in Qdrant → return hits with scores.

## Services

| Service | Tech | Description |
|---------|------|-------------|
| **api** | FastAPI, SQLAlchemy, Alembic | REST API + embedding pipeline |
| **db** | PostgreSQL 16 | Document metadata store |
| **qdrant** | Qdrant 1.12 | Vector database |

## Quick Start (Local)

```bash
git clone <your-fork-url>
cd fastapi-qdrant-starter

./dev/toolbox/run up        # start everything
./dev/toolbox/run seed      # index 5 sample documents
./dev/toolbox/run search "how do I deploy python on railway"
```

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

See [docs/development.md](docs/development.md) for the full toolbox, tests, and migrations.

## API at a glance

```bash
# Index a document
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "Intro to Qdrant", "content": "Qdrant is a vector database.", "tags": ["qdrant"]}'

# Search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is a vector database", "limit": 5}'
```

Full endpoint reference: [docs/api-reference.md](docs/api-reference.md).

## Deploy on Railway

Click the button at the top — Railway forks the repo and provisions `api`, Postgres, and Qdrant. The template auto-generates random secrets for `SECRET_KEY`, `POSTGRES_PASSWORD`, `QDRANT__SERVICE__API_KEY`, and **`API_KEY`**.

### After the template deploys — grab your API key

The API is protected with `API_KEY`. To call it, copy the auto-generated value from Railway:

1. Open the `api` service in your Railway project
2. Go to **Variables** → find `API_KEY` → click the value to reveal/copy it
3. Send it as a header on every request:

```bash
curl -H "X-API-Key: <paste-value-here>" https://your-api.up.railway.app/api/v1/documents
```

`/health` and `/api/v1/app` stay open (no key needed) so platform healthchecks work.

Full walkthrough + env var reference: [docs/deployment.md](docs/deployment.md).

## Documentation

| Guide | Description |
|-------|-------------|
| [docs/development.md](docs/development.md) | Local setup, toolbox commands, tests, migrations |
| [docs/deployment.md](docs/deployment.md) | Railway deployment, env vars, volumes |
| [docs/embeddings.md](docs/embeddings.md) | fastembed vs OpenAI — trade-offs and how to switch |
| [docs/api-reference.md](docs/api-reference.md) | Endpoints, request/response formats, data model |

## Project Structure

```
.
├── api/              # FastAPI backend
│   ├── app/
│   │   ├── api/routes/       # HTTP endpoints
│   │   ├── core/             # config, Qdrant client
│   │   ├── db/               # SQLAlchemy engine + session
│   │   ├── services/         # document, search, embeddings
│   │   ├── schemas/          # Pydantic models
│   │   └── shared/models/    # SQLAlchemy models
│   ├── alembic/              # Database migrations
│   └── tests/
├── dev/toolbox/              # Dev CLI
├── docs/                     # Documentation
└── docker-compose.yml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
