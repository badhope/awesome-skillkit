# AI-SKILL

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  <img src="https://img.shields.io/github/stars/badhope/AI-SKILL?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/github/issues-pr/badhope/AI-SKILL" alt="Pull Requests">
  <img src="https://img.shields.io/github/actions/workflow/status/badhope/AI-SKILL/ci.yml?branch=main" alt="Build Status">
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/skills-9400%2B-orange" alt="Skills Count">
  <img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python">
  <img src="https://img.shields.io/badge/typescript-5.9+-3178C6" alt="TypeScript">
</p>

<p align="center">
  <strong>The largest universal agent skill library</strong> — 9,400+ production-ready skills across 50+ categories, supporting 13+ platforms.
</p>

---

## ✨ Features

- 🔍 **Semantic Search** — Powered by Qdrant vector database with Sentence-BERT embeddings for intelligent, context-aware skill discovery
- 📱 **Mobile-First Responsive Design** — Optimized Progressive Web App experience across desktop, tablet, and mobile devices
- 🌐 **English/Chinese i18n** — Full internationalization support with runtime locale switching
- 🧠 **Vector Search** — Hybrid BM25 + dense vector search for maximum recall and precision
- 🔄 **Version Control** — Semantic versioning with complete skill change history and rollback support
- 🔗 **Dependency Management** — Declare skill dependencies with version constraints and cycle detection
- ⭐ **Quality Assessment** — User ratings, usage analytics, and automated quality scoring
- 📊 **Analytics Dashboard** — Real-time usage statistics, popularity trends, and engagement metrics
- 🔌 **REST API** — Fully documented FastAPI backend with auto-generated OpenAPI schema
- 📦 **Python & TypeScript SDKs** — First-class client libraries for seamless integration
- 🛡️ **Security** — JWT authentication, RBAC authorization, rate limiting, and audit logging
- 🐳 **Docker Support** — One-command deployment with Docker Compose

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL
cp .env.example .env
docker-compose up -d
```

Then open **http://localhost:3000** in your browser.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| API Documentation (ReDoc) | http://localhost:8000/redoc |

### Manual Setup

#### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Qdrant (optional, defaults to local)

#### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your database credentials

pip install poetry
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open **http://localhost:3000**.

---

## 📚 Documentation

| Resource | Link |
|----------|------|
| API Reference | http://localhost:8000/docs |
| Python SDK Docs | [sdk/python/README.md](sdk/python/README.md) |
| TypeScript SDK Docs | [sdk/typescript/](sdk/typescript/) |
| Contributing Guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security Policy | [SECURITY.md](SECURITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

---

## 🏗️ Architecture

```
                         ┌──────────────────────────┐
                         │       Client Layer        │
                         │   Browser  │  Mobile App  │
                         │   Python SDK │   TS SDK   │
                         └────────────┬─────────────┘
                                      │ HTTP/REST
                         ┌────────────▼─────────────┐
                         │    Nginx / Load Balancer  │
                         └────────────┬─────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────▼─────────┐   ┌────────▼────────┐   ┌──────────▼──────────┐
    │    Frontend        │   │    Backend       │   │    Vector Search    │
    │   Next.js 15       │   │   FastAPI 0.115  │   │    Qdrant 1.9+      │
    │   Port 3000        │   │   Port 8000      │   │    Port 6333        │
    └───────────────────┘   └────────┬─────────┘   └─────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
           ┌─────────▼─────┐  ┌──────▼──────┐  ┌─────▼──────┐
           │  PostgreSQL 16 │  │   Redis 7   │  │  Storage   │
           │  Port 5432    │  │  Port 6379  │  │ Local / S3 │
           └───────────────┘  └─────────────┘  └────────────┘
```

---

## 📊 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend Framework | Next.js (App Router) | 15.x |
| Frontend Language | TypeScript | 5.9+ |
| Styling | Tailwind CSS | 3.4+ |
| UI Components | shadcn/ui + Radix UI | Latest |
| Data Fetching | TanStack Query | 5.x |
| Charts | Recharts | 3.x |
| Backend Framework | FastAPI | 0.115+ |
| Backend Language | Python | 3.12+ |
| ORM | SQLAlchemy (async) | 2.0+ |
| Data Validation | Pydantic | 2.9+ |
| Primary Database | PostgreSQL | 16 |
| Vector Database | Qdrant | 1.9+ |
| Cache | Redis | 7 |
| Task Queue | Celery | 5.x |
| Observability | OpenTelemetry + Sentry | Latest |
| Containerization | Docker + Docker Compose | Latest |
| CI/CD | GitHub Actions | Latest |

---

## 🔌 API Overview

### Authentication

```http
POST   /api/v1/auth/register         # Register new user
POST   /api/v1/auth/login            # Login, get JWT tokens
POST   /api/v1/auth/refresh          # Refresh access token
```

### Skills

```http
GET    /api/v1/skills                # List skills (paginated, filterable)
GET    /api/v1/skills/search         # Semantic vector search
GET    /api/v1/skills/featured       # Featured/popular skills
GET    /api/v1/skills/{slug}         # Get skill details
POST   /api/v1/skills                # Create a new skill
PUT    /api/v1/skills/{slug}         # Update a skill
DELETE /api/v1/skills/{slug}         # Delete a skill
```

### Categories

```http
GET    /api/v1/categories            # Category tree
GET    /api/v1/categories/{slug}     # Category with children
```

### Tags

```http
GET    /api/v1/tags                  # List all tags
GET    /api/v1/tags/{name}           # Skills by tag
```

### Analytics

```http
GET    /api/v1/analytics/overview    # Dashboard overview stats
GET    /api/v1/analytics/skills      # Per-skill analytics
GET    /api/v1/analytics/usage       # Usage trends
```

---

## 📦 SDK

### Python SDK

```python
from skill_sdk import SkillClient

client = SkillClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Semantic search
results = client.search_skills(
    query="React performance optimization hooks",
    limit=10,
    category="frontend/react"
)

# Get skill detail
skill = client.get_skill("react-use-memo-guide")

# List skills with filters
skills = client.list_skills(
    category="ai/llms",
    tags=["prompt-engineering"],
    page=1,
    size=20
)
```

Install via pip:

```bash
pip install skill-sdk
```

### TypeScript SDK

```typescript
import { SkillClient } from '@ai-skill/sdk';

const client = new SkillClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key',
});

// Semantic search
const results = await client.searchSkills({
  query: 'React performance optimization hooks',
  limit: 10,
  category: 'frontend/react',
});

// Get skill detail
const skill = await client.getSkill('react-use-memo-guide');

// List skills
const { items, total } = await client.listSkills({
  category: 'ai/llms',
  tags: ['prompt-engineering'],
  page: 1,
  size: 20,
});
```

Install via npm:

```bash
npm install @ai-skill/sdk
```

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

- Fork the repository
- Create a feature branch (`feat/amazing-feature`)
- Write tests and ensure they pass
- Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed workflow, commit conventions, and code style guidelines.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=badhope/AI-SKILL&type=Date)](https://star-history.com/#badhope/AI-SKILL&Date)

---

<p align="center">
  Built with ❤️ by the AI-SKILL community
</p>