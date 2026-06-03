from __future__ import annotations

import typer

from app.cli.commands import (
    cache_app,
    categories_app,
    export_app,
    import_app,
    index_app,
    search_app,
    skills_app,
    tags_app,
)

cli = typer.Typer(
    name="skill-cli",
    help="Modern Skill Library CLI - 管理 AI 技能库的命令行工具",
    no_args_is_help=True,
)

cli.add_typer(skills_app, name="skills", help="技能管理")
cli.add_typer(categories_app, name="categories", help="分类管理")
cli.add_typer(tags_app, name="tags", help="标签管理")
cli.add_typer(search_app, name="search", help="搜索")
cli.add_typer(import_app, name="import", help="导入")
cli.add_typer(export_app, name="export", help="导出")
cli.add_typer(index_app, name="index", help="索引管理")
cli.add_typer(cache_app, name="cache", help="缓存管理")


@cli.command()
def version():
    """显示版本信息"""
    from app.core.config import get_settings

    settings = get_settings()
    typer.echo(f"{settings.APP_NAME} v{settings.APP_VERSION}")


if __name__ == "__main__":
    cli()
