PYTHON ?= python3
COMPOSE ?= docker compose
ENV_FILE ?= .env.example

.PHONY: install-dev up up-db down logs logs-db format lint typecheck test verify

install-dev:
	cd backend && $(PYTHON) -m pip install -e ".[dev]"

up:
	$(COMPOSE) --env-file $(ENV_FILE) up -d --build postgres backend frontend

up-db:
	$(COMPOSE) --env-file $(ENV_FILE) up -d postgres

down:
	$(COMPOSE) --env-file $(ENV_FILE) down

logs:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f postgres backend frontend

logs-db:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f postgres

format:
	cd backend && $(PYTHON) -m ruff format .
	cd frontend && npm run format

lint:
	cd backend && $(PYTHON) -m ruff format --check .
	cd backend && $(PYTHON) -m ruff check .
	cd frontend && npm run lint

typecheck:
	cd backend && $(PYTHON) -m mypy src tests
	cd frontend && npm run typecheck

test:
	cd backend && $(PYTHON) -m pytest

verify: lint typecheck test
