PYTHON ?= python3
COMPOSE ?= docker compose
ENV_FILE ?= .env.example
DB_DOWN_REVISION ?= -1
DB_REVISION_MESSAGE ?= database change
DB_AUTOGENERATE ?= false

.PHONY: install-dev up up-db down logs logs-db logs-bootstrap db-upgrade db-downgrade db-current db-history db-revision db-reset seed-run format lint typecheck test verify

install-dev:
	cd backend && $(PYTHON) -m pip install -e ".[dev]"

up:
	$(COMPOSE) --env-file $(ENV_FILE) up -d --build postgres backend frontend

up-db:
	$(COMPOSE) --env-file $(ENV_FILE) up -d postgres

down:
	$(COMPOSE) --env-file $(ENV_FILE) down

logs:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f postgres migrations bootstrap backend frontend

logs-db:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f postgres

logs-bootstrap:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f bootstrap

seed-run:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm bootstrap sh /app/scripts/bootstrap-system.sh

db-upgrade:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm migrations sh /app/scripts/manage-db.sh upgrade

db-downgrade:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm migrations sh /app/scripts/manage-db.sh downgrade $(DB_DOWN_REVISION)

db-current:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm migrations sh /app/scripts/manage-db.sh current

db-history:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm --no-deps migrations sh /app/scripts/manage-db.sh history

db-revision:
	$(COMPOSE) --env-file $(ENV_FILE) run --rm migrations sh /app/scripts/manage-db.sh revision --message "$(DB_REVISION_MESSAGE)" $(if $(filter true,$(DB_AUTOGENERATE)),--autogenerate,)

db-reset:
	@test "$(CONFIRM_RESET)" = "dev" || (echo "Refusing to reset database. Re-run with CONFIRM_RESET=dev."; exit 1)
	$(COMPOSE) --env-file $(ENV_FILE) run --rm -e MCP_SECRET_MANAGER_ALLOW_DB_RESET=true migrations sh /app/scripts/manage-db.sh reset

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
