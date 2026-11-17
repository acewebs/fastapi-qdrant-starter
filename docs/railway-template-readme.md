# Deploy and Host Vector Knowledge Base API on Railway

A production-ready API for semantic search and AI knowledge bases. Index documents, generate embeddings, and retrieve relevant context by meaning rather than keywords. Built with FastAPI, Qdrant and PostgreSQL, it embeds locally with fastembed so it needs no external API key, and switches to OpenAI by setting one variable.

## About Hosting Vector Knowledge Base API

This template provisions a complete semantic search stack: a FastAPI app, a Qdrant vector database, and PostgreSQL for document metadata. Railway handles provisioning, secret generation and private networking, so the API reaches Qdrant and Postgres over the project's internal network and nothing but the API is exposed.

The deploy asks for nothing. On first boot the API runs its migrations, creates the Qdrant collection, and is ready to index and search. Embeddings run in-process via fastembed, with the model baked into the image so the first query does not wait on a download. Setting `OPENAI_API_KEY` switches embedding to OpenAI instead. Volumes keep vectors and metadata across redeploys, and the API refuses to start if the configured embedding dimensions disagree with an existing collection, rather than writing vectors it cannot search.

## Common Use Cases

- **RAG backend for an AI assistant**: retrieve relevant context before generating a response
- **Internal documentation search**: query company docs, wikis or policies in natural language
- **Knowledge for automation workflows**: give an n8n or Zapier agent a searchable memory. Pairs with the [n8n Production Setup with Workers](https://railway.com/deploy/n8n-production-starter-with-workers) template: deploy both into the same project and n8n reaches this API privately, with no public domain needed and no embedding provider key

## Dependencies for Vector Knowledge Base API Hosting

- **Qdrant**: vector database for similarity search
- **PostgreSQL**: structured storage for documents and metadata
- **fastembed**: local embedding model, bundled in the image

### Deployment Dependencies

- https://github.com/acewebs/fastapi-qdrant-starter
- https://github.com/acewebs/fastapi-qdrant-starter/blob/main/docs/deployment.md
- https://github.com/acewebs/fastapi-qdrant-starter/blob/main/docs/embeddings.md
- https://github.com/acewebs/fastapi-qdrant-starter/blob/main/docs/api-reference.md
- https://qdrant.tech/documentation/
- https://github.com/qdrant/fastembed

### Implementation Details

Every `/api/v1` endpoint requires the `API_KEY` that Railway generates for you, sent as an `X-API-Key` header. `/health` and `/api/health` stay open so platform healthchecks work, and interactive API docs are at `/docs`.

```bash
# Index a document
curl -X POST https://your-api.up.railway.app/api/v1/documents \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Intro to Qdrant",
    "content": "Qdrant is a vector database optimized for similarity search.",
    "tags": ["qdrant", "vector"]
  }'

# Semantic search
curl -X POST https://your-api.up.railway.app/api/v1/search \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "what is a vector database", "limit": 5}'
```

To use OpenAI embeddings instead of the local model, set `OPENAI_API_KEY` on the `vector index` service. `OPENAI_MODEL` and `OPENAI_DIMENSIONS` default to `text-embedding-3-large` at 1024 dimensions. Do this before indexing: vectors from different models are not comparable, so switching later means reindexing into a fresh collection.

## Why Deploy Vector Knowledge Base API on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying Vector Knowledge Base API on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.
