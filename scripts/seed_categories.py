#!/usr/bin/env python3
"""
Seed standard category tree in the modern skill system database.

Creates a comprehensive hierarchical category structure for organizing skills.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import asyncpg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost:5432/skill_db")

STANDARD_CATEGORIES: List[Dict[str, Any]] = [
    {
        "name": "Artificial Intelligence",
        "slug": "artificial-intelligence",
        "description": "AI, machine learning models, LLM integration, and intelligent agents",
        "icon": "brain",
        "sort_order": 10,
        "children": [
            {"name": "Large Language Models", "slug": "llm", "description": "LLM integration, prompting, and fine-tuning", "icon": "message-square", "sort_order": 1, "children": []},
            {"name": "Machine Learning", "slug": "machine-learning", "description": "ML models, training, and deployment", "icon": "cpu", "sort_order": 2, "children": []},
            {"name": "Natural Language Processing", "slug": "nlp", "description": "Text processing, sentiment analysis, translation", "icon": "type", "sort_order": 3, "children": []},
            {"name": "Computer Vision", "slug": "computer-vision", "description": "Image/video recognition, object detection", "icon": "eye", "sort_order": 4, "children": []},
        ],
    },
    {
        "name": "Backend Development",
        "slug": "backend-development",
        "description": "Server-side programming, APIs, databases, and infrastructure",
        "icon": "server",
        "sort_order": 20,
        "children": [
            {"name": "API Development", "slug": "api-development", "description": "REST, GraphQL, gRPC APIs", "icon": "webhook", "sort_order": 1, "children": []},
            {"name": "Databases", "slug": "databases", "description": "SQL, NoSQL, and data modeling", "icon": "database", "sort_order": 2, "children": []},
            {"name": "Microservices", "slug": "microservices", "description": "Distributed systems and service architecture", "icon": "git-branch", "sort_order": 3, "children": []},
            {"name": "Message Queues", "slug": "message-queues", "description": "Kafka, RabbitMQ, and async messaging", "icon": "send", "sort_order": 4, "children": []},
        ],
    },
    {
        "name": "Frontend Development",
        "slug": "frontend-development",
        "description": "Client-side web development, UI frameworks, and design systems",
        "icon": "palette",
        "sort_order": 30,
        "children": [
            {"name": "React Ecosystem", "slug": "react", "description": "React, Next.js, and related tools", "icon": "component", "sort_order": 1, "children": []},
            {"name": "Vue Ecosystem", "slug": "vue", "description": "Vue.js, Nuxt, and related tools", "icon": "layers", "sort_order": 2, "children": []},
            {"name": "CSS & Design", "slug": "css-design", "description": "CSS frameworks, Tailwind, and design systems", "icon": "paintbrush", "sort_order": 3, "children": []},
            {"name": "Web Performance", "slug": "web-performance", "description": "Optimization, Core Web Vitals, and speed", "icon": "gauge", "sort_order": 4, "children": []},
        ],
    },
    {
        "name": "DevOps & Infrastructure",
        "slug": "devops",
        "description": "CI/CD, containerization, cloud services, and infrastructure as code",
        "icon": "cloud",
        "sort_order": 40,
        "children": [
            {"name": "Docker & Containers", "slug": "containers", "description": "Docker, Podman, container orchestration", "icon": "box", "sort_order": 1, "children": []},
            {"name": "Kubernetes", "slug": "kubernetes", "description": "K8s deployment, scaling, and management", "icon": "ship", "sort_order": 2, "children": []},
            {"name": "CI/CD", "slug": "ci-cd", "description": "GitHub Actions, Jenkins, and deployment pipelines", "icon": "play-circle", "sort_order": 3, "children": []},
            {"name": "Infrastructure as Code", "slug": "iac", "description": "Terraform, Pulumi, and CloudFormation", "icon": "file-code", "sort_order": 4, "children": []},
        ],
    },
    {
        "name": "Cloud Computing",
        "slug": "cloud-computing",
        "description": "AWS, Azure, GCP, and other cloud platforms",
        "icon": "cloud-lightning",
        "sort_order": 50,
        "children": [
            {"name": "AWS", "slug": "aws", "description": "Amazon Web Services", "icon": "cloud", "sort_order": 1, "children": []},
            {"name": "Azure", "slug": "azure", "description": "Microsoft Azure cloud services", "icon": "cloud", "sort_order": 2, "children": []},
            {"name": "GCP", "slug": "gcp", "description": "Google Cloud Platform", "icon": "cloud", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Mobile Development",
        "slug": "mobile-development",
        "description": "iOS, Android, React Native, and Flutter development",
        "icon": "smartphone",
        "sort_order": 60,
        "children": [
            {"name": "iOS", "slug": "ios", "description": "Swift, SwiftUI, and iOS ecosystem", "icon": "apple", "sort_order": 1, "children": []},
            {"name": "Android", "slug": "android", "description": "Kotlin, Jetpack Compose, and Android ecosystem", "icon": "android", "sort_order": 2, "children": []},
            {"name": "Cross-Platform", "slug": "cross-platform", "description": "React Native, Flutter, and Xamarin", "icon": "smartphone", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Security",
        "slug": "security",
        "description": "Application security, cryptography, and best practices",
        "icon": "shield",
        "sort_order": 70,
        "children": [
            {"name": "Web Security", "slug": "web-security", "description": "OWASP, XSS, CSRF, and secure coding", "icon": "shield-check", "sort_order": 1, "children": []},
            {"name": "Authentication & Authorization", "slug": "auth", "description": "OAuth, SAML, JWT, and access control", "icon": "key", "sort_order": 2, "children": []},
            {"name": "Cryptography", "slug": "cryptography", "description": "Encryption, hashing, and secure communication", "icon": "lock", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Testing & Quality",
        "slug": "testing-qa",
        "description": "Unit tests, integration tests, E2E testing, and quality assurance",
        "icon": "check-circle",
        "sort_order": 80,
        "children": [
            {"name": "Unit Testing", "slug": "unit-testing", "description": "Individual function and component testing", "icon": "test-tube", "sort_order": 1, "children": []},
            {"name": "Integration Testing", "slug": "integration-testing", "description": "System integration and API testing", "icon": "git-merge", "sort_order": 2, "children": []},
            {"name": "E2E Testing", "slug": "e2e-testing", "description": "End-to-end user flow testing", "icon": "play", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Data Science",
        "slug": "data-science",
        "description": "Data analysis, visualization, and statistical modeling",
        "icon": "bar-chart",
        "sort_order": 90,
        "children": [
            {"name": "Data Analysis", "slug": "data-analysis", "description": "Pandas, NumPy, and data exploration", "icon": "table", "sort_order": 1, "children": []},
            {"name": "Data Visualization", "slug": "data-visualization", "description": "Charts, dashboards, and visual analytics", "icon": "pie-chart", "sort_order": 2, "children": []},
            {"name": "Big Data", "slug": "big-data", "description": "Spark, Hadoop, and large-scale processing", "icon": "database", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Blockchain & Web3",
        "slug": "blockchain",
        "description": "Blockchain development, smart contracts, and decentralized apps",
        "icon": "hexagon",
        "sort_order": 100,
        "children": [
            {"name": "Smart Contracts", "slug": "smart-contracts", "description": "Solidity, Rust, and smart contract development", "icon": "file-code", "sort_order": 1, "children": []},
            {"name": "DeFi", "slug": "defi", "description": "Decentralized finance protocols", "icon": "dollar-sign", "sort_order": 2, "children": []},
        ],
    },
    {
        "name": "Game Development",
        "slug": "game-development",
        "description": "Game engines, 3D graphics, and game design",
        "icon": "gamepad",
        "sort_order": 110,
        "children": [
            {"name": "Unity", "slug": "unity", "description": "Unity Engine development", "icon": "box", "sort_order": 1, "children": []},
            {"name": "Unreal Engine", "slug": "unreal", "description": "Unreal Engine development", "icon": "box", "sort_order": 2, "children": []},
        ],
    },
    {
        "name": "Developer Tools",
        "slug": "developer-tools",
        "description": "CLI tools, IDE extensions, and developer productivity",
        "icon": "wrench",
        "sort_order": 120,
        "children": [
            {"name": "CLI Tools", "slug": "cli-tools", "description": "Command-line utilities and automation", "icon": "terminal", "sort_order": 1, "children": []},
            {"name": "IDE Extensions", "slug": "ide-extensions", "description": "VS Code, IntelliJ, and IDE plugins", "icon": "puzzle", "sort_order": 2, "children": []},
        ],
    },
    {
        "name": "Documentation",
        "slug": "documentation",
        "description": "Technical writing, API documentation, and knowledge management",
        "icon": "book-open",
        "sort_order": 130,
        "children": [],
    },
    {
        "name": "Monitoring & Observability",
        "slug": "monitoring-observability",
        "description": "Logging, metrics, tracing, and system monitoring",
        "icon": "activity",
        "sort_order": 140,
        "children": [
            {"name": "Logging", "slug": "logging", "description": "Log aggregation and management", "icon": "file-text", "sort_order": 1, "children": []},
            {"name": "Metrics", "slug": "metrics", "description": "Prometheus, Grafana, and system metrics", "icon": "bar-chart-2", "sort_order": 2, "children": []},
            {"name": "Tracing", "slug": "tracing", "description": "Distributed tracing and debugging", "icon": "map", "sort_order": 3, "children": []},
        ],
    },
    {
        "name": "Embedded Systems",
        "slug": "embedded-systems",
        "description": "Embedded programming, IoT, and firmware development",
        "icon": "cpu",
        "sort_order": 150,
        "children": [],
    },
]


async def seed_category(conn: asyncpg.Connection, cat: Dict[str, Any], parent_id: Optional[str] = None) -> Optional[str]:
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO categories (name, slug, description, icon, sort_order, parent_id, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, true, $7, $7)
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                icon = EXCLUDED.icon,
                sort_order = EXCLUDED.sort_order,
                parent_id = EXCLUDED.parent_id,
                is_active = true,
                updated_at = $7
            RETURNING id
            """,
            cat["name"],
            cat["slug"],
            cat.get("description"),
            cat.get("icon"),
            cat.get("sort_order", 0),
            parent_id,
            datetime.now(timezone.utc),
        )
        cat_id = str(row["id"]) if row else None

        for child in cat.get("children", []):
            await seed_category(conn, child, cat_id)

        return cat_id
    except Exception as e:
        print(f"  [ERROR] Seeding category {cat['slug']}: {e}")
        return None


async def main() -> None:
    print("=" * 60)
    print("  CATEGORY SEEDING TOOL")
    print("=" * 60)
    print(f"  Database: {DATABASE_URL}")
    print()

    print("  Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    print("  Connected!")

    print(f"\n  Seeding {len(STANDARD_CATEGORIES)} top-level categories...")
    success_count = 0
    error_count = 0

    for cat in STANDARD_CATEGORIES:
        cat_id = await seed_category(conn, cat)
        if cat_id:
            print(f"  + {cat['name']} ({cat['slug']})")
            success_count += 1
        else:
            error_count += 1

    print(f"\n  Seeding complete: {success_count} created, {error_count} errors")

    row = await conn.fetchrow("SELECT COUNT(*) as cnt FROM categories")
    print(f"  Total categories in database: {row['cnt'] if row else 0}")

    await conn.close()
    print("  Done!")


if __name__ == "__main__":
    asyncio.run(main())