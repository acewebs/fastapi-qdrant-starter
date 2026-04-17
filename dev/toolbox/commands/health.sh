#!/bin/bash

case "$1" in
    health)
        echo ""
        step "Checking API..."
        api_response=$(curl -sf http://localhost:8000/health 2>/dev/null)
        if [ $? -eq 0 ]; then
            success "API:     healthy — $api_response"
        else
            error "API:     unreachable"
        fi

        step "Checking Postgres..."
        dk-c exec -T db pg_isready -U app > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            success "DB:      healthy"
        else
            error "DB:      unreachable"
        fi

        step "Checking Qdrant..."
        qdrant_response=$(curl -sf http://localhost:6333/readyz 2>/dev/null)
        if [ $? -eq 0 ]; then
            success "Qdrant:  healthy"
        else
            error "Qdrant:  unreachable"
        fi

        echo ""
        exit 0
        ;;
    status)
        echo ""
        info "Service URLs:"
        echo "  API:      http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo "  Qdrant:   http://localhost:6333/dashboard"
        echo "  Postgres: localhost:5432"
        echo ""
        dk-c ps
        exit 0
        ;;
esac
