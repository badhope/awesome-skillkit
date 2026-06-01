from __future__ import annotations

import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    ZIP = "zip"


class ImportExportService:

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

    def __init__(
        self,
        skills_db: Optional[Dict[str, Dict[str, Any]]] = None,
        export_dir: str = "/tmp/skill_exports",
    ):
        self.skills_db: Dict[str, Dict[str, Any]] = skills_db or {}
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def set_skills_db(self, skills: Dict[str, Dict[str, Any]]) -> None:
        self.skills_db = skills

    def import_from_markdown(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = self._parse_frontmatter(content)
        if frontmatter is None:
            raise ValueError(f"No valid YAML frontmatter found in {file_path}")

        skill = self._convert_old_frontmatter(frontmatter)
        skill["content"] = body
        skill["source_file"] = os.path.basename(file_path)
        skill["imported_at"] = datetime.utcnow().isoformat()

        if "id" not in skill:
            import uuid
            skill["id"] = str(uuid.uuid4())

        if "name" not in skill:
            stem = Path(file_path).stem
            skill["name"] = stem.replace("_", " ").replace("-", " ").title()

        if "version" not in skill:
            skill["version"] = "1.0.0"

        skill_id = str(skill["id"])
        self.skills_db[skill_id] = skill

        return skill

    def export_to_markdown(self, skill_id: str, output_path: Optional[str] = None) -> str:
        skill = self.skills_db.get(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        frontmatter: Dict[str, Any] = {}
        frontmatter_keys = [
            "name", "description", "version", "author", "license",
            "category", "tags", "dependencies", "created_at", "updated_at",
        ]

        for key in frontmatter_keys:
            if key in skill and skill[key]:
                frontmatter[key] = skill[key]

        yaml_content = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

        markdown_body = skill.get("content", "")

        full_content = f"---\n{yaml_content}---\n\n{markdown_body}"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            return output_path

        return full_content

    def batch_import_from_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        imported: List[Dict[str, Any]] = []
        dir_path = os.path.abspath(dir_path)

        skill_md_files = list(Path(dir_path).rglob("SKILL.md"))
        skill_md_files.extend(Path(dir_path).rglob("skill.md"))

        for md_file in skill_md_files:
            try:
                skill = self.import_from_markdown(str(md_file))
                imported.append(skill)
            except Exception:
                pass

        for md_file in Path(dir_path).rglob("*.md"):
            if md_file.name.lower() in ("skill.md", "readme.md"):
                continue
            try:
                skill = self.import_from_markdown(str(md_file))
                imported.append(skill)
            except Exception:
                pass

        return imported

    def export_skill_bundle(
        self,
        skill_ids: List[str],
        output_path: Optional[str] = None,
    ) -> str:
        if not output_path:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.export_dir, f"skill_bundle_{timestamp}.zip")

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            manifest: Dict[str, Any] = {
                "exported_at": datetime.utcnow().isoformat(),
                "skill_count": 0,
                "skills": [],
            }

            for skill_id in skill_ids:
                skill = self.skills_db.get(skill_id)
                if not skill:
                    continue

                skill_name = self._sanitize_filename(skill.get("name", skill_id))
                json_path = f"{skill_name}.json"
                markdown_path = f"{skill_name}.md"

                json_data = self._skill_to_json_export(skill)
                zf.writestr(json_path, json.dumps(json_data, indent=2, ensure_ascii=False))

                markdown_content = self.export_to_markdown(skill_id)
                zf.writestr(markdown_path, markdown_content)

                manifest["skill_count"] += 1
                manifest["skills"].append({
                    "id": skill_id,
                    "name": skill.get("name", ""),
                    "version": skill.get("version", "1.0.0"),
                    "json_file": json_path,
                    "markdown_file": markdown_path,
                })

            zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        return output_path

    def import_skill_bundle(self, zip_path: str) -> List[Dict[str, Any]]:
        imported: List[Dict[str, Any]] = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            manifest_data = None
            try:
                manifest_data = json.loads(zf.read("manifest.json"))
            except (KeyError, json.JSONDecodeError):
                pass

            if manifest_data and "skills" in manifest_data:
                for skill_entry in manifest_data["skills"]:
                    json_file = skill_entry.get("json_file")
                    if json_file:
                        try:
                            skill_data = json.loads(zf.read(json_file))
                            skill_id = str(skill_data.get("id", ""))
                            if skill_id:
                                self.skills_db[skill_id] = skill_data
                                imported.append(skill_data)
                        except (KeyError, json.JSONDecodeError):
                            continue

            for file_name in zf.namelist():
                if file_name.endswith(".json") and file_name != "manifest.json":
                    if manifest_data:
                        manifest_ids = {s["id"] for s in manifest_data.get("skills", [])}
                        already_imported = any(
                            s.get("id") in manifest_ids for s in imported
                        )
                        if already_imported:
                            continue
                    try:
                        skill_data = json.loads(zf.read(file_name))
                        skill_id = str(skill_data.get("id", ""))
                        if skill_id and skill_id not in self.skills_db:
                            self.skills_db[skill_id] = skill_data
                            imported.append(skill_data)
                    except (json.JSONDecodeError, KeyError):
                        continue

                if file_name.endswith(".md") and file_name != "manifest.json":
                    try:
                        content = zf.read(file_name).decode("utf-8")
                        frontmatter, body = self._parse_frontmatter(content)
                        if frontmatter:
                            skill = self._convert_old_frontmatter(frontmatter)
                            skill["content"] = body
                            if "id" not in skill:
                                import uuid
                                skill["id"] = str(uuid.uuid4())
                            skill_id = str(skill["id"])
                            if skill_id not in self.skills_db:
                                self.skills_db[skill_id] = skill
                                imported.append(skill)
                    except (UnicodeDecodeError, Exception):
                        continue

        return imported

    def export_skill_as_json(self, skill_id: str, output_path: Optional[str] = None) -> str:
        skill = self.skills_db.get(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        json_data = self._skill_to_json_export(skill)
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            return output_path

        return json_str

    def export_skill_as_yaml(self, skill_id: str, output_path: Optional[str] = None) -> str:
        skill = self.skills_db.get(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        yaml_str = yaml.dump(skill, default_flow_style=False, allow_unicode=True, sort_keys=False)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)
            return output_path

        return yaml_str

    def _skill_to_json_export(self, skill: Dict[str, Any]) -> Dict[str, Any]:
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
            "exported_at": datetime.utcnow().isoformat(),
        }

    def _parse_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        content = content.strip()

        if not content.startswith("---"):
            return None, content

        rest = content[3:]
        end_idx = rest.find("---")
        if end_idx == -1:
            return None, content

        frontmatter_str = rest[:end_idx].strip()
        body = rest[end_idx + 3:].strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None, content

        if not isinstance(frontmatter, dict):
            return None, content

        return frontmatter, body

    def _convert_old_frontmatter(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        converted: Dict[str, Any] = {}

        for old_key, new_key in self.OLD_FRONTMATTER_KEY_MAP.items():
            if old_key in frontmatter:
                converted[new_key] = frontmatter[old_key]

        for key, value in frontmatter.items():
            if key not in self.OLD_FRONTMATTER_KEY_MAP:
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

    def _sanitize_filename(self, name: str) -> str:
        sanitized = re.sub(r"[^\w\s-]", "", name)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = sanitized.strip("_")
        return sanitized or "skill"

    def list_exportable_skills(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": skill_id,
                "name": skill.get("name", ""),
                "version": skill.get("version", "1.0.0"),
                "category": skill.get("category", ""),
            }
            for skill_id, skill in self.skills_db.items()
        ]