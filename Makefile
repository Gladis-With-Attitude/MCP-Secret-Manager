PYTHON ?= python3
COMPOSE ?= docker compose
ENV_FILE ?= configs/local.env.example

.PHONY: install-dev up down logs format lint typecheck test verify

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

up:
	$(COMPOSE) --env-file $(ENV_FILE) up -d postgres

down:
	$(COMPOSE) --env-file $(ENV_FILE) down

logs:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f postgres

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src tests

test:
	$(PYTHON) -m pytest

verify: lint typecheck test
