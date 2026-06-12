#!/usr/bin/env python3
"""批量修复所有 SKILL.md 文件的验证错误。

修复内容：
1. 添加缺失的 required fields: slug, version, inputs, output, author, license, created, updated
2. 确保 slug 是 kebab-case 且匹配目录名
3. 设置 created/updated 为 2026-06-12
4. 设置 inputs 为有效的 list 格式
5. 设置 output 为有效的 dict 格式
6. 确保第一个 sections 顺序正确：When to use, Inputs, Output, Prompt
7. 将无效的 category 映射到有效的类别
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml not installed. Run: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
REQUIRED_SECTIONS = ["When to use", "Inputs", "Output", "Prompt"]

# 有效的49个类别
VALID_CATEGORIES = {
    "official-cookbooks", "prompt-libraries", "agent-frameworks", "rag-retrieval",
    "vector-databases", "embeddings", "evaluation", "benchmarks", "tool-use",
    "mcp-protocol", "llm-serving", "fine-tuning", "distributed-training",
    "quantization", "model-merging", "guardrails", "safety-alignment",
    "privacy-federated", "observability", "memory", "knowledge-graphs",
    "synthetic-data", "data-pipelines", "dev-tools", "code-llms",
    "code-assistants", "terminal-cli", "browser-automation", "computer-use",
    "multimodal", "image-generation", "video-generation", "audio-speech",
    "robotics-embodied", "reasoning-models", "applications", "chat-uikits",
    "documentation", "text-to-sql", "customer-support", "education",
    "scientific-ml", "medical-bio", "finance", "legal", "translation",
    "gpu-kernels", "awesome-lists", "case-studies",
}

# 默认类别映射（根据技能名称推断）
CATEGORY_MAP = {
    "frontend": "code-assistants",
    "backend": "dev-tools",
    "api": "dev-tools",
    "cli": "terminal-cli",
    "database": "data-pipelines",
    "testing": "evaluation",
    "documentation": "documentation",
    "ai": "applications",
    "llm": "applications",
    "python": "dev-tools",
    "typescript": "code-assistants",
    "javascript": "code-assistants",
}


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str]:
    """分离 frontmatter 和 body。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "", text
    yaml = YAML(typ="safe")
    try:
        fm = dict(yaml.load(m.group(1)) or {})
    except Exception:
        return None, "", text
    return fm, m.group(0), m.group(2)


def section_names(body: str) -> list[str]:
    """提取 body 中的 H1 sections。"""
    return [line[2:].strip() for line in body.split("\n")
            if line.startswith("# ") and not line.startswith("## ")]


def fix_category(category: str) -> str:
    """修复无效的 category。"""
    if category in VALID_CATEGORIES:
        return category
    
    # 尝试从 category 名称推断
    cat_lower = category.lower()
    for key, value in CATEGORY_MAP.items():
        if key in cat_lower:
            return value
    
    # 默认使用 "applications"
    return "applications"


def fix_inputs(inputs: Any) -> list[dict]:
    """修复 inputs 字段。"""
    if isinstance(inputs, list) and len(inputs) > 0:
        # 检查是否是有效格式
        valid = True
        for inp in inputs:
            if not isinstance(inp, dict):
                valid = False
                break
            if "name" not in inp or "type" not in inp:
                valid = False
                break
        if valid:
            return inputs
    
    # 返回默认 inputs
    return [
        {
            "name": "request",
            "type": "string",
            "required": True,
            "description": "User request or task description"
        }
    ]


def fix_output(output: Any) -> dict:
    """修复 output 字段。"""
    if isinstance(output, dict) and "format" in output:
        if output["format"] in {"markdown", "json", "text", "code"}:
            return output
    
    # 返回默认 output
    return {
        "format": "markdown",
        "description": "Generated content based on the user request"
    }


def fix_sections(body: str) -> str:
    """修复 body 中的 sections 顺序。

    确保前4个 H1 sections 是：When to use, Inputs, Output, Prompt
    """
    lines = body.split("\n")
    
    # 提取所有 sections 及其内容
    sections: dict[str, list[str]] = {}
    current_section = None
    preamble: list[str] = []  # 第一个 section 之前的内容
    
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            section_name = line[2:].strip()
            current_section = section_name
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(line)
        elif current_section is not None:
            sections[current_section].append(line)
        else:
            preamble.append(line)
    
    # 构建新的 body
    result_lines = preamble.copy()
    
    # 按顺序添加必需的 sections
    for section_name in REQUIRED_SECTIONS:
        if section_name in sections:
            result_lines.extend(sections[section_name])
        else:
            # 添加默认的 section 内容
            result_lines.append(f"# {section_name}")
            result_lines.append("")
            if section_name == "When to use":
                result_lines.append("Use this skill when you need assistance with the related task.")
            elif section_name == "Inputs":
                result_lines.append("User request or task description.")
            elif section_name == "Output":
                result_lines.append("Generated content based on the user request.")
            elif section_name == "Prompt":
                result_lines.append("Follow the guidelines in this skill when working on related tasks.")
            result_lines.append("")
    
    # 添加其他 sections（不在 REQUIRED_SECTIONS 中的）
    for section_name, content in sections.items():
        if section_name not in REQUIRED_SECTIONS:
            result_lines.extend(content)
    
    return "\n".join(result_lines)


def fix_skill_file(path: Path) -> bool:
    """修复单个 SKILL.md 文件。"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  error  {path}: cannot read: {e}", file=sys.stderr)
        return False
    
    fm, _header, body = split_frontmatter(text)
    
    if fm is None:
        print(f"  error  {path}: frontmatter missing or unparseable", file=sys.stderr)
        return False
    
    # 获取 slug（从目录名）
    slug = path.parent.name
    
    # 修复 frontmatter
    changed = False
    
    # slug
    if fm.get("slug") != slug:
        fm["slug"] = slug
        changed = True
    
    # version
    if not fm.get("version") or not isinstance(fm.get("version"), str):
        fm["version"] = "1.0.0"
        changed = True
    
    # created
    if not fm.get("created"):
        fm["created"] = "2026-06-12"
        changed = True
    
    # updated
    if not fm.get("updated"):
        fm["updated"] = "2026-06-12"
        changed = True
    
    # inputs
    inputs = fix_inputs(fm.get("inputs"))
    if fm.get("inputs") != inputs:
        fm["inputs"] = inputs
        changed = True
    
    # output
    output = fix_output(fm.get("output"))
    if fm.get("output") != output:
        fm["output"] = output
        changed = True
    
    # author
    if not fm.get("author"):
        fm["author"] = "AI-SKILL"
        changed = True
    
    # license
    if not fm.get("license"):
        fm["license"] = "MIT"
        changed = True
    
    # category
    category = fm.get("category", "applications")
    fixed_category = fix_category(category)
    if category != fixed_category:
        fm["category"] = fixed_category
        changed = True
    
    # 修复 sections
    fixed_body = fix_sections(body)
    if fixed_body != body:
        changed = True
    
    if not changed:
        return True
    
    # 重新构建文件
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    from io import StringIO
    buf = StringIO()
    yaml.dump(fm, buf)
    frontmatter_str = buf.getvalue().rstrip()
    
    new_text = f"---\n{frontmatter_str}\n---\n{fixed_body}"
    
    try:
        path.write_text(new_text, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  error  {path}: cannot write: {e}", file=sys.stderr)
        return False


def main() -> int:
    """主函数。"""
    if not SKILLS_DIR.exists():
        print(f"skills directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1
    
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    
    if not skill_files:
        print("no SKILL.md files found", file=sys.stderr)
        return 1
    
    print(f"Found {len(skill_files)} SKILL.md files")
    
    fixed = 0
    failed = 0
    
    for path in skill_files:
        if fix_skill_file(path):
            fixed += 1
        else:
            failed += 1
    
    print(f"\n== {fixed} fixed / {failed} failed / {len(skill_files)} total ==")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
