from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.content_i18n import escape_like
from app.db import async_session_factory
from app.models import (
    Category,
    Skill,
    Tag,
)
from app.services.cache import CacheService
from app.services.import_export import ImportExportService
from app.services.vector_search import VectorSearchService

settings = get_settings()
console = Console()
err_console = Console(stderr=True)


async def _get_db() -> AsyncSession:
    return async_session_factory()


skills_app = typer.Typer(help="技能管理命令")
categories_app = typer.Typer(help="分类管理命令")
tags_app = typer.Typer(help="标签管理命令")
search_app = typer.Typer(help="搜索命令")
import_app = typer.Typer(help="导入命令")
export_app = typer.Typer(help="导出命令")
index_app = typer.Typer(help="索引管理命令")
cache_app = typer.Typer(help="缓存管理命令")


@skills_app.command("list")
def list_skills(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="按分类过滤"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="按状态过滤"),
    complexity: Optional[str] = typer.Option(None, "--complexity", help="按复杂度过滤"),
    limit: int = typer.Option(20, "--limit", "-l", help="返回数量"),
    offset: int = typer.Option(0, "--offset", "-o", help="偏移量"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息"),
):
    async def _run():
        db = await _get_db()
        try:
            query = select(Skill).options(
                selectinload(Skill.category),
                selectinload(Skill.tags),
                selectinload(Skill.author),
            )
            if category:
                query = query.join(Category).where(Category.slug == category)
            if status:
                query = query.where(Skill.status == status)
            if complexity:
                query = query.where(Skill.complexity == complexity)
            query = query.order_by(Skill.updated_at.desc()).offset(offset).limit(limit)

            result = await db.execute(query)
            skills = result.unique().scalars().all()

            count_query = select(func.count()).select_from(Skill)
            if category:
                count_query = count_query.join(Category).where(Category.slug == category)
            if status:
                count_query = count_query.where(Skill.status == status)
            if complexity:
                count_query = count_query.where(Skill.complexity == complexity)
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            if not skills:
                console.print("[yellow]No skills found.[/yellow]")
                return

            if verbose:
                table = Table(title=f"Skills ({total} total)")
                table.add_column("ID", style="dim")
                table.add_column("Name", style="bold")
                table.add_column("Slug")
                table.add_column("Category")
                table.add_column("Version")
                table.add_column("Complexity")
                table.add_column("Status")
                table.add_column("Rating")
                table.add_column("Tags")
                table.add_column("Downloads")
                table.add_column("Updated")

                for skill in skills:
                    tags_str = ", ".join(t.name for t in (skill.tags or [])[:5])
                    if skill.tags and len(skill.tags) > 5:
                        tags_str += f" +{len(skill.tags) - 5}"
                    table.add_row(
                        str(skill.id)[:8] + "...",
                        skill.name or "",
                        skill.slug or "",
                        skill.category.name if skill.category else "-",
                        skill.version or "",
                        skill.complexity.value if skill.complexity else "-",
                        skill.status.value if skill.status else "-",
                        f"{skill.rating_avg:.1f} ({skill.rating_count})",
                        tags_str,
                        str(skill.download_count),
                        skill.updated_at.strftime("%Y-%m-%d") if skill.updated_at else "-",
                    )
            else:
                table = Table(title=f"Skills ({total} total)")
                table.add_column("ID", style="dim")
                table.add_column("Name", style="bold")
                table.add_column("Category")
                table.add_column("Version")
                table.add_column("Status")

                for skill in skills:
                    table.add_row(
                        str(skill.id)[:8] + "...",
                        skill.name or "",
                        skill.category.name if skill.category else "-",
                        skill.version or "",
                        skill.status.value if skill.status else "-",
                    )

            console.print(table)
        finally:
            await db.close()

    asyncio.run(_run())


@skills_app.command("search")
def search_skills(
    query: str = typer.Argument(..., help="搜索关键词"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="按分类过滤"),
    limit: int = typer.Option(20, "--limit", "-l", help="返回数量"),
):
    async def _run():
        db = await _get_db()
        try:
            search_pattern = f"%{escape_like(query)}%"
            stmt = (
                select(Skill)
                .options(
                    selectinload(Skill.category),
                    selectinload(Skill.tags),
                )
                .where(
                    (Skill.name.ilike(search_pattern, escape="\\"))
                    | (Skill.description.ilike(search_pattern, escape="\\"))
                    | (Skill.slug.ilike(search_pattern, escape="\\"))
                )
                .order_by(Skill.rating_avg.desc())
                .limit(limit)
            )
            if category:
                stmt = stmt.join(Category).where(Category.slug == category)

            result = await db.execute(stmt)
            skills = result.unique().scalars().all()

            if not skills:
                console.print(f"[yellow]No skills found for '{query}'[/yellow]")
                return

            table = Table(title=f"Search: '{query}'")
            table.add_column("Name", style="bold")
            table.add_column("Slug")
            table.add_column("Category")
            table.add_column("Rating")
            table.add_column("Description")

            for skill in skills:
                desc = skill.description or ""
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                table.add_row(
                    skill.name or "",
                    skill.slug or "",
                    skill.category.name if skill.category else "-",
                    f"{skill.rating_avg:.1f}",
                    desc,
                )

            console.print(table)
        finally:
            await db.close()

    asyncio.run(_run())


@skills_app.command("create")
def create_skill(
    name: str = typer.Option(..., "--name", "-n", help="技能名称"),
    slug: str = typer.Option(..., "--slug", help="技能标识"),
    description: str = typer.Option("", "--description", "-d", help="技能描述"),
    version: str = typer.Option("1.0.0", "--version", help="版本号"),
    category: str = typer.Option(..., "--category", "-c", help="分类 slug"),
    complexity: str = typer.Option("intermediate", "--complexity", help="复杂度"),
    license_str: str = typer.Option("MIT", "--license", help="许可证"),
    is_public: bool = typer.Option(True, "--public/--private", help="是否公开"),
    is_featured: bool = typer.Option(False, "--featured", help="是否精选"),
    tags: str = typer.Option("", "--tags", "-t", help="标签，逗号分隔"),
    content_json: str = typer.Option("{}", "--content-json", help="内容 JSON"),
    metadata_json: str = typer.Option("{}", "--metadata-json", help="元数据 JSON"),
):
    async def _run():
        db = await _get_db()
        try:
            existing = await db.execute(select(Skill).where(Skill.slug == slug))
            if existing.scalar_one_or_none():
                err_console.print(f"[red]Skill with slug '{slug}' already exists[/red]")
                raise typer.Exit(code=1)

            cat_result = await db.execute(select(Category).where(Category.slug == category))
            cat = cat_result.scalar_one_or_none()
            if not cat:
                err_console.print(f"[red]Category '{category}' not found[/red]")
                raise typer.Exit(code=1)

            tag_names = [t.strip() for t in tags.split(",") if t.strip()]
            tag_objects: list[Tag] = []
            for tag_name in tag_names:
                tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
                tag_obj = tag_result.scalar_one_or_none()
                if tag_obj:
                    # 已存在: skill 关联后 +1 (新建走 INSERT 关联会建立新一行, 所以 +1)
                    tag_obj.usage_count += 1
                    tag_objects.append(tag_obj)
                else:
                    # 之前漏掉了新建 tag 的 +1, 改成统一 +1
                    new_tag = Tag(name=tag_name, usage_count=1)
                    db.add(new_tag)
                    tag_objects.append(new_tag)

            skill = Skill(
                name=name,
                slug=slug,
                description=description,
                version=version,
                category_id=cat.id,
                complexity=complexity,
                license=license_str,
                is_public=is_public,
                is_featured=is_featured,
                content=json.loads(content_json),
                extra_metadata=json.loads(metadata_json),
                tags=tag_objects,
            )
            db.add(skill)
            await db.commit()
            await db.refresh(skill)

            console.print(f"[green]Skill '{skill.name}' created successfully (ID: {skill.id})[/green]")
        finally:
            await db.close()

    asyncio.run(_run())


@skills_app.command("delete")
def delete_skill(
    slug: str = typer.Argument(..., help="要删除的技能 slug"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不确认"),
):
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(select(Skill).where(Skill.slug == slug))
            skill = result.scalar_one_or_none()
            if not skill:
                err_console.print(f"[red]Skill '{slug}' not found[/red]")
                raise typer.Exit(code=1)

            if not force:
                confirm = typer.confirm(f"Are you sure you want to delete '{skill.name}'?")
                if not confirm:
                    console.print("[yellow]Cancelled.[/yellow]")
                    return

            # 删除前先把关联的 tag 各 -1 (之前是漏掉的)
            current_tag_names = {t.name for t in (skill.tags or [])}
            if current_tag_names:
                tag_rows = await db.execute(
                    select(Tag).where(Tag.name.in_(current_tag_names))
                )
                for tag in tag_rows.scalars().all():
                    if tag.usage_count > 0:
                        tag.usage_count -= 1

            await db.delete(skill)
            await db.commit()
            console.print(f"[green]Skill '{skill.name}' deleted successfully.[/green]")
        finally:
            await db.close()

    asyncio.run(_run())


@skills_app.command("stats")
def skills_stats():
    async def _run():
        db = await _get_db()
        try:
            total_result = await db.execute(select(func.count()).select_from(Skill))
            total = total_result.scalar()

            published_result = await db.execute(
                select(func.count()).select_from(Skill).where(Skill.status == "published")
            )
            published = published_result.scalar()

            draft_result = await db.execute(
                select(func.count()).select_from(Skill).where(Skill.status == "draft")
            )
            draft = draft_result.scalar()

            deprecated_result = await db.execute(
                select(func.count()).select_from(Skill).where(Skill.status == "deprecated")
            )
            deprecated = deprecated_result.scalar()

            complexity_result = await db.execute(
                select(Skill.complexity, func.count()).group_by(Skill.complexity)
            )
            complexity_rows = complexity_result.all()

            top_result = await db.execute(
                select(Skill.name, Skill.download_count)
                .order_by(Skill.download_count.desc())
                .limit(10)
            )
            top_skills = top_result.all()

            table = Table(title="Skill Statistics")
            table.add_column("Metric", style="bold")
            table.add_column("Value")

            table.add_row("Total Skills", str(total))
            table.add_row("Published", str(published))
            table.add_row("Drafts", str(draft))
            table.add_row("Deprecated", str(deprecated))

            for comp, cnt in complexity_rows:
                if comp:
                    table.add_row(f"  {comp.value}", str(cnt))

            console.print(table)

            if top_skills:
                console.print()
                top_table = Table(title="Top 10 by Downloads")
                top_table.add_column("Name", style="bold")
                top_table.add_column("Downloads")
                for name, count in top_skills:
                    top_table.add_row(name, str(count))
                console.print(top_table)
        finally:
            await db.close()

    asyncio.run(_run())


@categories_app.command("list")
def list_categories(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息"),
):
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(
                select(Category).order_by(Category.sort_order, Category.name)
            )
            categories = result.scalars().all()

            if not categories:
                console.print("[yellow]No categories found.[/yellow]")
                return

            if verbose:
                table = Table(title="Categories")
                table.add_column("ID", style="dim")
                table.add_column("Name", style="bold")
                table.add_column("Slug")
                table.add_column("Icon")
                table.add_column("Active")
                table.add_column("Skills")
                table.add_column("Description")

                for cat in categories:
                    skill_count_result = await db.execute(
                        select(func.count()).select_from(Skill).where(Skill.category_id == cat.id)
                    )
                    skill_count = skill_count_result.scalar()
                    desc = cat.description or ""
                    if len(desc) > 50:
                        desc = desc[:47] + "..."
                    table.add_row(
                        str(cat.id)[:8] + "...",
                        cat.name,
                        cat.slug,
                        cat.icon or "-",
                        "✓" if cat.is_active else "✗",
                        str(skill_count),
                        desc,
                    )
            else:
                table = Table(title="Categories")
                table.add_column("Name", style="bold")
                table.add_column("Slug")
                table.add_column("Active")

                for cat in categories:
                    table.add_row(cat.name, cat.slug, "✓" if cat.is_active else "✗")

            console.print(table)
        finally:
            await db.close()

    asyncio.run(_run())


@categories_app.command("tree")
def categories_tree():
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(
                select(Category).order_by(Category.sort_order, Category.name)
            )
            categories = result.scalars().all()

            root_cats = [c for c in categories if c.parent_id is None]

            def build_tree(cat, tree: Tree):
                label = f"[bold]{cat.name}[/bold]"
                if cat.description:
                    label += f"\n  [dim]{cat.description[:60]}[/dim]"
                branch = tree.add(label)

                children = [c for c in categories if c.parent_id and str(c.parent_id) == str(cat.id)]
                for child in children:
                    build_tree(child, branch)

            root_tree = Tree("Categories")
            for root_cat in root_cats:
                build_tree(root_cat, root_tree)

            console.print(root_tree)
        finally:
            await db.close()

    asyncio.run(_run())


@tags_app.command("list")
def list_tags(
    limit: int = typer.Option(50, "--limit", "-l", help="返回数量"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息"),
):
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(
                select(Tag).order_by(Tag.usage_count.desc()).limit(limit)
            )
            tags = result.scalars().all()

            if not tags:
                console.print("[yellow]No tags found.[/yellow]")
                return

            table = Table(title="Tags")
            table.add_column("Name", style="bold")
            table.add_column("Color")
            table.add_column("Usage Count")
            if verbose:
                table.add_column("Description")
                table.add_column("Created")

            for tag in tags:
                color_display = f"[{tag.color}]{tag.color}[/{tag.color}]" if tag.color else "-"
                row = [tag.name, color_display, str(tag.usage_count)]
                if verbose:
                    row.append(tag.description or "")
                    row.append(tag.created_at.strftime("%Y-%m-%d") if tag.created_at else "-")
                table.add_row(*row)

            console.print(table)
        finally:
            await db.close()

    asyncio.run(_run())


@tags_app.command("popular")
def popular_tags(
    limit: int = typer.Option(20, "--limit", "-l", help="返回数量"),
):
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(
                select(Tag).order_by(Tag.usage_count.desc()).limit(limit)
            )
            tags = result.scalars().all()

            if not tags:
                console.print("[yellow]No tags found.[/yellow]")
                return

            max_count = tags[0].usage_count if tags else 1

            console.print("[bold]Popular Tags:[/bold]\n")
            for tag in tags:
                bar_width = int((tag.usage_count / max_count) * 40) if max_count > 0 else 0
                bar = "█" * bar_width
                color_tag = tag.color or "#ffffff"
                console.print(
                    f"  [{color_tag}]{tag.name:20}[/{color_tag}] "
                    f"[cyan]{bar}[/cyan] {tag.usage_count}"
                )
        finally:
            await db.close()

    asyncio.run(_run())


@search_app.command("semantic")
def semantic_search(
    query: str = typer.Argument(..., help="搜索查询"),
    limit: int = typer.Option(10, "--limit", "-l", help="返回数量"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="按分类过滤"),
):
    async def _run():
        try:
            vector_service = VectorSearchService(
                qdrant_url=settings.QDRANT_URL,
                qdrant_api_key=settings.QDRANT_API_KEY,
            )

            results = vector_service.search_skills(
                query=query,
                limit=limit,
                category_id=category,
                only_public=True,
            )

            if not results:
                console.print(f"[yellow]No results found for '{query}'[/yellow]")
                return

            table = Table(title=f"Semantic Search: '{query}'")
            table.add_column("Name", style="bold")
            table.add_column("Description")
            table.add_column("Score", style="cyan")
            table.add_column("Tags")

            for r in results:
                desc = r.get("description", "") or ""
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                tags = r.get("tags", [])
                tags_str = ", ".join(tags[:5])
                if len(tags) > 5:
                    tags_str += f" +{len(tags) - 5}"
                table.add_row(
                    r.get("name", ""),
                    desc,
                    f"{r.get('score', 0):.4f}",
                    tags_str,
                )

            console.print(table)
        except Exception as e:
            err_console.print(f"[red]Search error: {e}[/red]")

    asyncio.run(_run())


@search_app.command("hybrid")
def hybrid_search(
    query: str = typer.Argument(..., help="搜索查询"),
    limit: int = typer.Option(10, "--limit", "-l", help="返回数量"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="按分类过滤"),
    vector_weight: float = typer.Option(0.7, "--vector-weight", help="向量搜索权重 (0-1)"),
):
    async def _run():
        try:
            vector_service = VectorSearchService(
                qdrant_url=settings.QDRANT_URL,
                qdrant_api_key=settings.QDRANT_API_KEY,
                embedding_model="all-MiniLM-L6-v2",
                vector_size=384,
            )

            filters: dict[str, Any] = {"only_public": True}
            if category:
                filters["category_id"] = category

            results = vector_service.hybrid_search(
                query=query,
                limit=limit,
                filters=filters,
                vector_weight=vector_weight,
            )

            if not results:
                console.print(f"[yellow]No results found for '{query}'[/yellow]")
                return

            table = Table(title=f"Hybrid Search: '{query}' (vector={vector_weight}, bm25={1-vector_weight:.1f})")
            table.add_column("Name", style="bold")
            table.add_column("Description")
            table.add_column("Combined", style="cyan")
            table.add_column("Vector", style="dim")
            table.add_column("BM25", style="dim")
            table.add_column("Tags")

            for r in results:
                desc = r.get("description", "") or ""
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                tags = r.get("tags", [])
                tags_str = ", ".join(tags[:3])
                table.add_row(
                    r.get("name", ""),
                    desc,
                    f"{r.get('score', 0):.4f}",
                    f"{r.get('vector_score', 0):.4f}",
                    f"{r.get('bm25_score', 0):.4f}",
                    tags_str,
                )

            console.print(table)
        except Exception as e:
            err_console.print(f"[red]Search error: {e}[/red]")

    asyncio.run(_run())


@import_app.command("from-dir")
def import_from_dir(
    directory: str = typer.Argument(..., help="技能文件所在目录"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="递归搜索子目录"),
):
    async def _run():
        db = await _get_db()
        try:
            import_service = ImportExportService(db, export_dir="/tmp/skill_exports")

            dir_path = Path(directory)
            if not dir_path.exists():
                err_console.print(f"[red]Directory not found: {directory}[/red]")
                raise typer.Exit(code=1)

            skill_data_list = import_service.batch_import_from_directory(str(dir_path))
            console.print(f"[bold]Importing skills from: {directory}[/bold]")
            console.print(f"  Parsed {len(skill_data_list)} candidate markdown files\n")

            imported_count = 0
            error_count = 0
            skipped_count = 0

            for skill_data in skill_data_list:
                try:
                    persisted = await import_service.persist_skill(skill_data)
                    if persisted is None:
                        skipped_count += 1
                        console.print(
                            f"  [yellow]Skipped (exists or empty): "
                            f"{skill_data.get('source_file', '?')} -> {skill_data.get('name')}[/yellow]"
                        )
                        continue
                    imported_count += 1
                    console.print(
                        f"  [green]Imported: {skill_data.get('source_file', '?')} -> "
                        f"{persisted.name}[/green]"
                    )
                except Exception as e:
                    error_count += 1
                    err_console.print(
                        f"  [red]Error: {skill_data.get('source_file', '?')} - {e}[/red]"
                    )

            await db.commit()
            console.print(
                f"\n[bold green]Import complete: {imported_count} imported, "
                f"{skipped_count} skipped, {error_count} errors[/bold green]"
            )
        finally:
            await db.close()

    asyncio.run(_run())


@export_app.command("skill")
def export_skill(
    slug: str = typer.Argument(..., help="要导出的技能 slug"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    format: str = typer.Option("markdown", "--format", "-f", help="导出格式 (markdown, json, yaml)"),
):
    async def _run():
        db = await _get_db()
        try:
            result = await db.execute(select(Skill).where(Skill.slug == slug))
            skill = result.scalar_one_or_none()
            if not skill:
                err_console.print(f"[red]Skill '{slug}' not found[/red]")
                raise typer.Exit(code=1)

            import_service = ImportExportService(db)

            if format == "json":
                content = await import_service.export_skill_as_json(str(skill.id), output_path=output)
                if not output:
                    console.print_json(content)
            elif format == "yaml":
                content = await import_service.export_skill_as_yaml(str(skill.id), output_path=output)
                if not output:
                    console.print(content)
            else:
                content = await import_service.export_to_markdown(str(skill.id), output_path=output)
                if not output:
                    console.print(content)

            if output:
                console.print(f"[green]Exported to: {output}[/green]")
            else:
                console.print(f"\n[green]Skill '{skill.name}' exported as {format}.[/green]")
        finally:
            await db.close()

    asyncio.run(_run())


@index_app.command("rebuild")
def rebuild_index(
    confirm: bool = typer.Option(False, "--yes", "-y", help="跳过确认"),
):
    async def _run():
        db = await _get_db()
        try:
            if not confirm:
                sure = typer.confirm("This will rebuild the entire search index. Continue?")
                if not sure:
                    console.print("[yellow]Cancelled.[/yellow]")
                    return

            result = await db.execute(
                select(Skill)
                .options(selectinload(Skill.tags), selectinload(Skill.category))
                .where(Skill.is_public == True)
            )
            skills = result.unique().scalars().all()

            skill_dicts: list[dict[str, Any]] = []
            for skill in skills:
                skill_dicts.append({
                    "id": str(skill.id),
                    "name": skill.name or "",
                    "description": skill.description or "",
                    "category_id": str(skill.category_id) if skill.category_id else "",
                    "category": skill.category.name if skill.category else "",
                    "tags": [t.name for t in (skill.tags or [])],
                    "is_public": skill.is_public,
                    "version": skill.version or "1.0.0",
                    "author": str(skill.author_id) if skill.author_id else "",
                    "usage_count": skill.usage_count,
                    "rating": skill.rating_avg,
                    "content": skill.content.get("prompt_template", "") if skill.content else "",
                    "created_at": skill.created_at.isoformat() if skill.created_at else None,
                    "updated_at": skill.updated_at.isoformat() if skill.updated_at else None,
                })

            vector_service = VectorSearchService(
                qdrant_url=settings.QDRANT_URL,
                qdrant_api_key=settings.QDRANT_API_KEY,
            )

            vector_service.rebuild_index(skill_dicts)

            console.print(f"[green]Index rebuilt successfully with {len(skill_dicts)} skills.[/green]")
        except Exception as e:
            err_console.print(f"[red]Index rebuild error: {e}[/red]")
        finally:
            await db.close()

    asyncio.run(_run())


@cache_app.command("warm")
def warm_cache():
    async def _run():
        try:
            cache = CacheService(
                redis_url=settings.REDIS_URL,
                key_prefix="skill_library",
                default_ttl=3600,
            )
            await cache.connect()

            db = await _get_db()
            try:
                result = await db.execute(
                    select(Skill)
                    .options(selectinload(Skill.tags), selectinload(Skill.category))
                    .order_by(Skill.download_count.desc())
                    .limit(100)
                )
                skills = result.unique().scalars().all()

                skill_dicts = []
                for skill in skills:
                    skill_dicts.append({
                        "id": str(skill.id),
                        "name": skill.name,
                        "slug": skill.slug,
                        "description": skill.description,
                        "version": skill.version,
                        "complexity": skill.complexity.value if skill.complexity else None,
                        "category": skill.category.name if skill.category else None,
                        "tags": [t.name for t in (skill.tags or [])],
                        "download_count": skill.download_count,
                        "usage_count": skill.usage_count,
                        "rating_avg": skill.rating_avg,
                        "rating_count": skill.rating_count,
                    })

                count = await cache.warm_cache(popular_skills=skill_dicts)

                cat_result = await db.execute(select(Category).order_by(Category.sort_order))
                categories = cat_result.scalars().all()
                cat_dicts = [{"id": str(c.id), "name": c.name, "slug": c.slug, "description": c.description} for c in categories]
                await cache.cache_categories(cat_dicts)

                console.print(f"[green]Cache warmed: {count} skills cached, {len(cat_dicts)} categories cached.[/green]")
            finally:
                await db.close()

            await cache.disconnect()
        except Exception as e:
            err_console.print(f"[red]Cache warm error: {e}[/red]")

    asyncio.run(_run())


@cache_app.command("stats")
def cache_stats():
    async def _run():
        try:
            cache = CacheService(
                redis_url=settings.REDIS_URL,
                key_prefix="skill_library",
                default_ttl=3600,
            )
            await cache.connect()

            stats = await cache.get_cache_stats()

            table = Table(title="Cache Statistics")
            table.add_column("Metric", style="bold")
            table.add_column("Value")

            table.add_row("Used Memory", stats.get("used_memory_human", "unknown"))
            table.add_row("Peak Memory", stats.get("used_memory_peak_human", "unknown"))
            table.add_row("Connected Clients", str(stats.get("connected_clients", 0)))

            keyspace = stats.get("keyspace", {})
            for db_name, db_info in keyspace.items():
                if isinstance(db_info, dict):
                    table.add_row(f"DB {db_name} Keys", str(db_info.get("keys", 0)))
                    table.add_row(f"DB {db_name} Expires", str(db_info.get("expires", 0)))

            console.print(table)
            await cache.disconnect()
        except Exception as e:
            err_console.print(f"[red]Cache stats error: {e}[/red]")

    asyncio.run(_run())
