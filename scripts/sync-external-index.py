#!/usr/bin/env python3
"""Sync external-index/skills.yaml → frontend/public/external-repos.json.

The YAML is the source of truth for the 928-repo external index.
This script projects it to the JSON the frontend fetches at runtime,
keeping only the fields the UI needs and adding derived fields
(domain label, vendor-type label, star-tier) for easier rendering.

Run this after editing skills.yaml, before building the frontend.
validate-skill.py also calls this automatically.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml required: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
SKILLS_YAML = REPO / "external-index" / "skills.yaml"
OUTPUT_JSON = REPO / "frontend" / "public" / "external-repos.json"

# Domain → localized labels
DOMAIN_LABELS: dict[str, dict[str, str]] = {
    "infrastructure":      {"en": "Infrastructure & Serving",   "zh": "基础设施与部署"},
    "agents":              {"en": "Agent & Tooling",            "zh": "智能体与工具"},
    "rag-knowledge":       {"en": "RAG & Knowledge",            "zh": "RAG 与知识"},
    "evaluation-safety":   {"en": "Evaluation & Safety",        "zh": "评估与安全"},
    "dev-tools":           {"en": "Development Tools",          "zh": "开发工具"},
    "applications":        {"en": "Applications",               "zh": "应用"},
    "multimodal":          {"en": "Multimodal",                 "zh": "多模态"},
    "content-docs":        {"en": "Content & Docs",             "zh": "内容与文档"},
    "research-training":   {"en": "Research & Training",        "zh": "研究与训练"},
}

# Vendor type → localized labels
VENDOR_TYPE_LABELS: dict[str, dict[str, str]] = {
    "big-corp":           {"en": "Big Corp / Official",   "zh": "大厂 / 官方"},
    "popular-community":  {"en": "Popular Community",     "zh": "热门社区"},
    "community":          {"en": "Community",             "zh": "社区"},
    "indie":              {"en": "Indie / Personal",      "zh": "个人项目"},
}


def star_tier(stars: int) -> str:
    """Bucket stars into tiers for filtering."""
    if stars >= 100000: return "100k+"
    if stars >= 50000:  return "50k+"
    if stars >= 10000:  return "10k+"
    if stars >= 1000:   return "1k+"
    if stars > 0:       return "<1k"
    return "none"


def main() -> int:
    if not SKILLS_YAML.exists():
        print(f"  warn   {SKILLS_YAML.relative_to(REPO)} not found, skipping external index sync", file=sys.stderr)
        return 0

    yaml = YAML(typ="safe")
    with SKILLS_YAML.open(encoding="utf-8") as f:
        data = yaml.load(f)

    skills = data.get("skills", []) if data else []

    repos: list[dict[str, Any]] = []
    for s in skills:
        stars = s.get("stars") or 0
        # Extract vendor name from source (org/repo format)
        source = s.get("source") or ""
        vendor = source.split("/")[0] if "/" in source else s.get("title", "")
        # Normalize: capitalize known orgs
        vendor = vendor.replace("-", " ").replace("_", " ").title()

        repos.append({
            "slug": s.get("slug", ""),
            "title": s.get("title", ""),
            "title_zh": s.get("title_zh") or s.get("title", ""),
            "vendor": vendor,
            "repo": source,
            "url": s.get("source_url", ""),
            "category": s.get("category", ""),
            "domain": s.get("domain", "applications"),
            "vendor_type": s.get("vendor_type", "community"),
            "tags": s.get("tags") or [],
            "skills": s.get("skills") or [],
            "summary_en": s.get("summary", ""),
            "summary_zh": s.get("summary_zh") or s.get("summary", ""),
            "stars": stars,
            "star_tier": star_tier(stars),
            "license": s.get("license", ""),
            "archived": bool(s.get("archived")),
            "pushed_at": s.get("pushed_at") or "",
            "subgroup": s.get("subgroup") or "",
        })

    # Sort by stars descending (most popular first)
    repos.sort(key=lambda r: r["stars"], reverse=True)

    output = {
        "repos": repos,
        "domains": DOMAIN_LABELS,
        "vendor_types": VENDOR_TYPE_LABELS,
        "total": len(repos),
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  wrote {OUTPUT_JSON.relative_to(REPO)} ({len(repos)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
