# Embeddings

The API turns text into vectors using one of two built-in engines. You pick which one by setting `EMBED_ENGINE`.

Both engines use the same four env vars — no code changes needed to switch.

## Option A — fastembed (default, local, no API key)

Runs a small model in-process via ONNX Runtime. Works out of the box.

```
EMBED_ENGINE=fastembed
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384
```

Good fit when:
- You're indexing lots of documents and want to avoid per-call API costs
- You don't want an external dependency on OpenAI
- You're already running a container with spare CPU/RAM

Trade-offs:
- Adds ~300 MB to the image and ~150–250 MB resident RAM
- First embed call after startup loads the model (~1–3 s)
- First run on a fresh container downloads the model weights (~30 MB)

## Option B — OpenAI embeddings API

Calls OpenAI's `/v1/embeddings`. You need an API key.

```
EMBED_ENGINE=openai
EMBED_ENGINE_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

Good fit when:
- You have low/medium traffic and don't want to pay for always-on CPU/RAM
- You want top-tier embedding quality (`text-embedding-3-large`)
- You prefer a small, simple API container

Trade-offs:
- Per-call cost (pennies at small scale, real money at million-doc scale)
- Network latency (~100–300 ms per call) and external dependency

## How to set the variables

**Locally** — put them in a `.env` file at the repo root, then `./dev/toolbox/run up`:

```bash
# .env
EMBED_ENGINE=openai
EMBED_ENGINE_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

**On Railway** — add them as service variables on the `api` service, then redeploy. See [deployment.md](deployment.md).

## Switching engines after you've already indexed data

Vectors from different models live in different spaces and aren't comparable. If you change `EMBED_ENGINE`, `EMBEDDING_MODEL`, or `EMBEDDING_DIM` after indexing, you must wipe Qdrant and re-index.

**Locally:**

```bash
docker compose down -v    # drops the qdrantdata volume
./dev/toolbox/run up
./dev/toolbox/run seed    # or re-index your own data
```

**On Railway:** delete the Qdrant service volume (or recreate the Qdrant service) and re-index.

## LLMs vs embedders — a common confusion

An embedding model is separate from an LLM. Its only job is to turn text into a vector. You can embed with fastembed locally and still feed retrieved documents to ChatGPT (or any other LLM) — the LLM never sees the vectors, only the retrieved text.

The one hard rule: **the query and the documents must be embedded with the same model.** That's why switching the engine or model requires re-indexing.

## Adding a third engine

To add Cohere, Voyage, or any other provider:

1. Open `api/app/services/embeddings.py`
2. Add an `_embed_<name>` async function that takes `list[str]` and returns `list[list[float]]`
3. Add a branch in `embed_texts` that dispatches on `settings.EMBED_ENGINE == "<name>"`
4. Update `EMBEDDING_DIM` to match that provider's vector size
