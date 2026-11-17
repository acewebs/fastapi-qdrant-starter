#!/bin/sh
set -e

if [ "$SKIP_MIGRATIONS" = "true" ]; then
    echo "Skipping migrations (SKIP_MIGRATIONS=true)"
else
    echo "Running database migrations..."
    alembic upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
