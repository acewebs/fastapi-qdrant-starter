# Local Development

## Prerequisites

- Docker + Docker Compose
- (Optional) Python 3.12 if you want to run the API outside Docker

## Configuration

The template works out of the box with no setup — every env var in `docker-compose.yml` has a safe local default (insecure credentials like `POSTGRES_PASSWORD=app`, which is fine for localhost-only).

To override any of them, copy the example file and edit it:

```bash
cp .env.example .env
```

`docker-compose` reads `.env` automatically on `up`. The file is gitignored.

You **must** create a `.env` only if you want to use OpenAI for embeddings — then set `EMBED_ENGINE=openai` and `EMBED_ENGINE_KEY=sk-...` (see [embeddings.md](embeddings.md)).

## Start everything

```bash
./dev/toolbox/run up
```

This builds the `api` image and starts `api`, `db` (Postgres), and `qdrant`.

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

Tip — add a shell alias:

```bash
alias d='bash ./dev/toolbox/run'
# d up, d logs api, d health, d seed, d search "query"
```

## Toolbox commands

All commands live under `./dev/toolbox/run <command>`. Run `./dev/toolbox/run help` for the full list.

**Docker**
- `up` — start all services
- `down` — stop and remove containers
- `rebuild [service]` — rebuild with `--no-cache`
- `logs [service]` — tail logs
- `ps` — show running containers

**Shell**
- `shell:api` — bash inside the API container
- `shell:db` — psql into Postgres

**Database**
- `migrate` — run `alembic upgrade head`
- `migrate:status` — show current revision
- `migrate:history` — show migration history

**Quality**
- `lint` — ruff + mypy
- `format` — auto-format Python code
- `test` — run pytest inside the API container

**Utilities**
- `health` — check API / DB / Qdrant readiness
- `status` — show service URLs + `docker compose ps`
- `seed` — index five sample documents via the API
- `search <query>` — run a semantic search and pretty-print the JSON

## Running the API outside Docker

```bash
cd api
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/app
export QDRANT_URL=http://localhost:6333
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

You still need `db` and `qdrant` running (e.g. via `docker compose up db qdrant`).

## Database migrations

```bash
# After changing a SQLAlchemy model
./dev/toolbox/run shell:api
alembic revision --autogenerate -m "add field X to documents"
exit

# Apply
./dev/toolbox/run migrate
```

Migrations live in `api/alembic/versions/`.

## Tests

```bash
./dev/toolbox/run test
```

Tests run against SQLite (aiosqlite) and mock both the Qdrant client and the embedder, so they're fast and don't require external services. See `api/tests/conftest.py`.

To run a single test:

```bash
./dev/toolbox/run test tests/test_documents.py::test_create_document
```

## Extending the API

- **Add a field to `Document`** — edit `api/app/shared/models/document.py`, then create a migration. Update `api/app/schemas/document.py` and the seed script if needed.
- **Add a new endpoint** — create `api/app/api/routes/<name>.py` and register it in `api/app/main.py`.
- **Add a new embedder** — see [embeddings.md](embeddings.md#adding-a-third-engine).
- **Change the Qdrant distance metric** — edit `_ensure_collection` in `api/app/core/qdrant.py`.
