# ──────────────────────────────────────────────────────────────────────────────
# AI-SKILL — top-level Makefile
#
# Every common workflow has a target. `make help` lists them all.
# `make first-run` is the single command a new contributor needs.
# ──────────────────────────────────────────────────────────────────────────────

# ---- Configuration ------------------------------------------------------------
SHELL       := /usr/bin/env bash
.DEFAULT    := help
.PHONY      := help
PYTHON      ?= python3
PIP         ?= $(PYTHON) -m pip
POETRY      ?= $(PYTHON) -m poetry
NPM         ?= npm
COMPOSE     ?= docker compose
DOCKER      ?= docker
BACKEND_DIR := backend
FRONTEND_DIR:= frontend
SDK_PY_DIR  := sdk/python
SDK_TS_DIR  := sdk/typescript

# ---- Help --------------------------------------------------------------------
help:  ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_.-]+:.*?## / {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Useful one-liners:"
	@echo "  make first-run          # Bootstrap everything from scratch"
	@echo "  make dev                # Bring up the full stack in Docker"
	@echo "  make test               # Run all tests (backend + frontend + SDKs)"

# ---- First-time setup ---------------------------------------------------------
.PHONY: first-run install pre-commit
first-run: install pre-commit generate-secrets  ## One-shot bootstrap for new contributors
	@echo ""
	@echo "✓ First-run complete. Next steps:"
	@echo "    1. Edit .env  (database, JWT, admin password)"
	@echo "    2. make dev    (start the stack)"
	@echo "    3. make test   (run the test suite)"

install:  ## Install all dependencies (backend + frontend + SDKs)
	$(MAKE) install-backend
	$(MAKE) install-frontend
	$(MAKE) install-sdk-python
	$(MAKE) install-sdk-typescript

install-backend:  ## Install backend Python deps via Poetry
	cd $(BACKEND_DIR) && $(POETRY) install --no-interaction

install-frontend:  ## Install frontend Node deps via npm
	cd $(FRONTEND_DIR) && $(NPM) install

install-sdk-python:  ## Install Python SDK deps in editable mode
	cd $(SDK_PY_DIR) && $(PIP) install -e .[dev]

install-sdk-typescript:  ## Install TypeScript SDK deps
	cd $(SDK_TS_DIR) && $(NPM) install

pre-commit:  ## Install pre-commit hooks into .git/hooks
	$(PIP) install pre-commit
	pre-commit install

generate-secrets:  ## Generate strong JWT + admin + DB passwords and write to .env
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "JWT_SECRET_KEY=\"$$(openssl rand -hex 32)\"" >> .env
	@echo "ADMIN_PASSWORD=\"$$(openssl rand -base64 18)\"" >> .env
	@echo "POSTGRES_PASSWORD=\"$$(openssl rand -base64 18)\"" >> .env
	@echo "✓ Secrets appended to .env"

# ---- Run the stack -----------------------------------------------------------
.PHONY: dev dev-detached down logs restart
dev:  ## Start the full stack (build + foreground)
	$(COMPOSE) up --build

dev-detached:  ## Start the full stack in the background
	$(COMPOSE) up --build -d
	@echo "✓ Stack started. Tail logs with 'make logs'."

down:  ## Stop the stack
	$(COMPOSE) down

logs:  ## Tail logs from all services
	$(COMPOSE) logs -f --tail=200

restart:  ## Restart all services
	$(COMPOSE) restart

# ---- Database migrations ------------------------------------------------------
.PHONY: db-upgrade db-downgrade db-revision db-reset
db-upgrade:  ## Apply all pending Alembic migrations
	cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head

db-downgrade:  ## Roll back the last migration
	cd $(BACKEND_DIR) && $(POETRY) run alembic downgrade -1

db-revision:  ## Create a new Alembic migration (msg="<message>")
	cd $(BACKEND_DIR) && $(POETRY) run alembic revision --autogenerate -m "$(msg)"

db-reset:  ## Drop and recreate the local database (DESTRUCTIVE)
	$(COMPOSE) down -v
	$(COMPOSE) up -d postgres
	@sleep 5
	$(MAKE) db-upgrade

# ---- Tests -------------------------------------------------------------------
.PHONY: test test-backend test-frontend test-sdk test-coverage
test: test-backend test-frontend test-sdk  ## Run the full test suite

test-backend:  ## Run backend pytest
	cd $(BACKEND_DIR) && $(POETRY) run pytest --cov=app --cov-report=term-missing

test-frontend:  ## Run frontend vitest/jest
	cd $(FRONTEND_DIR) && $(NPM) test -- --coverage

test-sdk: test-sdk-python test-sdk-typescript  ## Run both SDK test suites

test-sdk-python:  ## Run Python SDK tests
	cd $(SDK_PY_DIR) && $(PYTHON) -m pytest skill_sdk/

test-sdk-typescript:  ## Run TypeScript SDK tests
	cd $(SDK_TS_DIR) && $(NPM) test

test-coverage:  ## Generate combined coverage report
	$(MAKE) test-backend COV=1
	$(MAKE) test-frontend COV=1
	@echo "✓ Coverage reports: backend/coverage/, frontend/coverage/"

# ---- Linting & type checks ---------------------------------------------------
.PHONY: lint format typecheck
lint: lint-backend lint-frontend lint-sdk  ## Run all linters

lint-backend:  ## ruff + mypy on the backend
	cd $(BACKEND_DIR) && $(POETRY) run ruff check app/ tests/
	cd $(BACKEND_DIR) && $(POETRY) run mypy app/ --ignore-missing-imports

lint-frontend:  ## eslint on the frontend
	cd $(FRONTEND_DIR) && $(NPM) run lint

lint-sdk: lint-sdk-python lint-sdk-typescript  ## Lint both SDKs

lint-sdk-python:  ## ruff + mypy on the Python SDK
	cd $(SDK_PY_DIR) && $(POETRY) run ruff check skill_sdk/
	cd $(SDK_PY_DIR) && $(POETRY) run mypy skill_sdk/ --ignore-missing-imports

lint-sdk-typescript:  ## tsc on the TypeScript SDK
	cd $(SDK_TS_DIR) && $(NPM) run typecheck

format:  ## Auto-format everything
	cd $(BACKEND_DIR) && $(POETRY) run ruff format app/ tests/
	cd $(SDK_PY_DIR)  && $(POETRY) run ruff format skill_sdk/
	cd $(FRONTEND_DIR)&& $(NPM) run format
	cd $(SDK_TS_DIR)  && $(NPM) run format

typecheck:  ## Strict type-check the entire monorepo
	cd $(BACKEND_DIR) && $(POETRY) run mypy app/ --ignore-missing-imports
	cd $(FRONTEND_DIR)&& $(NPM) run typecheck
	cd $(SDK_PY_DIR)  && $(POETRY) run mypy skill_sdk/ --ignore-missing-imports
	cd $(SDK_TS_DIR)  && $(NPM) run typecheck

# ---- Admin / DB helpers -------------------------------------------------------
.PHONY: create-admin seed health-check
create-admin:  ## Interactively create the first superuser
	cd $(BACKEND_DIR) && $(POETRY) run python -m app.scripts.create_admin

seed:  ## Seed categories + tags (idempotent)
	cd $(BACKEND_DIR) && $(POETRY) run python -m app.core.seed

health-check:  ## Probe the running backend
	cd $(BACKEND_DIR) && $(POETRY) run python $(CURDIR)/scripts/health_check.py

i18n-compile:  ## Compile all .po catalogs into .mo files (server-side i18n)
	cd $(BACKEND_DIR) && $(PYTHON) -m app.core.i18n compile

i18n-check: i18n-compile  ## Recompile and verify every key is present in every locale
	cd $(BACKEND_DIR) && $(PYTHON) -m app.core.i18n check

# ---- Build & publish ---------------------------------------------------------
.PHONY: build build-backend build-frontend publish
build: build-backend build-frontend  ## Build both Docker images

build-backend:
	$(DOCKER) build -t ai-skill/backend:latest $(BACKEND_DIR)

build-frontend:
	$(DOCKER) build -t ai-skill/frontend:latest $(FRONTEND_DIR)

# ---- Cleanup ------------------------------------------------------------------
.PHONY: clean clean-pyc clean-build clean-docker clean-all
clean: clean-pyc clean-build  ## Remove Python and Node build artifacts

clean-pyc:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

clean-build:
	rm -rf $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.mypy_cache $(BACKEND_DIR)/.ruff_cache
	rm -rf $(BACKEND_DIR)/htmlcov $(BACKEND_DIR)/coverage.xml
	rm -rf $(FRONTEND_DIR)/.next $(FRONTEND_DIR)/coverage
	rm -rf $(SDK_TS_DIR)/dist $(SDK_TS_DIR)/node_modules/.cache

clean-docker:  ## Remove all AI-SKILL Docker resources (volumes preserved)
	$(DOCKER) rm -f $$(docker ps -a -q --filter "name=skill-") 2>/dev/null || true
	$(DOCKER) image rm -f ai-skill/backend:latest ai-skill/frontend:latest 2>/dev/null || true

clean-all: clean clean-docker  ## Nuke everything (build artifacts + Docker)
	$(COMPOSE) down -v

# ---- Security -----------------------------------------------------------------
.PHONY: security-scan secrets-scan
security-scan:  ## Run pip-audit + npm audit
	cd $(BACKEND_DIR) && $(POETRY) run pip-audit || true
	cd $(FRONTEND_DIR) && $(NPM) audit --audit-level=high || true
	cd $(SDK_TS_DIR)  && $(NPM) audit --audit-level=high || true

secrets-scan:  ## Grep the source tree for likely secrets
	@echo "Scanning for hardcoded credentials…"
	@! grep -rEn 'admin123|Admin1234|change-this-in-production|your-super-secret-key|skill_pass' \
		backend/app/ backend/alembic/ docker-compose.yml 2>/dev/null
	@echo "✓ No hardcoded credentials found."
