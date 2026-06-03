from __future__ import annotations

import json
import os
import re
import zipfile
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Category, Skill, Tag, skill_tag_association


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    ZIP = "zip"


class SkillFrontmatterParser:
    """
    纯解析器：不依赖任何外部存储，只负责
      * 拆分 frontmatter / body
      * 把旧版字段（`prompt` / `system_prompt` / `examples` / `parameters` / `model` / `metadata` / `created` / `updated`）
        折叠成新结构（`content`、`compatibility`、`created_at`、`updated_at`）
    是 import_export 与 skill_validator 之间的「单一来源」。
    """

    OLD_FRONTMATTER_KEY_MAP = {
        "name": "name",
        "description": "description",
        "license": "license",
        "compatibility": "compatibility",
        "metadata": "metadata",
        "author": "author",
        "tags": "tags",
        "version": "version",
        "category": "category",
        "dependencies": "dependencies",
        "model": "model",
        "parameters": "parameters",
        "prompt": "prompt",
        "system_prompt": "system_prompt",
        "examples": "examples",
        "created": "created_at",
        "updated": "updated_at",
    }

    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        与 skill_validator.parse_with_frontmatter 等价, 但只返回 (frontmatter, body),
        不抛 3 元 parse_error, 调用方按 frontmatter is None 判定.
        """
        content = content.strip()
        if not content.startswith("---"):
            return None, content

        rest = content[3:]
        end_idx = rest.find("---")
        if end_idx == -1:
            return None, content

        frontmatter_str = rest[:end_idx].strip()
        body = rest[end_idx + 3 :].strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None, content

        if not isinstance(frontmatter, dict):
            return None, content

        return frontmatter, body

    @classmethod
    def convert_old_frontmatter(cls, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        converted: Dict[str, Any] = {}

        for old_key, new_key in cls.OLD_FRONTMATTER_KEY_MAP.items():
            if old_key in frontmatter:
                converted[new_key] = frontmatter[old_key]

        for key, value in frontmatter.items():
            if key not in cls.OLD_FRONTMATTER_KEY_MAP:
                converted[key] = value

        if "model" in converted:
            converted.setdefault("compatibility", {})
            if isinstance(converted["compatibility"], dict):
                converted["compatibility"]["model"] = converted.pop("model")

        if "prompt" in converted:
            converted.setdefault("content", "")
            converted["content"] = converted.pop("prompt") + "\n\n" + converted["content"]

        if "system_prompt" in converted:
            converted.setdefault("content", "")
            converted["content"] = (
                "## System Prompt\n\n"
                + converted.pop("system_prompt")
                + "\n\n"
                + converted["content"]
            )

        if "examples" in converted:
            examples = converted.pop("examples")
            if isinstance(examples, list):
                converted.setdefault("content", "")
                examples_section = "## Examples\n\n"
                for i, example in enumerate(examples):
                    if isinstance(example, dict):
                        inp = example.get("input", example.get("prompt", ""))
                        out = example.get("output", example.get("response", ""))
                        examples_section += f"### Example {i + 1}\n\n"
                        if inp:
                            examples_section += f"**Input:**\n```\n{inp}\n```\n\n"
                        if out:
                            examples_section += f"**Output:**\n```\n{out}\n```\n\n"
                    elif isinstance(example, str):
                        examples_section += f"### Example {i + 1}\n\n{example}\n\n"
                converted["content"] = examples_section + converted["content"]

        if "parameters" in converted:
            params = converted.pop("parameters")
            converted.setdefault("content", "")
            if isinstance(params, dict):
                params_yaml = yaml.dump(params, default_flow_style=False)
                converted["content"] = (
                    "## Parameters\n\n```yaml\n"
                    + params_yaml
                    + "```\n\n"
                    + converted["content"]
                )

        if "metadata" in converted:
            metadata = converted.pop("metadata")
            if isinstance(metadata, dict):
                for k, v in metadata.items():
                    if k not in converted:
                        converted[k] = v

        return converted


class ImportExportService:
    """
    与多 worker / 多进程兼容的导入导出服务。
    关键改动：旧版本把数据放在进程内的 `self.skills_db` dict 里, 跨 worker 必然丢数据。
    新版本只持有一个 `AsyncSession` (`db`), 所有 read/write 都走数据库, 单实例只用来
    编排事务 / 序列化, 不保存任何业务状态。
    """

    def __init__(
        self,
        db: AsyncSession,
        export_dir: str = "/tmp/skill_exports",
    ) -> None:
        self.db = db
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    # ---- 解析入口（纯函数, 不写库） ----

    def import_from_markdown(self, file_path: str) -> Dict[str, Any]:
        """只解析 frontmatter, 不入库. 调用方拿到 dict 之后自己决定如何落库."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = SkillFrontmatterParser.parse_frontmatter(content)
        if frontmatter is None:
            raise ValueError(f"No valid YAML frontmatter found in {file_path}")

        skill = SkillFrontmatterParser.convert_old_frontmatter(frontmatter)
        skill["content"] = body
        skill["source_file"] = os.path.basename(file_path)
        skill["imported_at"] = datetime.now(timezone.utc).isoformat()

        if "id" not in skill:
            import uuid

            skill["id"] = str(uuid.uuid4())

        if "name" not in skill:
            stem = Path(file_path).stem
            skill["name"] = stem.replace("_", " ").replace("-", " ").title()

        if "version" not in skill:
            skill["version"] = "1.0.0"

        return skill

    def batch_import_from_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """返回所有解析出的 skill dict (不落库), 方便调用方逐个处理."""
        imported: List[Dict[str, Any]] = []
        dir_path = os.path.abspath(dir_path)

        seen: set = set()
        candidates: List[Path] = []
        for pattern in ("SKILL.md", "skill.md"):
            for p in Path(dir_path).rglob(pattern):
                if p not in seen:
                    seen.add(p)
                    candidates.append(p)
        for p in Path(dir_path).rglob("*.md"):
            if p.name.lower() in ("skill.md", "readme.md"):
                continue
            if p not in seen:
                seen.add(p)
                candidates.append(p)

        for md_file in candidates:
            try:
                imported.append(self.import_from_markdown(str(md_file)))
            except Exception:
                # 静默跳过, 跟旧行为一致: 解析失败的 .md 不阻塞其他文件
                continue

        return imported

    # ---- 落库入口 ----

    async def persist_skill(self, skill_data: Dict[str, Any]) -> Optional[Skill]:
        """
        把解析出来的 dict 写成 Skill / Tag 行.
        * category: 按 slug 匹配, 没找到就放空（不要创建未知分类, 避免脏数据）
        * tags:     按 name 匹配, 没有就建, 每次关联 +1 usage_count (与 API 侧逻辑保持一致)
        返回新建的 Skill ORM 对象 (None 表示已存在被跳过)
        """
        slug = (skill_data.get("name") or "").lower().replace(" ", "-")
        if not slug:
            return None

        existing = await self.db.execute(select(Skill).where(Skill.slug == slug))
        if existing.scalar_one_or_none():
            return None

        category_id: Optional[Any] = None
        cat_slug = skill_data.get("category")
        if cat_slug and isinstance(cat_slug, str):
            cat_result = await self.db.execute(
                select(Category).where(Category.slug == cat_slug)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                category_id = cat.id

        skill = Skill(
            name=skill_data.get("name", slug),
            slug=slug,
            description=skill_data.get("description", ""),
            version=skill_data.get("version", "1.0.0"),
            license=skill_data.get("license"),
            content=skill_data.get("content", {}),
            extra_metadata=skill_data.get("metadata", {}),
            category_id=category_id,
        )
        self.db.add(skill)
        await self.db.flush()  # 拿到 skill.id 才能写关联表

        tag_names = skill_data.get("tags") or []
        if isinstance(tag_names, list) and tag_names:
            tag_rows = await self.db.execute(
                select(Tag).where(Tag.name.in_(tag_names))
            )
            existing_tags = {t.name: t for t in tag_rows.scalars().all()}
            for tag_name in tag_names:
                tag = existing_tags.get(tag_name)
                if tag is None:
                    tag = Tag(name=tag_name, usage_count=1)
                    self.db.add(tag)
                    await self.db.flush()
                else:
                    tag.usage_count += 1
                await self.db.execute(
                    skill_tag_association.insert().values(
                        skill_id=skill.id, tag_id=tag.id
                    )
                )

        return skill

    # ---- 导出入口 ----

    async def _load_skill(self, skill_id: str) -> Optional[Skill]:
        try:
            import uuid as _uuid

            uid = _uuid.UUID(skill_id)
        except (ValueError, TypeError):
            return None
        result = await self.db.execute(select(Skill).where(Skill.id == uid))
        return result.scalar_one_or_none()

    @staticmethod
    def _skill_to_dict(skill: Skill) -> Dict[str, Any]:
        return {
            "id": str(skill.id),
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "category": skill.category.name if skill.category else None,
            "tags": [t.name for t in (skill.tags or [])],
            "license": skill.license,
            "content": skill.content,
            "metadata": skill.extra_metadata,
            "created_at": skill.created_at.isoformat() if skill.created_at else None,
            "updated_at": skill.updated_at.isoformat() if skill.updated_at else None,
        }

    async def export_skill_as_json(
        self, skill_id: str, output_path: Optional[str] = None
    ) -> str:
        skill = await self._load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        json_data = self._skill_to_json_export(self._skill_to_dict(skill))
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            return output_path
        return json_str

    async def export_skill_as_yaml(
        self, skill_id: str, output_path: Optional[str] = None
    ) -> str:
        skill = await self._load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        yaml_str = yaml.dump(
            self._skill_to_dict(skill),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)
            return output_path
        return yaml_str

    async def export_to_markdown(
        self, skill_id: str, output_path: Optional[str] = None
    ) -> str:
        skill = await self._load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        skill_dict = self._skill_to_dict(skill)
        frontmatter: Dict[str, Any] = {}
        frontmatter_keys = [
            "name",
            "description",
            "version",
            "author",
            "license",
            "category",
            "tags",
            "dependencies",
            "created_at",
            "updated_at",
        ]
        for key in frontmatter_keys:
            if skill_dict.get(key):
                frontmatter[key] = skill_dict[key]

        yaml_content = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        markdown_body = skill_dict.get("content", "")
        full_content = f"---\n{yaml_content}---\n\n{markdown_body}"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            return output_path
        return full_content

    async def export_skill_bundle(
        self,
        skill_ids: List[str],
        output_path: Optional[str] = None,
    ) -> str:
        if not output_path:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.export_dir, f"skill_bundle_{timestamp}.zip")

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            manifest: Dict[str, Any] = {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "skill_count": 0,
                "skills": [],
            }

            for skill_id in skill_ids:
                skill = await self._load_skill(skill_id)
                if not skill:
                    continue
                skill_dict = self._skill_to_dict(skill)
                skill_name = self._sanitize_filename(skill_dict.get("name", skill_id))
                json_path = f"{skill_name}.json"
                markdown_path = f"{skill_name}.md"

                json_data = self._skill_to_json_export(skill_dict)
                zf.writestr(json_path, json.dumps(json_data, indent=2, ensure_ascii=False))
                zf.writestr(markdown_path, await self.export_to_markdown(skill_id))

                manifest["skill_count"] += 1
                manifest["skills"].append(
                    {
                        "id": skill_id,
                        "name": skill_dict.get("name", ""),
                        "version": skill_dict.get("version", "1.0.0"),
                        "json_file": json_path,
                        "markdown_file": markdown_path,
                    }
                )

            zf.writestr(
                "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False)
            )

        return output_path

    async def import_skill_bundle(self, zip_path: str) -> List[Dict[str, Any]]:
        """从 zip 包导入, 直接落库. 解析失败的文件被静默跳过 (跟旧行为一致)."""
        imported: List[Dict[str, Any]] = []
        with zipfile.ZipFile(zip_path, "r") as zf:
            for file_name in zf.namelist():
                if not file_name.endswith((".json", ".md")):
                    continue
                try:
                    raw = zf.read(file_name)
                except KeyError:
                    continue
                if file_name.endswith(".json"):
                    try:
                        skill_data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                else:
                    frontmatter, body = SkillFrontmatterParser.parse_frontmatter(
                        raw.decode("utf-8")
                    )
                    if frontmatter is None:
                        continue
                    skill_data = SkillFrontmatterParser.convert_old_frontmatter(frontmatter)
                    skill_data["content"] = body
                    if "id" not in skill_data:
                        import uuid

                        skill_data["id"] = str(uuid.uuid4())

                persisted = await self.persist_skill(skill_data)
                if persisted is not None:
                    imported.append(self._skill_to_dict(persisted))
        return imported

    @staticmethod
    def _skill_to_json_export(skill: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": skill.get("id"),
            "name": skill.get("name"),
            "description": skill.get("description"),
            "version": skill.get("version", "1.0.0"),
            "author": skill.get("author"),
            "license": skill.get("license"),
            "category": skill.get("category"),
            "tags": skill.get("tags", []),
            "dependencies": skill.get("dependencies", []),
            "content": skill.get("content"),
            "created_at": skill.get("created_at"),
            "updated_at": skill.get("updated_at"),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        sanitized = re.sub(r"[^\w\s-]", "", name)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = sanitized.strip("_")
        return sanitized or "skill"
