#!/bin/bash

HELP_TEXT="
${BLUE}FastAPI + Qdrant Starter — Dev Toolbox${NC}

Usage: ./dev/toolbox/run <command> [args]

${GREEN}Docker${NC}
  up                 Start all services
  down               Stop and remove all services
  stop               Stop services (keep containers)
  start              Start stopped services
  restart            Restart all services
  rebuild [service]  Rebuild containers (no cache)
  logs [service]     Tail logs (default: all)
  ps                 Show running containers

${GREEN}Shell${NC}
  shell:api          Open bash in API container
  shell:db           Open psql shell

${GREEN}Database${NC}
  migrate            Run alembic migrations (upgrade head)
  migrate:status     Show current migration revision
  migrate:history    Show migration history

${GREEN}Health & Status${NC}
  health             Check health of all services
  status             Show service ports and URLs

${GREEN}Linting & Formatting${NC}
  lint               Run all linters (ruff, mypy)
  format             Auto-format all Python code

${GREEN}Testing${NC}
  test               Run API tests

${GREEN}Utilities${NC}
  seed               Index sample documents via API
  search <query>     Run a semantic search
  help               Show this help message
"
