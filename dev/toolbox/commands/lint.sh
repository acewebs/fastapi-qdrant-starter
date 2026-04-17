#!/bin/bash

case "$1" in
    lint|lint:all|lint:api)
        info "Linting API..."
        run_in_service api ruff check app/ tests/
        run_in_service api ruff format --check app/ tests/
        run_in_service api mypy app/ --ignore-missing-imports
        success "API lint passed"
        exit 0
        ;;
    format)
        info "Formatting all Python code..."
        run_in_service api ruff format app/ tests/
        run_in_service api ruff check --fix app/ tests/
        success "Formatting complete"
        exit 0
        ;;
esac
