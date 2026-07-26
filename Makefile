PYTHON ?= python3
DOCKER ?= docker
COMPOSE ?= docker compose
ENV_FILE ?= .env.example
DOCKER_BUILD_PROGRESS ?= plain
DB_DOWN_REVISION ?= -1
DB_REVISION_MESSAGE ?= database change
DB_AUTOGENERATE ?= false
FRONTEND_URL ?= http://localhost:3000
OPEN_BROWSER ?= true
FRONTEND_BROWSER ?= Firefox
NEXT_PUBLIC_API_BASE_URL ?= http://127.0.0.1:8000
NEXT_PUBLIC_APP_ENV ?= test
PLAYWRIGHT_BASE_URL ?= http://127.0.0.1:3000
PLAYWRIGHT_ADMIN_API_KEY ?=
WARM_FRONTEND ?= true
WARM_PAGE ?= true
PAGE_WARM_TIMEOUT_SECONDS ?= 120
VAULT_ID ?= vault-id
PROJECT_ID ?= project-id
SECRET_ID ?= secret-id
VERSION_ID ?= version-id
API_KEY_ID ?= api-key-id
AUDIT_EVENT_ID ?= audit-event-id
ROLE_ID ?= role-id
USER_ID ?= user-id
RELEASE_VERSION ?= dev
RELEASE_DIST_DIR ?= dist/release
RELEASE_ARCHIVE_PREFIX ?= mcp-secret-manager-$(RELEASE_VERSION)

GITLEAKS_IMAGE ?= ghcr.io/gitleaks/gitleaks:v8.30.1
PIP_AUDIT_VERSION ?= 2.10.1

.PHONY: install-dev up up-db up-observability down logs logs-db logs-bootstrap db-upgrade db-downgrade db-current db-history db-revision db-reset seed-run frontend-warm-pages secret-scan dependency-scan docker-build docker-build-production playwright-e2e release-artifacts format lint typecheck test verify pages page-home page-design-system page-dashboard page-vaults page-vault-new page-vault page-vault-edit page-projects page-vault-projects page-project-new page-project page-project-edit page-secrets page-project-secrets page-secret-new page-secret page-secret-edit page-secret-versions page-secret-version page-secret-rotate page-api-keys page-api-key-new page-api-key page-audit page-audit-event page-rbac page-rbac-roles page-rbac-role-new page-rbac-role page-rbac-role-edit page-rbac-user page-profile page-settings page-settings-security page-settings-preferences page-settings-notifications

define open_frontend_page
	@url="$(FRONTEND_URL)$(1)"; \
	printf "%s\n" "$$url"; \
	if [ "$(WARM_PAGE)" = "true" ]; then \
		printf "Warming %s...\n" "$(1)"; \
		$(COMPOSE) --env-file $(ENV_FILE) exec -T frontend sh -c 'wget -q -O /dev/null --timeout=$(PAGE_WARM_TIMEOUT_SECONDS) "http://127.0.0.1:3000$(1)"' >/dev/null 2>&1 || true; \
	fi; \
	if [ "$(OPEN_BROWSER)" = "true" ]; then \
		if command -v open >/dev/null 2>&1; then \
			open -a "$(FRONTEND_BROWSER)" "$$url"; \
		elif command -v firefox >/dev/null 2>&1; then \
			firefox "$$url"; \
		elif command -v xdg-open >/dev/null 2>&1; then \
			xdg-open "$$url" >/dev/null 2>&1 || true; \
		else \
			printf "No browser opener found. Open the URL above manually.\n"; \
		fi; \
	fi
endef

install-dev:
	cd backend && $(PYTHON) -m pip install -e ".[dev]"

up:
	$(COMPOSE) --env-file $(ENV_FILE) up -d --build postgres backend frontend
	@if [ "$(WARM_FRONTEND)" = "true" ]; then $(MAKE) frontend-warm-pages; fi

up-db:
	$(COMPOSE) --env-file $(ENV_FILE) up -d postgres

up-observability:
	$(COMPOSE) --env-file $(ENV_FILE) --profile observability up -d prometheus grafana

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

secret-scan:
	docker run --rm -v "$(CURDIR):/repo" $(GITLEAKS_IMAGE) git --verbose --redact /repo

dependency-scan:
	cd backend && uv run --extra dev --with pip-audit==$(PIP_AUDIT_VERSION) pip-audit --progress-spinner off --skip-editable
	cd frontend && npm audit --audit-level=high

docker-build:
	$(DOCKER) build --progress=$(DOCKER_BUILD_PROGRESS) --target development -t mcp-secret-manager-backend:ci ./backend
	$(DOCKER) build --progress=$(DOCKER_BUILD_PROGRESS) --target development -t mcp-secret-manager-frontend:ci ./frontend

docker-build-production:
	$(DOCKER) build --progress=$(DOCKER_BUILD_PROGRESS) --target production -t mcp-secret-manager-backend:production ./backend
	$(DOCKER) build --progress=$(DOCKER_BUILD_PROGRESS) --target production -t mcp-secret-manager-frontend:production ./frontend

playwright-e2e:
	@test -n "$(PLAYWRIGHT_ADMIN_API_KEY)" || (echo "PLAYWRIGHT_ADMIN_API_KEY is required."; exit 1)
	cd frontend && NEXT_PUBLIC_API_BASE_URL="$(NEXT_PUBLIC_API_BASE_URL)" NEXT_PUBLIC_APP_ENV="$(NEXT_PUBLIC_APP_ENV)" npm run build
	cd frontend && NEXT_PUBLIC_API_BASE_URL="$(NEXT_PUBLIC_API_BASE_URL)" NEXT_PUBLIC_APP_ENV="$(NEXT_PUBLIC_APP_ENV)" PLAYWRIGHT_BASE_URL="$(PLAYWRIGHT_BASE_URL)" PLAYWRIGHT_ADMIN_API_KEY="$(PLAYWRIGHT_ADMIN_API_KEY)" npm run e2e

release-artifacts:
	@case "$(RELEASE_VERSION)" in ""|*[!A-Za-z0-9._-]*) echo "RELEASE_VERSION must contain only letters, numbers, dots, underscores or hyphens."; exit 1;; esac
	rm -rf "$(RELEASE_DIST_DIR)"
	mkdir -p "$(RELEASE_DIST_DIR)"
	git archive --format=tar.gz --prefix="$(RELEASE_ARCHIVE_PREFIX)/" -o "$(RELEASE_DIST_DIR)/$(RELEASE_ARCHIVE_PREFIX)-source.tar.gz" HEAD
	@sha="$$(git rev-parse HEAD)"; \
	ref="$$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"; \
	created_at="$$(date -u +%Y-%m-%dT%H:%M:%SZ)"; \
	printf '{\n' > "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "name": "mcp-secret-manager",\n' >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "version": "%s",\n' "$(RELEASE_VERSION)" >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "git_sha": "%s",\n' "$$sha" >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "git_ref": "%s",\n' "$$ref" >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "created_at": "%s",\n' "$$created_at" >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '  "archive": "%s-source.tar.gz"\n' "$(RELEASE_ARCHIVE_PREFIX)" >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '}\n' >> "$(RELEASE_DIST_DIR)/release-manifest.json"; \
	printf '# MCP Secret Manager %s\n\n' "$(RELEASE_VERSION)" > "$(RELEASE_DIST_DIR)/RELEASE_NOTES.md"; \
	printf 'Release validation is performed by the GitHub Actions release workflow before these artifacts are published.\n\n' >> "$(RELEASE_DIST_DIR)/RELEASE_NOTES.md"; \
	printf 'Commit: `%s`\n' "$$sha" >> "$(RELEASE_DIST_DIR)/RELEASE_NOTES.md"
	cd "$(RELEASE_DIST_DIR)" && sha256sum "$(RELEASE_ARCHIVE_PREFIX)-source.tar.gz" release-manifest.json RELEASE_NOTES.md > SHA256SUMS

frontend-warm-pages:
	@printf "Warming frontend pages in Next.js dev server...\n"
	@$(COMPOSE) --env-file $(ENV_FILE) exec -T frontend sh -c ' \
		set -eu; \
		base="http://127.0.0.1:3000"; \
		for attempt in $$(seq 1 60); do \
			if wget -q -O /dev/null --timeout=2 "$$base/"; then break; fi; \
			if [ "$$attempt" = "60" ]; then echo "Frontend did not become ready."; exit 1; fi; \
			sleep 1; \
		done; \
		for route in \
			/ \
			/design-system \
			/dashboard \
			/vaults \
			/vaults/new \
			/vaults/$(VAULT_ID) \
			/vaults/$(VAULT_ID)/edit \
			/projects \
			/vaults/$(VAULT_ID)/projects \
			/vaults/$(VAULT_ID)/projects/new \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID) \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/edit \
			/secrets \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/new \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID) \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/edit \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions/$(VERSION_ID) \
			/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions/rotate \
			/api-keys \
			/api-keys/new \
			/api-keys/$(API_KEY_ID) \
			/audit \
			/audit/$(AUDIT_EVENT_ID) \
			/rbac \
			/rbac/roles \
			/rbac/roles/new \
			/rbac/roles/$(ROLE_ID) \
			/rbac/roles/$(ROLE_ID)/edit \
			/rbac/users/$(USER_ID) \
			/profile \
			/settings \
			/settings/security \
			/settings/preferences \
			/settings/notifications; do \
			printf "  %s\n" "$$route"; \
			wget -q -O /dev/null --timeout=$(PAGE_WARM_TIMEOUT_SECONDS) "$$base$$route"; \
		done; \
	'
	@printf "Frontend pages warmed.\n"

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

pages:
	@printf "Frontend base URL: %s\n\n" "$(FRONTEND_URL)"
	@printf "Public\n"
	@printf "  make page-home                      / \n"
	@printf "  make page-design-system             /design-system\n"
	@printf "\nAuthenticated\n"
	@printf "  make page-dashboard                 /dashboard\n"
	@printf "  make page-vaults                    /vaults\n"
	@printf "  make page-vault-new                 /vaults/new\n"
	@printf "  make page-vault VAULT_ID=...        /vaults/{vaultId}\n"
	@printf "  make page-vault-edit VAULT_ID=...   /vaults/{vaultId}/edit\n"
	@printf "  make page-projects                  /projects\n"
	@printf "  make page-vault-projects VAULT_ID=...                      /vaults/{vaultId}/projects\n"
	@printf "  make page-project-new VAULT_ID=...                         /vaults/{vaultId}/projects/new\n"
	@printf "  make page-project VAULT_ID=... PROJECT_ID=...              /vaults/{vaultId}/projects/{projectId}\n"
	@printf "  make page-project-edit VAULT_ID=... PROJECT_ID=...         /vaults/{vaultId}/projects/{projectId}/edit\n"
	@printf "  make page-secrets                   /secrets\n"
	@printf "  make page-project-secrets VAULT_ID=... PROJECT_ID=...      /vaults/{vaultId}/projects/{projectId}/secrets\n"
	@printf "  make page-secret-new VAULT_ID=... PROJECT_ID=...           /vaults/{vaultId}/projects/{projectId}/secrets/new\n"
	@printf "  make page-secret VAULT_ID=... PROJECT_ID=... SECRET_ID=... /vaults/{vaultId}/projects/{projectId}/secrets/{secretId}\n"
	@printf "  make page-secret-edit VAULT_ID=... PROJECT_ID=... SECRET_ID=...      /vaults/{vaultId}/projects/{projectId}/secrets/{secretId}/edit\n"
	@printf "  make page-secret-versions VAULT_ID=... PROJECT_ID=... SECRET_ID=...  /vaults/{vaultId}/projects/{projectId}/secrets/{secretId}/versions\n"
	@printf "  make page-secret-version VAULT_ID=... PROJECT_ID=... SECRET_ID=... VERSION_ID=... /vaults/{vaultId}/projects/{projectId}/secrets/{secretId}/versions/{versionId}\n"
	@printf "  make page-secret-rotate VAULT_ID=... PROJECT_ID=... SECRET_ID=...    /vaults/{vaultId}/projects/{projectId}/secrets/{secretId}/versions/rotate\n"
	@printf "  make page-api-keys                  /api-keys\n"
	@printf "  make page-api-key-new               /api-keys/new\n"
	@printf "  make page-api-key API_KEY_ID=...    /api-keys/{apiKeyId}\n"
	@printf "  make page-audit                     /audit\n"
	@printf "  make page-audit-event AUDIT_EVENT_ID=... /audit/{eventId}\n"
	@printf "  make page-rbac                      /rbac\n"
	@printf "  make page-rbac-roles                /rbac/roles\n"
	@printf "  make page-rbac-role-new             /rbac/roles/new\n"
	@printf "  make page-rbac-role ROLE_ID=...     /rbac/roles/{roleId}\n"
	@printf "  make page-rbac-role-edit ROLE_ID=... /rbac/roles/{roleId}/edit\n"
	@printf "  make page-rbac-user USER_ID=...     /rbac/users/{userId}\n"
	@printf "  make page-profile                   /profile\n"
	@printf "  make page-settings                  /settings\n"
	@printf "  make page-settings-security         /settings/security\n"
	@printf "  make page-settings-preferences      /settings/preferences\n"
	@printf "  make page-settings-notifications    /settings/notifications\n"
	@printf "\nOptions: FRONTEND_URL=http://localhost:3000 FRONTEND_BROWSER=Firefox OPEN_BROWSER=false WARM_PAGE=false WARM_FRONTEND=false\n"

page-home:
	$(call open_frontend_page,/)

page-design-system:
	$(call open_frontend_page,/design-system)

page-dashboard:
	$(call open_frontend_page,/dashboard)

page-vaults:
	$(call open_frontend_page,/vaults)

page-vault-new:
	$(call open_frontend_page,/vaults/new)

page-vault:
	$(call open_frontend_page,/vaults/$(VAULT_ID))

page-vault-edit:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/edit)

page-projects:
	$(call open_frontend_page,/projects)

page-vault-projects:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects)

page-project-new:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/new)

page-project:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID))

page-project-edit:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/edit)

page-secrets:
	$(call open_frontend_page,/secrets)

page-project-secrets:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets)

page-secret-new:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/new)

page-secret:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID))

page-secret-edit:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/edit)

page-secret-versions:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions)

page-secret-version:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions/$(VERSION_ID))

page-secret-rotate:
	$(call open_frontend_page,/vaults/$(VAULT_ID)/projects/$(PROJECT_ID)/secrets/$(SECRET_ID)/versions/rotate)

page-api-keys:
	$(call open_frontend_page,/api-keys)

page-api-key-new:
	$(call open_frontend_page,/api-keys/new)

page-api-key:
	$(call open_frontend_page,/api-keys/$(API_KEY_ID))

page-audit:
	$(call open_frontend_page,/audit)

page-audit-event:
	$(call open_frontend_page,/audit/$(AUDIT_EVENT_ID))

page-rbac:
	$(call open_frontend_page,/rbac)

page-rbac-roles:
	$(call open_frontend_page,/rbac/roles)

page-rbac-role-new:
	$(call open_frontend_page,/rbac/roles/new)

page-rbac-role:
	$(call open_frontend_page,/rbac/roles/$(ROLE_ID))

page-rbac-role-edit:
	$(call open_frontend_page,/rbac/roles/$(ROLE_ID)/edit)

page-rbac-user:
	$(call open_frontend_page,/rbac/users/$(USER_ID))

page-profile:
	$(call open_frontend_page,/profile)

page-settings:
	$(call open_frontend_page,/settings)

page-settings-security:
	$(call open_frontend_page,/settings/security)

page-settings-preferences:
	$(call open_frontend_page,/settings/preferences)

page-settings-notifications:
	$(call open_frontend_page,/settings/notifications)
