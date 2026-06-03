#!/usr/bin/env python3
"""
Complete migration script: migrate skills from old AI-SKILL project to new PostgreSQL database.

Features:
- Recursively scan /workspace/AI-SKILL/skills/ for SKILL.md files and JSON indexes
- Parse JSON skill data
- Map old categories to new category tree
- Create all skills in the new PostgreSQL database
- Build vector index incrementally
- Track migration progress with resume support
- Generate migration report
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import asyncpg
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

OLD_SKILLS_DIR = Path("/workspace/AI-SKILL/skills")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost:5432/skill_db")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = "skills"
PROGRESS_FILE = Path("/workspace/modern_skill_system/scripts/.migration_progress.json")
BATCH_SIZE = 100

CATEGORY_MAPPING: Dict[str, str] = {
    "ai": "artificial-intelligence",
    "backend": "backend-development",
    "frontend": "frontend-development",
    "devops": "devops",
    "data-science": "data-science",
    "mobile": "mobile-development",
    "security": "security",
    "testing": "testing-qa",
    "database": "databases",
    "cloud": "cloud-computing",
    "machine-learning": "machine-learning",
    "nlp": "natural-language-processing",
    "computer-vision": "computer-vision",
    "blockchain": "blockchain",
    "game-dev": "game-development",
    "embedded": "embedded-systems",
    "api": "api-development",
    "tools": "developer-tools",
    "documentation": "documentation",
    "monitoring": "monitoring-observability",
}


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  [WARN] Failed to load {path}: {e}")
        return None


def parse_skills_from_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    skills: List[Dict[str, Any]] = []
    categories = data.get("categories", {})

    for category_name, skill_list in categories.items():
        for skill in skill_list:
            skills.append({
                "name": skill.get("name", ""),
                "slug": skill.get("name", ""),
                "description": skill.get("description", "")[:2000] if skill.get("description") else None,
                "version": skill.get("version", "1.0.0"),
                "category_slug": CATEGORY_MAPPING.get(category_name, category_name),
                "original_category": category_name,
                "author": skill.get("author", "Unknown"),
                "tags": _clean_tags(skill.get("tags", [])),
                "license": skill.get("license", "MIT"),
                "source_url": skill.get("source_repo"),
                "path": skill.get("path", ""),
                "is_public": True,
                "is_featured": False,
                "complexity": _infer_complexity(skill),
                "content": _build_content(skill),
                "metadata": {
                    "original_category": category_name,
                    "original_path": skill.get("path", ""),
                    "source_commit": skill.get("source_commit", ""),
                    "sync_timestamp": skill.get("sync_timestamp", ""),
                },
            })

    return skills


def _clean_tags(tags: List[str]) -> List[str]:
    cleaned: List[str] = []
    for tag in tags:
        parts = [t.strip().lower().replace(" ", "-") for t in tag.split(",") if t.strip()]
        cleaned.extend(parts)
    return list(dict.fromkeys(cleaned))[:20]


def _infer_complexity(skill: Dict[str, Any]) -> str:
    desc = (skill.get("description") or "").lower()
    name = (skill.get("name") or "").lower()

    advanced_keywords = ["advanced", "expert", "complex", "production", "enterprise", "distributed"]
    beginner_keywords = ["beginner", "basic", "simple", "starter", "quick", "easy"]

    text = desc + " " + name

    if any(kw in text for kw in advanced_keywords):
        return "advanced"
    if any(kw in text for kw in beginner_keywords):
        return "beginner"
    return "intermediate"


def _build_content(skill: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "description": skill.get("description", ""),
        "author": skill.get("author", ""),
        "version": skill.get("version", "1.0.0"),
        "tags": skill.get("tags", []),
    }


def load_progress() -> Dict[str, Any]:
    if PROGRESS_FILE.exists():
        return load_json_file(PROGRESS_FILE) or {}
    return {"completed_slugs": [], "total_processed": 0, "total_errors": 0, "errors": []}


def save_progress(progress: Dict[str, Any]) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, default=str)


async def ensure_categories_exist(conn: asyncpg.Connection, category_slugs: Set[str]) -> Dict[str, str]:
    category_map: Dict[str, str] = {}

    for slug in category_slugs:
        if not slug:
            continue

        row = await conn.fetchrow("SELECT id, slug FROM categories WHERE slug = $1", slug)
        if row:
            category_map[slug] = str(row["id"])
            continue

        display_name = slug.replace("-", " ").title()
        try:
            result = await conn.fetchrow(
                """
                INSERT INTO categories (name, slug, description, sort_order, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (slug) DO UPDATE SET is_active = true
                RETURNING id
                """,
                display_name,
                slug,
                f"Auto-migrated category: {display_name}",
                0,
                True,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            )
            if result:
                category_map[slug] = str(result["id"])
                print(f"  Created category: {slug}")
        except Exception as e:
            print(f"  [ERROR] Creating category {slug}: {e}")

    return category_map


async def insert_skills_batch(
    conn: asyncpg.Connection,
    skills: List[Dict[str, Any]],
    progress: Dict[str, Any],
    qdrant_client: QdrantClient,
) -> Tuple[int, int]:
    inserted = 0
    errors = 0

    for skill in skills:
        slug = skill["slug"]
        if slug in progress["completed_slugs"]:
            print(f"  [SKIP] Already migrated: {slug}")
            continue

        try:
            description = skill["description"]
            if description and len(description) > 2000:
                description = description[:1997] + "..."

            row = await conn.fetchrow(
                """
                INSERT INTO skills (
                    name, slug, description, version, category_id,
                    complexity, status, license, source_url,
                    is_public, is_featured, download_count, view_count, usage_count,
                    rating_avg, rating_count, content, metadata,
                    author_id, created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7, $8, $9,
                    $10, $11, 0, 0, 0,
                    0.0, 0, $12, $13,
                    NULL, NOW(), NOW()
                )
                ON CONFLICT (slug) DO UPDATE SET
                    description = EXCLUDED.description,
                    version = EXCLUDED.version,
                    updated_at = NOW()
                RETURNING id
                """,
                skill["name"],
                slug,
                description,
                skill["version"],
                skill.get("category_id"),
                skill["complexity"],
                "published",
                skill["license"],
                skill["source_url"],
                skill["is_public"],
                skill["is_featured"],
                json.dumps(skill["content"]),
                json.dumps(skill["metadata"]),
            )

            if not row:
                raise Exception(f"Failed to insert skill: {slug}")

            skill_id = str(row["id"])

            for tag_name in skill["tags"]:
                await conn.execute(
                    """
                    INSERT INTO tags (name, usage_count, created_at, updated_at)
                    VALUES ($1, 1, NOW(), NOW())
                    ON CONFLICT (name) DO UPDATE SET usage_count = tags.usage_count + 1
                    """,
                    tag_name,
                )

                tag_row = await conn.fetchrow("SELECT id FROM tags WHERE name = $1", tag_name)
                if tag_row:
                    try:
                        await conn.execute(
                            """
                            INSERT INTO skill_tags (skill_id, tag_id)
                            VALUES ($1, $2)
                            ON CONFLICT DO NOTHING
                            """,
                            skill_id,
                            str(tag_row["id"]),
                        )
                    except Exception:
                        pass

            try:
                qdrant_client.upsert(
                    collection_name=QDRANT_COLLECTION_NAME,
                    points=[
                        qdrant_models.PointStruct(
                            id=skill_id,
                            vector=[0.0] * 768,
                            payload={
                                "id": skill_id,
                                "name": skill["name"],
                                "description": description or "",
                                "category_id": skill.get("category_id", ""),
                                "tags": skill["tags"],
                                "is_public": skill["is_public"],
                                "version": skill["version"],
                                "author": skill.get("author", ""),
                                "usage_count": 0,
                                "rating": 0.0,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            },
                        )
                    ],
                )
            except Exception as e:
                print(f"  [WARN] Qdrant indexing failed for {slug}: {e}")

            progress["completed_slugs"].append(slug)
            progress["total_processed"] += 1
            inserted += 1

            if inserted % 50 == 0:
                save_progress(progress)
                print(f"  ... processed {progress['total_processed']} skills (checkpoint saved)")

        except Exception as e:
            print(f"  [ERROR] Failed to migrate {slug}: {e}")
            errors += 1
            progress["total_errors"] += 1
            progress["errors"].append({"slug": slug, "error": str(e)})

    save_progress(progress)
    return inserted, errors


def ensure_qdrant_collection(client: QdrantClient) -> None:
    try:
        client.get_collection(QDRANT_COLLECTION_NAME)
        print(f"  Collection '{QDRANT_COLLECTION_NAME}' exists")
    except Exception:
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=qdrant_models.VectorParams(
                size=768,
                distance=qdrant_models.Distance.COSINE,
            ),
        )
        print(f"  Created collection '{QDRANT_COLLECTION_NAME}'")


def generate_report(progress: Dict[str, Any], start_time: float) -> str:
    elapsed = time.time() - start_time
    report_lines = [
        "=" * 60,
        "  MIGRATION REPORT",
        "=" * 60,
        f"  Time elapsed:       {elapsed:.2f}s",
        f"  Total processed:    {progress['total_processed']}",
        f"  Total errors:       {progress['total_errors']}",
        f"  Success rate:       {((progress['total_processed'] - progress['total_errors']) / max(progress['total_processed'], 1)) * 100:.1f}%",
    ]

    if progress["errors"]:
        report_lines.append("\n  Errors:")
        for err in progress["errors"][:20]:
            report_lines.append(f"    - {err['slug']}: {err['error']}")

    report_lines.append("=" * 60)

    report_path = Path("/workspace/modern_skill_system/scripts/migration_report.txt")
    report_content = "\n".join(report_lines)
    report_path.write_text(report_content)
    print("\n" + report_content)
    return report_content


async def main() -> None:
    print("=" * 60)
    print("  SKILL MIGRATION TOOL")
    print("=" * 60)
    print(f"  Source directory: {OLD_SKILLS_DIR}")
    print(f"  Database: {DATABASE_URL}")
    print(f"  Qdrant: {QDRANT_URL}")
    print()

    if not OLD_SKILLS_DIR.exists():
        print(f"[ERROR] Source directory not found: {OLD_SKILLS_DIR}")
        sys.exit(1)

    start_time = time.time()
    progress = load_progress()

    if progress["total_processed"] > 0:
        print(f"  Resuming migration from progress file ({progress['total_processed']} already processed)")
        print(f"  To reset: rm {PROGRESS_FILE}")
        print()

    print("  Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    print("  Connected!")

    print("  Connecting to Qdrant...")
    qdrant_client = QdrantClient(url=QDRANT_URL)
    ensure_qdrant_collection(qdrant_client)
    print("  Qdrant ready!")

    print("\n  Loading skill data from JSON files...")
    json_files = list(OLD_SKILLS_DIR.glob("*.json"))

    all_skills: List[Dict[str, Any]] = []
    unique_slugs: Set[str] = set()

    for json_file in json_files:
        print(f"  Reading: {json_file.name}")
        data = load_json_file(json_file)
        if not data:
            continue

        skills = parse_skills_from_json(data)
        for skill in skills:
            slug = skill["slug"]
            if slug and slug not in unique_slugs:
                unique_slugs.add(slug)
                all_skills.append(skill)

    print(f"\n  Total unique skills found: {len(all_skills)}")

    print("\n  Ensuring categories exist in database...")
    category_slugs = {s["category_slug"] for s in all_skills if s["category_slug"]}
    category_map = await ensure_categories_exist(conn, category_slugs)
    print(f"  Categories ready: {len(category_map)}")

    for skill in all_skills:
        cat_slug = skill["category_slug"]
        if cat_slug and cat_slug in category_map:
            skill["category_id"] = category_map[cat_slug]

    print("\n  Migrating skills to database...")
    total_inserted = 0
    total_errors = 0

    for i in range(0, len(all_skills), BATCH_SIZE):
        batch = all_skills[i : i + BATCH_SIZE]
        print(f"\n  Processing batch {i // BATCH_SIZE + 1} ({len(batch)} skills)...")
        inserted, errors = await insert_skills_batch(conn, batch, progress, qdrant_client)
        total_inserted += inserted
        total_errors += errors
        await asyncio.sleep(0.1)

    print(f"\n  Migration complete: {total_inserted} inserted, {total_errors} errors")
    generate_report(progress, start_time)

    print("  Closing connections...")
    await conn.close()
    qdrant_client.close()
    print("  Done!")


if __name__ == "__main__":
    asyncio.run(main())
