FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt api/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

ENV FASTEMBED_CACHE_PATH=/opt/fastembed \
    EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

RUN python -c "import os; from fastembed import TextEmbedding; TextEmbedding(model_name=os.environ['EMBEDDING_MODEL'])"

COPY api/ .
COPY scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV PYTHONPATH=/app

CMD ["/app/start.sh"]
