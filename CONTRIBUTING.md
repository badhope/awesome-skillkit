# Contributing to AI-SKILL

Thank you for your interest in contributing to AI-SKILL! This document outlines the processes and conventions for contributing to the project.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How to Contribute

### Reporting Bugs

1. Check the [existing issues](https://github.com/badhope/AI-SKILL/issues) to avoid duplicates
2. Use the **Bug Report** template when opening a new issue
3. Include:
   - A clear, descriptive title
   - Steps to reproduce the bug
   - Expected behavior vs actual behavior
   - Environment details (OS, browser, Python version, Node version)
   - Screenshots or error logs if applicable

### Suggesting Enhancements

1. Check existing issues and discussions for similar suggestions
2. Use the **Feature Request** template
3. Describe the feature, its use case, and potential implementation approach
4. Be open to feedback and iteration

### Submitting Pull Requests

1. **Fork** the repository
2. **Create** a branch following our [branch naming conventions](#branch-naming)
3. **Make** your changes, adhering to [code style guidelines](#code-style)
4. **Write/update** tests for your changes
5. **Run** the full test suite and linting
6. **Commit** using [Conventional Commits](#commit-message-conventions)
7. **Push** your branch to your fork
8. **Open** a Pull Request against the `main` branch

---

## Development Workflow

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (recommended)
- Poetry (Python dependency management)

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AI-SKILL.git
cd AI-SKILL

# Start infrastructure services
docker-compose up -d postgres redis qdrant

# Backend setup
cd backend
poetry install
poetry run alembic upgrade head

# Frontend setup
cd ../frontend
npm install
```

### Running in Development

```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=term-missing

# Frontend tests (when available)
cd frontend
npm run lint
npm run typecheck
```

### Code Quality Checks

```bash
# Backend
cd backend
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app/

# Frontend
cd frontend
npm run lint
npm run typecheck
```

---

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `style` | Code style/formatting (no logic change) |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependency updates |
| `ci` | CI/CD configuration changes |
| `build` | Build system changes |

### Scopes

Common scopes: `api`, `frontend`, `sdk`, `search`, `auth`, `db`, `docker`, `docs`, `deps`

### Examples

```
feat(search): add hybrid BM25 + vector search
fix(auth): handle expired JWT tokens gracefully
docs(api): document skills search endpoint
test(search): add integration tests for semantic search
chore(deps): update fastapi to 0.115.0
```

---

## Branch Naming

| Prefix | Purpose |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `refactor/` | Code refactoring |
| `perf/` | Performance improvements |
| `test/` | Test additions/updates |
| `chore/` | Maintenance tasks |

Examples: `feat/semantic-search`, `fix/skill-slug-encoding`, `docs/api-reference`

---

## Code Style

### Python (Backend & SDK)

- Follow [PEP 8](https://peps.python.org/pep-0008/) with a 120-character line limit
- Use type hints for all function signatures
- Format with `ruff format`
- Lint with `ruff check`
- Type-check with `mypy`
- Use `async/await` for all I/O-bound operations
- Use Pydantic models for request/response schemas
- Organize imports: standard library → third-party → local

### TypeScript / React (Frontend & TS SDK)

- Follow the existing Next.js and React patterns in the codebase
- Use functional components with hooks
- Use TypeScript strict mode
- Use `clsx` + `tailwind-merge` for conditional class names
- Use Zod for runtime validation
- Prefer named exports over default exports
- Use `next/link` for internal navigation
- Format with ESLint (`eslint-config-next`)

### General

- Write self-documenting code; use comments sparingly and only for complex logic
- Keep files focused and under ~400 lines when possible
- Follow existing patterns in the codebase
- No emoji in code, commit messages only

---

## Testing Requirements

- **New features** must include unit tests
- **API endpoints** must include integration tests
- **Bug fixes** should include a regression test
- Aim for **80%+ test coverage** on new code
- Backend tests use `pytest` + `pytest-asyncio`
- Frontend tests (when available) use Jest + React Testing Library

---

## Documentation Requirements

- Update relevant documentation when adding or changing features
- API endpoints must have complete docstrings
- New SDK methods must include usage examples
- Significant changes should be noted in `CHANGELOG.md`
- README should reflect the current state of the project

---

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update documentation as needed
3. Add an entry to `CHANGELOG.md` under `[Unreleased]`
4. Your PR must be reviewed and approved by at least one maintainer
5. Squash merge is preferred for a clean history

### PR Title Format

Use the same format as commit messages:

```
feat(search): implement hybrid search with BM25 ranking
```

---

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/badhope/AI-SKILL/discussions)
- **Bugs?** Open an [Issue](https://github.com/badhope/AI-SKILL/issues)
- **Chat?** Join our community Discord (link coming soon)

---

Thank you for contributing to AI-SKILL!