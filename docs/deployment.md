# Deploying on Railway

This template is designed to deploy with one click to [Railway](https://railway.app).

## Deploy

1. Click the **Deploy on Railway** button in the main [README](../README.md)
2. Railway forks the repo to your GitHub account and provisions three services: `api`, `db` (Postgres), and `qdrant`
3. Wait for the first build. The `api` service auto-runs `alembic upgrade head` on boot.

### Manual setup (if you're creating the services by hand)

If you're wiring a Railway project yourself instead of using the template:

1. **`api`** — "Deploy from GitHub repo" → this repo. **Set Root Directory to `api`.** Railway will auto-detect `api/Dockerfile` and `api/railway.toml` (which sets `/health` as the healthcheck).
2. **`db`** — "Deploy from Docker Image" → `postgres:16`. Attach a volume to `/var/lib/postgresql/data`.
3. **`qdrant`** — "Deploy from Docker Image" → `qdrant/qdrant:v1.12.4`. Attach a volume to `/qdrant/storage`.
4. Set env vars on each service (see below), then redeploy `api`.

Once the deploy is green, your API is live at the Railway-generated domain for the `api` service. Visit `/docs` for the auto-generated OpenAPI UI.

### Grab your API key

The template auto-generates a random `API_KEY` on the `api` service. Every call to `/api/v1/documents` and `/api/v1/search` needs it as a header.

1. Open the `api` service → **Variables**
2. Copy the value of `API_KEY`
3. Send it on requests:

   ```bash
   curl -H "X-API-Key: <paste-value>" https://your-api.up.railway.app/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "hello"}'
   ```

`/health` and `/api/v1/app` don't require the key — platform healthchecks and status probes still work.

If you want to run the API **without** authentication, delete the `API_KEY` variable on the `api` service and redeploy. Not recommended for any publicly-reachable deploy.

## Environment variables

Every variable has a safe default, so the template works out of the box. Values below show what the Railway template sets — override any of them per-service.

### On the `db` service

| Variable | What to set | Notes |
|----------|-------------|-------|
| `POSTGRES_USER` | `app` | Username Postgres creates on first boot |
| `POSTGRES_PASSWORD` | **Generate random** | Use Railway's *"Generate"* option (32+ chars) |
| `POSTGRES_DB` | `app` | Database name |

### On the `qdrant` service

| Variable | What to set | Notes |
|----------|-------------|-------|
| `QDRANT__SERVICE__API_KEY` | **Generate random** (or leave empty) | Enables bearer-token auth on Qdrant |

### On the `api` service

**Required — references to other services**

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `postgresql://${{db.POSTGRES_USER}}:${{db.POSTGRES_PASSWORD}}@${{db.RAILWAY_PRIVATE_DOMAIN}}:5432/${{db.POSTGRES_DB}}` | Railway reference; API auto-normalizes the scheme to `postgresql+asyncpg://` |
| `QDRANT_URL` | `http://${{qdrant.RAILWAY_PRIVATE_DOMAIN}}:6333` | Internal networking to the Qdrant service |
| `QDRANT_API_KEY` | `${{qdrant.QDRANT__SERVICE__API_KEY}}` | Mirror whatever is set on Qdrant |
| `SECRET_KEY` | **Generate random** | 64+ chars |
| `API_KEY` | **Generate random** | 32+ chars. Strongly recommended on any public deploy. When set, `/api/v1/documents` and `/api/v1/search` require the header `X-API-Key: <value>`. `/health` and `/api/v1/app` stay open. Leave empty to keep the API open. |

**Embeddings — pick one**

| Variable | Value (fastembed, default) | Value (OpenAI) |
|----------|----------------------------|----------------|
| `EMBED_ENGINE` | `fastembed` | `openai` |
| `EMBED_ENGINE_KEY` | — | `sk-...` (your OpenAI API key) |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | `text-embedding-3-small` |
| `EMBEDDING_DIM` | `384` | `1536` |

See [embeddings.md](embeddings.md) for the full trade-offs.

**Optional**

| Variable | Default | When to set |
|----------|---------|-------------|
| `QDRANT_COLLECTION` | `documents` | To use a different collection name |
| `CORS_ORIGINS` | `http://localhost:3000` | Your frontend origin(s), comma-separated |
| `APP_ENV` | `development` | Set to `production` on Railway |
| `APP_NAME` | `qdrant-starter-api` | Shown in `/api/v1/app` |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warning`, `error` |
| `HOST` | `0.0.0.0` | Almost never needed |
| `PORT` | `8000` | Railway injects this automatically — don't override |

## Volumes — don't lose your data

Two volumes matter:

- **Postgres data** — attach a Railway volume to `/var/lib/postgresql/data` on the `db` service. (Or swap the included Postgres for Railway's managed Postgres plugin and skip this.)
- **Qdrant storage** — attach a Railway volume to `/qdrant/storage` on the `qdrant` service. Without it, your vectors disappear on every redeploy.

If you're using `fastembed`, also consider a small volume at `/root/.cache/fastembed` on the `api` service so model weights don't re-download on every redeploy.

## Considerations

**Cold start.** The first request after a deploy with `fastembed` loads the ONNX model (~1–3 s). If latency matters, warm the model in the FastAPI `lifespan` by calling `embed_text("warmup")` at startup.

**RAM sizing.** With `fastembed`, give the `api` service at least 512 MB, ideally 1 GB. With `EMBED_ENGINE=openai`, 256–512 MB is plenty.

**Using Railway's managed Postgres plugin.** You can swap the bundled `db` service for Railway's managed Postgres. Set `DATABASE_URL=${{Postgres.DATABASE_URL}}` on `api`. The API normalizes the scheme to `postgresql+asyncpg://` automatically.

## After deploying — make it yours

1. Clone your forked repo locally
2. Adjust the `Document` model and `Search` schema to match your domain
3. Pick an embedder — see [embeddings.md](embeddings.md)
4. Push changes — Railway auto-deploys from your fork
