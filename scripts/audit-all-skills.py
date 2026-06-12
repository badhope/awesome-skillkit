#!/usr/bin/env python3
"""Audit all 67 skills for quality issues."""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

SKILLS_DIR = Path("skills")

def audit_skill(slug: str) -> dict:
    """Audit a single skill directory."""
    skill_dir = SKILLS_DIR / slug
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        return {"slug": slug, "error": "SKILL.md not found"}
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Split frontmatter and body
    if not content.startswith("---"):
        return {"slug": slug, "error": "No frontmatter"}
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"slug": slug, "error": "Malformed frontmatter"}
    
    fm_text, body = parts[1], parts[2]
    
    # Parse frontmatter (simple YAML-like parsing)
    fm = {}
    for line in fm_text.strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            fm[key] = val
    
    # Check for issues
    issues = []
    
    # 1. Check needs_review
    needs_review = fm.get("needs_review", "").lower() == "true"
    
    # 2. Check Chinese translations
    has_name_zh = bool(fm.get("name_zh"))
    has_desc_zh = bool(fm.get("description_zh"))
    if not has_name_zh:
        issues.append("missing name_zh")
    if not has_desc_zh:
        issues.append("missing description_zh")
    
    # 3. Check tags
    tags_raw = fm.get("tags", "[]")
    if "needs-tagging" in tags_raw:
        issues.append("placeholder tags")
    
    # 4. Check H1 sections
    h1_sections = re.findall(r"^# (.+)$", body, re.MULTILINE)
    required_sections = ["When to use", "When NOT to use", "Example", "Prompt"]
    missing_sections = [s for s in required_sections if s not in h1_sections]
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
    category = fm.get("category", "")
    if category == "uncategorized":
        issues.append("uncategorized")
    
    # 8. Check platforms
    platforms = fm.get("platforms", "[]")
    
    return {
        "slug": slug,
        "name": fm.get("name", ""),
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

def main():
    """Audit all skills."""
    skills = []
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
    uncategorized = sum(1 for s in skills if s.get("category") == "uncategorized")
    
    print(f"=== SKILL AUDIT SUMMARY ===")
    print(f"Total skills: {total}")
    print(f"Needs review: {needs_review}")
    print(f"Missing Chinese: {missing_zh}")
    print(f"Placeholder tags: {placeholder_tags}")
    print(f"Missing sections: {missing_sections}")
    print(f"Short body (<20 lines): {short_body}")
    print(f"No code examples: {no_code}")
    print(f"Uncategorized: {uncategorized}")
    print()
    
    # Category distribution
    categories = defaultdict(list)
    for s in skills:
        if not s.get("error"):
            categories[s.get("category", "unknown")].append(s["slug"])
    
    print(f"=== CATEGORY DISTRIBUTION ===")
    for cat, slugs in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"{cat:30s} {len(slugs):3d}")
    print()
    
    # Skills with most issues
    print(f"=== SKILLS WITH MOST ISSUES ===")
    sorted_skills = sorted(skills, key=lambda s: -s.get("issue_count", 0))
    for s in sorted_skills[:20]:
        if s.get("issue_count", 0) > 0:
            print(f"{s['slug']:40s} {s['issue_count']:2d} issues: {', '.join(s['issues'][:3])}")
    print()
    
    # Save full audit
    with open("/tmp/skill-audit.json", "w") as f:
        json.dump(skills, f, indent=2)
    print(f"Full audit saved to /tmp/skill-audit.json")

if __name__ == "__main__":
    main()
