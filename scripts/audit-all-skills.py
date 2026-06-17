#!/usr/bin/env python3
"""Audit all skills for quality issues."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
AUDIT_JSON = REPO / "scripts" / "skill-audit.json"

# Must match validate-skill.py REQUIRED_SECTIONS
REQUIRED_SECTIONS = ["When to use", "Inputs", "Output", "Prompt"]


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str] | None:
    """Parse YAML frontmatter using ruamel.yaml, return (fm, body) or None."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        from ruamel.yaml import YAML
        yaml = YAML(typ="safe")
        fm = yaml.load(parts[1])
        if fm is None:
            fm = {}
    except Exception:
        return None
    return (dict(fm), parts[2])


def audit_skill(slug: str) -> dict[str, Any]:
    """Audit a single skill directory."""
    skill_md = SKILLS_DIR / slug / "SKILL.md"

    if not skill_md.exists():
        return {"slug": slug, "error": "SKILL.md not found"}

    content = skill_md.read_text(encoding="utf-8")
    parsed = parse_frontmatter(content)
    if parsed is None:
        return {"slug": slug, "error": "Malformed frontmatter"}

    fm, body = parsed
    issues: list[str] = []

    # 1. Check needs_review
    needs_review = bool(fm.get("needs_review", False))

    # 2. Check Chinese translations
    has_name_zh = bool(fm.get("name_zh"))
    has_desc_zh = bool(fm.get("description_zh"))
    if not has_name_zh:
        issues.append("missing name_zh")
    if not has_desc_zh:
        issues.append("missing description_zh")

    # 3. Check tags
    tags = fm.get("tags", [])
    tags_raw = ", ".join(tags) if isinstance(tags, list) else str(tags)
    if isinstance(tags, list) and "needs-tagging" in tags:
        issues.append("placeholder tags")

    # 4. Check H1 sections (must match validate-skill.py)
    h1_sections = re.findall(r"^# (.+)$", body, re.MULTILINE)
    missing_sections = [s for s in REQUIRED_SECTIONS if s not in h1_sections]
    if missing_sections:
        issues.append(f"missing sections: {', '.join(missing_sections)}")

    # 5. Check body length
    body_lines = len(body.strip().split("\n"))
    if body_lines < 20:
        issues.append(f"short body ({body_lines} lines)")

    # 6. Check for code examples
    has_code = "```" in body
    if not has_code:
        issues.append("no code examples")

    # 7. Check category
    category = str(fm.get("category", ""))

    # 8. Check platforms
    platforms = fm.get("platforms", [])

    return {
        "slug": slug,
        "name": str(fm.get("name", "")),
        "category": category,
        "platforms": platforms,
        "needs_review": needs_review,
        "has_name_zh": has_name_zh,
        "has_desc_zh": has_desc_zh,
        "tags": tags_raw,
        "h1_sections": h1_sections,
        "missing_sections": missing_sections,
        "body_lines": body_lines,
        "has_code": has_code,
        "issues": issues,
        "issue_count": len(issues),
    }


def main() -> int:
    """Audit all skills."""
    if not SKILLS_DIR.exists():
        print(f"skills directory not found at {SKILLS_DIR}", file=sys.stderr)
        return 1

    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
            result = audit_skill(skill_dir.name)
            skills.append(result)

    # Summary
    total = len(skills)
    needs_review = sum(1 for s in skills if s.get("needs_review"))
    missing_zh = sum(1 for s in skills if not s.get("has_name_zh") or not s.get("has_desc_zh"))
    placeholder_tags = sum(1 for s in skills if "placeholder tags" in s.get("issues", []))
    missing_sections = sum(1 for s in skills if s.get("missing_sections"))
    short_body = sum(1 for s in skills if any("short body" in i for i in s.get("issues", [])))
    no_code = sum(1 for s in skills if not s.get("has_code"))

    print("=== SKILL AUDIT SUMMARY ===")
    print(f"Total skills: {total}")
    print(f"Needs review: {needs_review}")
    print(f"Missing Chinese: {missing_zh}")
    print(f"Placeholder tags: {placeholder_tags}")
    print(f"Missing sections: {missing_sections}")
    print(f"Short body (<20 lines): {short_body}")
    print(f"No code examples: {no_code}")
    print()

    # Category distribution
    categories: dict[str, list[str]] = defaultdict(list)
    for s in skills:
        if not s.get("error"):
            categories[s.get("category", "unknown")].append(s["slug"])

    print("=== CATEGORY DISTRIBUTION ===")
    for cat, slugs in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"{cat:30s} {len(slugs):3d}")
    print()

    # Skills with most issues
    print("=== SKILLS WITH MOST ISSUES ===")
    sorted_skills = sorted(skills, key=lambda s: -s.get("issue_count", 0))
    for s in sorted_skills[:20]:
        if s.get("issue_count", 0) > 0:
            print(f"{s['slug']:40s} {s['issue_count']:2d} issues: {', '.join(s['issues'][:3])}")
    print()

    # Save full audit
    AUDIT_JSON.write_text(
        json.dumps(skills, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Full audit saved to {AUDIT_JSON.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
