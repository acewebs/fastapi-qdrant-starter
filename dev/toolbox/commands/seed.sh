#!/bin/bash

case "$1" in
    seed)
        info "Indexing sample documents..."
        echo ""

        titles=(
            "Introduction to Qdrant"
            "FastAPI in production"
            "Semantic search primer"
            "PostgreSQL performance tuning"
            "Running Python on Railway"
        )
        contents=(
            "Qdrant is a vector database optimized for similarity search over dense embeddings."
            "FastAPI is a modern, high-performance web framework for building APIs with Python 3.10+."
            "Semantic search compares the meaning of a query against documents rather than keywords."
            "Indexes, connection pools, and EXPLAIN ANALYZE are the three tools you reach for first."
            "Railway deploys Docker-based services with a managed Postgres and zero-config networking."
        )
        tags_list=(
            "qdrant,vector"
            "fastapi,python"
            "search,ml"
            "postgres,db"
            "deploy,railway"
        )

        for i in "${!titles[@]}"; do
            IFS=',' read -ra tags_arr <<< "${tags_list[$i]}"
            tags_json=$(printf '"%s",' "${tags_arr[@]}")
            tags_json="[${tags_json%,}]"

            response=$(curl -sf -X POST http://localhost:8000/api/v1/documents \
                -H "Content-Type: application/json" \
                -d "{\"title\": \"${titles[$i]}\", \"content\": \"${contents[$i]}\", \"tags\": ${tags_json}}" 2>/dev/null)

            if [ $? -eq 0 ]; then
                success "Indexed: ${titles[$i]}"
            else
                error "Failed:  ${titles[$i]}"
            fi
        done

        echo ""
        success "Seeding complete — try: ./dev/toolbox/run search 'how do I deploy python'"
        exit 0
        ;;
    search)
        shift
        query="$*"
        if [ -z "$query" ]; then
            error "Usage: ./dev/toolbox/run search <query>"
            exit 1
        fi
        info "Searching for: $query"
        echo ""
        curl -sf -X POST http://localhost:8000/api/v1/search \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$query\", \"limit\": 5}" | python3 -m json.tool
        exit 0
        ;;
esac
