"""initial migration

Revision ID: 0001
Revises:
Create Date: 2026-06-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import column, table

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


USERS_TABLE = "users"
CATEGORIES_TABLE = "categories"
TAGS_TABLE = "tags"
SKILLS_TABLE = "skills"
SKILL_TAG_ASSOCIATION_TABLE = "skill_tag_association"
SKILL_VERSIONS_TABLE = "skill_versions"
SKILL_DEPENDENCIES_TABLE = "skill_dependencies"
SKILL_RATINGS_TABLE = "skill_ratings"
SKILL_USAGE_LOGS_TABLE = "skill_usage_logs"
SKILL_COMPOSITIONS_TABLE = "skill_compositions"
SKILL_COMPOSITION_ITEMS_TABLE = "skill_composition_items"


SEED_CATEGORIES = [
    {"slug": "frontend", "name": "Frontend", "description": "前端开发相关技能，包括 UI 组件、状态管理、构建工具等", "icon": "layout", "sort_order": 1},
    {"slug": "backend", "name": "Backend", "description": "后端开发相关技能，包括 API 开发、数据库设计、微服务架构等", "icon": "server", "sort_order": 2},
    {"slug": "ai", "name": "AI", "description": "人工智能与机器学习相关技能，包括模型训练、推理优化、LLM 应用等", "icon": "cpu", "sort_order": 3},
    {"slug": "devops", "name": "DevOps", "description": "开发运维相关技能，包括 CI/CD、容器化、基础设施即代码等", "icon": "settings", "sort_order": 4},
    {"slug": "database", "name": "Database", "description": "数据库相关技能，包括 SQL 优化、NoSQL 设计、数据迁移等", "icon": "database", "sort_order": 5},
    {"slug": "security", "name": "Security", "description": "安全相关技能，包括认证授权、漏洞扫描、安全加固等", "icon": "shield", "sort_order": 6},
    {"slug": "testing", "name": "Testing", "description": "测试相关技能，包括单元测试、集成测试、性能测试等", "icon": "check-circle", "sort_order": 7},
    {"slug": "mobile", "name": "Mobile", "description": "移动端开发相关技能，包括 React Native、Flutter、原生开发等", "icon": "smartphone", "sort_order": 8},
    {"slug": "data-science", "name": "Data Science", "description": "数据科学相关技能，包括数据分析、可视化、特征工程等", "icon": "bar-chart", "sort_order": 9},
    {"slug": "design", "name": "Design", "description": "设计相关技能，包括 UI/UX 设计、设计系统、原型工具等", "icon": "figma", "sort_order": 10},
]

SEED_TAGS = [
    {"name": "react", "color": "#61DAFB", "description": "React 框架相关"},
    {"name": "typescript", "color": "#3178C6", "description": "TypeScript 语言相关"},
    {"name": "python", "color": "#3776AB", "description": "Python 语言相关"},
    {"name": "docker", "color": "#2496ED", "description": "Docker 容器相关"},
    {"name": "kubernetes", "color": "#326CE5", "description": "Kubernetes 编排相关"},
    {"name": "llm", "color": "#FF6F00", "description": "大语言模型相关"},
    {"name": "fastapi", "color": "#009688", "description": "FastAPI 框架相关"},
    {"name": "postgresql", "color": "#4169E1", "description": "PostgreSQL 数据库相关"},
    {"name": "redis", "color": "#DC382D", "description": "Redis 缓存相关"},
    {"name": "aws", "color": "#FF9900", "description": "AWS 云服务相关"},
    {"name": "nextjs", "color": "#000000", "description": "Next.js 框架相关"},
    {"name": "mongodb", "color": "#47A248", "description": "MongoDB 数据库相关"},
    {"name": "graphql", "color": "#E10098", "description": "GraphQL 查询语言相关"},
    {"name": "go", "color": "#00ADD8", "description": "Go 语言相关"},
    {"name": "rust", "color": "#000000", "description": "Rust 语言相关"},
    {"name": "terraform", "color": "#7B42BC", "description": "Terraform IaC 相关"},
    {"name": "ci-cd", "color": "#FC6D26", "description": "CI/CD 流水线相关"},
    {"name": "vue", "color": "#4FC08D", "description": "Vue.js 框架相关"},
    {"name": "nodejs", "color": "#339933", "description": "Node.js 运行时相关"},
    {"name": "ai", "color": "#6366F1", "description": "人工智能相关"},
]

SEED_SKILLS = [
    {
        "slug": "react-component-dev",
        "name": "React Component Development",
        "description": "A comprehensive skill for developing reusable React components with TypeScript, covering hooks, state management, testing, and Storybook integration.",
        "version": "2.1.0",
        "complexity": "intermediate",
        "license": "MIT",
        "is_featured": True,
        "content": {"prompt_template": "Develop a reusable React component...", "examples": [], "best_practices": ["Use functional components", "Implement proper prop types"]},
        "metadata": {"source": "internal", "compatibility": ["react-18", "react-19"]},
        "tags": ["react", "typescript", "nextjs"],
    },
    {
        "slug": "python-api-builder",
        "name": "Python API Builder",
        "description": "Build production-ready REST APIs using FastAPI with automatic OpenAPI documentation, async database operations, and comprehensive error handling.",
        "version": "1.5.2",
        "complexity": "intermediate",
        "license": "Apache-2.0",
        "is_featured": True,
        "content": {"prompt_template": "Create a FastAPI endpoint for...", "examples": [], "best_practices": ["Use Pydantic models", "Implement dependency injection"]},
        "metadata": {"source": "internal", "compatibility": ["fastapi-0.115", "python-3.12"]},
        "tags": ["python", "fastapi", "postgresql", "redis"],
    },
    {
        "slug": "docker-deployment",
        "name": "Docker Deployment",
        "description": "Automate containerized deployments with Docker and Docker Compose, including multi-stage builds, health checks, and production best practices.",
        "version": "3.0.0",
        "complexity": "beginner",
        "license": "MIT",
        "is_featured": True,
        "content": {"prompt_template": "Create a Dockerfile for...", "examples": [], "best_practices": ["Use multi-stage builds", "Run as non-root user"]},
        "metadata": {"source": "internal", "compatibility": ["docker-24", "docker-25"]},
        "tags": ["docker", "kubernetes", "aws", "ci-cd"],
    },
]

# NOTE: admin user bootstrap is intentionally NOT included in this migration.
# Migrations are immutable and shipping a default admin password would be a
# security regression on every fresh database. Create the first admin with:
#   ADMIN_PASSWORD=<strong> ADMIN_EMAIL=... python -m app.scripts.create_admin
# or rely on the application-level seed in app.core.seed which honors the
# ADMIN_PASSWORD env var (and refuses to run in production without it).


def upgrade() -> None:
    op.create_table(
        USERS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), unique=True, nullable=False),
        sa.Column("username", sa.String(150), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", USERS_TABLE, ["email"], unique=True)
    op.create_index("ix_users_username", USERS_TABLE, ["username"], unique=True)

    op.create_table(
        CATEGORIES_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_category_slug", CATEGORIES_TABLE, ["slug"])
    op.create_index("idx_category_parent", CATEGORIES_TABLE, ["parent_id"])

    op.create_table(
        TAGS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("usage_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tags_name", TAGS_TABLE, ["name"], unique=True)

    op.create_table(
        SKILLS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(50), nullable=False, server_default=sa.text("'1.0.0'")),
        sa.Column("category_id", UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("complexity", sa.Enum("beginner", "intermediate", "advanced", "expert", name="complexity_enum"), server_default="intermediate"),
        sa.Column("status", sa.Enum("draft", "published", "deprecated", "archived", name="status_enum"), server_default="published"),
        sa.Column("license", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("download_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("view_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("usage_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("rating_avg", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("rating_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("content", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_skill_slug", SKILLS_TABLE, ["slug"])
    op.create_index("idx_skill_category", SKILLS_TABLE, ["category_id"])
    op.create_index("idx_skill_author", SKILLS_TABLE, ["author_id"])
    op.create_index("idx_skill_featured", SKILLS_TABLE, ["is_featured"])
    op.create_index("idx_skill_status", SKILLS_TABLE, ["status"])
    op.create_index("idx_skill_complexity", SKILLS_TABLE, ["complexity"])

    op.create_table(
        SKILL_TAG_ASSOCIATION_TABLE,
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )
    # 故意不创建 `ix_skill_tag_skill_id` / `ix_skill_tag_tag_id`：
    # (skill_id, tag_id) 复合主键本身就为两列各建了一棵 BTree,
    # 再额外加两个单列索引是冗余的, 只会让写放大.

    op.create_table(
        SKILL_VERSIONS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("skill_id", "version", name="uq_skill_version"),
    )
    op.create_index("idx_skill_version_skill", SKILL_VERSIONS_TABLE, ["skill_id"])

    op.create_table(
        SKILL_DEPENDENCIES_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("depends_on_skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_constraint", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("skill_id", "depends_on_skill_id", name="uq_skill_dependency"),
    )
    op.create_index("idx_skill_dependency_skill", SKILL_DEPENDENCIES_TABLE, ["skill_id"])
    op.create_index("idx_skill_dependency_depends_on", SKILL_DEPENDENCIES_TABLE, ["depends_on_skill_id"])

    op.create_table(
        SKILL_RATINGS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("skill_id", "user_id", name="uq_skill_user_rating"),
    )
    op.create_index("idx_skill_rating_skill", SKILL_RATINGS_TABLE, ["skill_id"])
    op.create_index("idx_skill_rating_user", SKILL_RATINGS_TABLE, ["user_id"])

    op.create_table(
        SKILL_USAGE_LOGS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False, server_default=sa.text("'download'")),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_skill_usage_log_skill", SKILL_USAGE_LOGS_TABLE, ["skill_id"])
    op.create_index("idx_skill_usage_log_user", SKILL_USAGE_LOGS_TABLE, ["user_id"])
    op.create_index("idx_skill_usage_log_created", SKILL_USAGE_LOGS_TABLE, ["created_at"])

    op.create_table(
        SKILL_COMPOSITIONS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_skill_composition_owner", SKILL_COMPOSITIONS_TABLE, ["owner_id"])
    op.create_index("idx_skill_composition_slug", SKILL_COMPOSITIONS_TABLE, ["slug"])

    op.create_table(
        SKILL_COMPOSITION_ITEMS_TABLE,
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("composition_id", UUID(as_uuid=True), sa.ForeignKey("skill_compositions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("composition_id", "skill_id", name="uq_composition_skill"),
    )
    op.create_index("idx_comp_item_composition", SKILL_COMPOSITION_ITEMS_TABLE, ["composition_id"])
    op.create_index("idx_comp_item_skill", SKILL_COMPOSITION_ITEMS_TABLE, ["skill_id"])

    _insert_seed_data()


def downgrade() -> None:
    op.drop_table(SKILL_COMPOSITION_ITEMS_TABLE)
    op.drop_table(SKILL_COMPOSITIONS_TABLE)
    op.drop_table(SKILL_USAGE_LOGS_TABLE)
    op.drop_table(SKILL_RATINGS_TABLE)
    op.drop_table(SKILL_DEPENDENCIES_TABLE)
    op.drop_table(SKILL_VERSIONS_TABLE)
    op.drop_table(SKILL_TAG_ASSOCIATION_TABLE)
    op.drop_table(SKILLS_TABLE)
    op.drop_table(TAGS_TABLE)
    op.drop_table(CATEGORIES_TABLE)
    op.drop_table(USERS_TABLE)

    op.execute("DROP TYPE IF EXISTS complexity_enum")
    op.execute("DROP TYPE IF EXISTS status_enum")


def _insert_seed_data() -> None:
    # Admin user seeding has been moved out of the migration to avoid baking a
    # default password into immutable migration history. Categories and tags
    # below are still safe to seed from migrations because they contain no
    # secret material.
    import uuid as _uuid

    category_ids: dict[str, str] = {}
    categories_table = table(
        CATEGORIES_TABLE,
        column("id", UUID(as_uuid=True)),
        column("name", sa.String),
        column("slug", sa.String),
        column("description", sa.Text),
        column("parent_id", UUID(as_uuid=True)),
        column("icon", sa.String),
        column("sort_order", sa.Integer),
        column("is_active", sa.Boolean),
    )
    category_rows = []
    for cat in SEED_CATEGORIES:
        cat_id = str(_uuid.uuid4())
        category_ids[cat["slug"]] = cat_id
        category_rows.append({
            "id": cat_id,
            "name": cat["name"],
            "slug": cat["slug"],
            "description": cat["description"],
            "parent_id": None,
            "icon": cat["icon"],
            "sort_order": cat["sort_order"],
            "is_active": True,
        })
    op.bulk_insert(categories_table, category_rows)

    tag_ids: dict[str, str] = {}
    tags_table = table(
        TAGS_TABLE,
        column("id", UUID(as_uuid=True)),
        column("name", sa.String),
        column("color", sa.String),
        column("description", sa.Text),
        column("usage_count", sa.Integer),
    )
    tag_rows = []
    for tag in SEED_TAGS:
        tag_id = str(_uuid.uuid4())
        tag_ids[tag["name"]] = tag_id
        tag_rows.append({
            "id": tag_id,
            "name": tag["name"],
            "color": tag["color"],
            "description": tag["description"],
            "usage_count": 0,
        })
    op.bulk_insert(tags_table, tag_rows)

    skill_ids: dict[str, str] = {}
    skills_table = table(
        SKILLS_TABLE,
        column("id", UUID(as_uuid=True)),
        column("name", sa.String),
        column("slug", sa.String),
        column("description", sa.Text),
        column("version", sa.String),
        column("category_id", UUID(as_uuid=True)),
        column("author_id", UUID(as_uuid=True)),
        column("complexity", sa.String),
        column("status", sa.String),
        column("license", sa.String),
        column("source_url", sa.String),
        column("is_public", sa.Boolean),
        column("is_featured", sa.Boolean),
        column("download_count", sa.Integer),
        column("view_count", sa.Integer),
        column("usage_count", sa.Integer),
        column("rating_avg", sa.Float),
        column("rating_count", sa.Integer),
        column("content", JSONB),
        column("metadata", JSONB),
    )
    skill_rows = []
    for skill_data in SEED_SKILLS:
        skill_id = str(_uuid.uuid4())
        skill_ids[skill_data["slug"]] = skill_id
        skill_rows.append({
            "id": skill_id,
            "name": skill_data["name"],
            "slug": skill_data["slug"],
            "description": skill_data["description"],
            "version": skill_data["version"],
            "category_id": category_ids.get("frontend" if "react" in skill_data["slug"]
                else "backend" if "python" in skill_data["slug"]
                else "devops"),
            "author_id": None,
            "complexity": skill_data["complexity"],
            "status": "published",
            "license": skill_data["license"],
            "source_url": None,
            "is_public": True,
            "is_featured": skill_data["is_featured"],
            "download_count": 0,
            "view_count": 0,
            "usage_count": 0,
            "rating_avg": 0.0,
            "rating_count": 0,
            "content": skill_data["content"],
            "metadata": skill_data["metadata"],
        })
    op.bulk_insert(skills_table, skill_rows)

    skill_tag_assoc_table = table(
        SKILL_TAG_ASSOCIATION_TABLE,
        column("skill_id", UUID(as_uuid=True)),
        column("tag_id", UUID(as_uuid=True)),
    )
    assoc_rows: list[dict] = []
    for skill_data in SEED_SKILLS:
        skill_id = skill_ids[skill_data["slug"]]
        for tag_name in skill_data["tags"]:
            tag_id = tag_ids.get(tag_name)
            if tag_id:
                assoc_rows.append({"skill_id": skill_id, "tag_id": tag_id})
    if assoc_rows:
        op.bulk_insert(skill_tag_assoc_table, assoc_rows)

    # 累计每个 tag 的引用次数, 用一次 UPDATE 批量 +N, 而不是每个 (skill, tag) 一条 UPDATE.
    # 之前是 f-string 直接拼 tag_id 字符串, 既不安全 (SQL 注入) 又慢 (N 条 round-trip).
    tag_usage_counter: dict[str, int] = {}
    for skill_data in SEED_SKILLS:
        for tag_name in skill_data["tags"]:
            tag_id = tag_ids.get(tag_name)
            if tag_id:
                tag_usage_counter[tag_id] = tag_usage_counter.get(tag_id, 0) + 1
    for tag_id, count in tag_usage_counter.items():
        op.execute(
            text(
                "UPDATE tags SET usage_count = usage_count + :inc WHERE id = :tid"
            ),
            {"inc": count, "tid": tag_id},
        )
