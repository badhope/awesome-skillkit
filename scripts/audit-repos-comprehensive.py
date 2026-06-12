#!/usr/bin/env python3
"""
Comprehensive repo auditor for large-scale skill discovery.

This script audits 100+ repos to discover skill-shaped files for mass conversion.
It supports tiered auditing, priority levels, and generates detailed reports.

Usage:
    python scripts/audit-repos-comprehensive.py --manifest scripts/audit-manifest.json
    python scripts/audit-repos-comprehensive.py --tier tier1 --priority critical
    python scripts/audit-repos-comprehensive.py --category framework
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "scripts" / "audit-manifest.json"
DEFAULT_OUTPUT = REPO / "scripts" / "audit-report-comprehensive.json"

UA = "ai-skill-auditor/1.0 (+https://github.com/badhope/AI-SKILL)"
TIMEOUT_S = 30
WORKERS = 8

# Skill-shaped file patterns
SKILL_PATTERNS = (
    "SKILL.md", "AGENT.md", "PROMPT.md", "INSTRUCTIONS.md",
    "skill.md", "agent.md", "prompt.md",
)

# High-value directories
HIGH_VALUE_DIRS = (
    "skills/", "agents/", "prompts/", "examples/", "cookbook/",
    "cookbooks/", "docs/", "tutorials/", "guides/",
)


def api_url(source: str, ref: str) -> str:
    """Build GitHub API URL for repo tree."""
    return f"https://api.github.com/repos/{source}/git/trees/{ref}?recursive=1"


def fetch_tree(source: str, ref: str) -> tuple[list[str] | None, str]:
    """Fetch repo tree from GitHub API.
    
    Returns:
        (list_of_paths, status) where status is one of:
        ok, http_error, network_error, rate_limit
    """
    try:
        req = urllib.request.Request(
            api_url(source, ref),
            headers={
                "User-Agent": UA,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 403 and "rate limit" in str(e.read()).lower():
            return None, "rate_limit"
        return None, f"http_error:{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"network_error:{type(e).__name__}"
    
    if data.get("truncated"):
        return None, "truncated"
    
    paths = [
        item["path"] 
        for item in data.get("tree", []) 
        if item.get("type") == "blob"
    ]
    return paths, "ok"


def categorize_repo(paths: list[str]) -> dict[str, Any]:
    """Categorize repo content and find skill-shaped files.
    
    Returns dict with:
        - skill_shaped: list of skill-shaped file paths
        - high_value: list of files in high-value directories
        - total_files: total file count
        - code_files: count of code files
        - skill_dirs: unique directories containing skills
    """
    out = {
        "skill_shaped": [],
        "high_value": [],
        "total_files": len(paths),
        "code_files": 0,
        "skill_dirs": set(),
    }
    
    for p in paths:
        base = p.rsplit("/", 1)[-1]
        
        # Check for skill-shaped files
        if base in SKILL_PATTERNS:
            out["skill_shaped"].append(p)
            # Extract skill directory
            skill_dir = "/".join(p.split("/")[:-1])
            out["skill_dirs"].add(skill_dir)
        
        # Check for high-value directories
        if any(p.startswith(d) for d in HIGH_VALUE_DIRS):
            out["high_value"].append(p)
        
        # Count code files
        if p.endswith((".py", ".ts", ".js", ".go", ".rs", ".java", ".cpp", ".c")):
            out["code_files"] += 1
    
    # Convert set to sorted list for JSON serialization
    out["skill_dirs"] = sorted(out["skill_dirs"])
    
    return out


def audit_one(entry: dict) -> dict:
    """Audit a single repo entry.
    
    Returns dict with:
        - source: repo name
        - ref: branch/ref
        - tier: tier level
        - priority: priority level
        - category: category
        - status: audit status
        - skill_count: number of skill-shaped files found
        - details: categorization details
    """
    source = entry["source"]
    ref = entry.get("ref", "main")
    
    print(f"  Auditing {source}...", file=sys.stderr)
    
    paths, status = fetch_tree(source, ref)
    
    if paths is None:
        return {
            "source": source,
            "ref": ref,
            "tier": entry.get("tier", "unknown"),
            "priority": entry.get("priority", "unknown"),
            "category": entry.get("category", "unknown"),
            "status": status,
            "skill_count": 0,
            "details": {},
            "notes": entry.get("notes", ""),
        }
    
    details = categorize_repo(paths)
    
    return {
        "source": source,
        "ref": ref,
        "tier": entry.get("tier", "unknown"),
        "priority": entry.get("priority", "unknown"),
        "category": entry.get("category", "unknown"),
        "status": "ok",
        "skill_count": len(details["skill_shaped"]),
        "details": details,
        "notes": entry.get("notes", ""),
    }


def load_manifest(manifest_path: Path) -> list[dict]:
    """Load audit manifest from JSON file."""
    with manifest_path.open() as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        return data.get("items", [])
    return data


def filter_entries(
    entries: list[dict],
    tier: str | None = None,
    priority: str | None = None,
    category: str | None = None,
) -> list[dict]:
    """Filter entries by tier, priority, or category."""
    filtered = entries
    
    if tier:
        filtered = [e for e in filtered if e.get("tier") == tier]
    
    if priority:
        filtered = [e for e in filtered if e.get("priority") == priority]
    
    if category:
        filtered = [e for e in filtered if e.get("category") == category]
    
    return filtered


def generate_report(results: list[dict], manifest_meta: dict) -> dict:
    """Generate comprehensive audit report.
    
    Returns dict with:
        - meta: report metadata
        - summary: high-level statistics
        - by_tier: breakdown by tier
        - by_priority: breakdown by priority
        - by_category: breakdown by category
        - top_repos: repos with most skills
        - skill_shaped_files: all discovered skill-shaped files
        - errors: failed audits
    """
    # Calculate summary statistics
    total = len(results)
    successful = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]
    
    total_skills = sum(r["skill_count"] for r in successful)
    
    # Breakdown by tier
    by_tier = {}
    for r in results:
        tier = r.get("tier", "unknown")
        if tier not in by_tier:
            by_tier[tier] = {"count": 0, "skills": 0, "errors": 0}
        by_tier[tier]["count"] += 1
        if r["status"] == "ok":
            by_tier[tier]["skills"] += r["skill_count"]
        else:
            by_tier[tier]["errors"] += 1
    
    # Breakdown by priority
    by_priority = {}
    for r in results:
        priority = r.get("priority", "unknown")
        if priority not in by_priority:
            by_priority[priority] = {"count": 0, "skills": 0, "errors": 0}
        by_priority[priority]["count"] += 1
        if r["status"] == "ok":
            by_priority[priority]["skills"] += r["skill_count"]
        else:
            by_priority[priority]["errors"] += 1
    
    # Breakdown by category
    by_category = {}
    for r in results:
        category = r.get("category", "unknown")
        if category not in by_category:
            by_category[category] = {"count": 0, "skills": 0, "errors": 0}
        by_category[category]["count"] += 1
        if r["status"] == "ok":
            by_category[category]["skills"] += r["skill_count"]
        else:
            by_category[category]["errors"] += 1
    
    # Top repos by skill count
    top_repos = sorted(
        [r for r in successful if r["skill_count"] > 0],
        key=lambda x: x["skill_count"],
        reverse=True,
    )[:50]
    
    # All skill-shaped files
    skill_shaped_files = []
    for r in successful:
        for path in r["details"].get("skill_shaped", []):
            skill_shaped_files.append({
                "source": r["source"],
                "ref": r["ref"],
                "path": path,
                "tier": r["tier"],
                "priority": r["priority"],
                "category": r["category"],
            })
    
    return {
        "meta": {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_repos": total,
            "successful": len(successful),
            "failed": len(failed),
            "total_skills": total_skills,
            "manifest_meta": manifest_meta,
        },
        "summary": {
            "total_repos": total,
            "successful": len(successful),
            "failed": len(failed),
            "total_skills": total_skills,
            "avg_skills_per_repo": total_skills / len(successful) if successful else 0,
        },
        "by_tier": by_tier,
        "by_priority": by_priority,
        "by_category": by_category,
        "top_repos": top_repos,
        "skill_shaped_files": skill_shaped_files,
        "errors": failed,
    }


def print_summary(report: dict) -> None:
    """Print human-readable summary to stdout."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE AUDIT REPORT")
    print("=" * 80)
    
    summary = report["summary"]
    print(f"\nTotal repos: {summary['total_repos']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total skills discovered: {summary['total_skills']}")
    print(f"Average skills per repo: {summary['avg_skills_per_repo']:.1f}")
    
    print("\n" + "-" * 80)
    print("BREAKDOWN BY TIER")
    print("-" * 80)
    for tier, stats in sorted(report["by_tier"].items()):
        print(f"\n{tier}:")
        print(f"  Repos: {stats['count']}")
        print(f"  Skills: {stats['skills']}")
        print(f"  Errors: {stats['errors']}")
    
    print("\n" + "-" * 80)
    print("BREAKDOWN BY PRIORITY")
    print("-" * 80)
    for priority, stats in sorted(report["by_priority"].items()):
        print(f"\n{priority}:")
        print(f"  Repos: {stats['count']}")
        print(f"  Skills: {stats['skills']}")
        print(f"  Errors: {stats['errors']}")
    
    print("\n" + "-" * 80)
    print("TOP 20 REPOS BY SKILL COUNT")
    print("-" * 80)
    for i, repo in enumerate(report["top_repos"][:20], 1):
        print(f"{i:2d}. {repo['source']:40s} {repo['skill_count']:4d} skills")
    
    if report["errors"]:
        print("\n" + "-" * 80)
        print(f"ERRORS ({len(report['errors'])})")
        print("-" * 80)
        for err in report["errors"][:20]:
            print(f"  {err['source']:40s} {err['status']}")
        if len(report["errors"]) > 20:
            print(f"  ... and {len(report['errors']) - 20} more")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Path to audit manifest (default: {DEFAULT_MANIFEST})",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Path to output report (default: {DEFAULT_OUTPUT})",
    )
    ap.add_argument(
        "--tier",
        choices=["tier1", "tier2", "tier3"],
        help="Filter by tier level",
    )
    ap.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        help="Filter by priority level",
    )
    ap.add_argument(
        "--category",
        help="Filter by category",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=WORKERS,
        help=f"Number of concurrent workers (default: {WORKERS})",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary output",
    )
    args = ap.parse_args()
    
    # Load manifest
    if not args.manifest.exists():
        print(f"Error: manifest not found: {args.manifest}", file=sys.stderr)
        return 2
    
    entries = load_manifest(args.manifest)
    manifest_data = json.loads(args.manifest.read_text())
    manifest_meta = manifest_data.get("_meta", {})
    
    # Filter entries
    entries = filter_entries(entries, args.tier, args.priority, args.category)
    
    if not entries:
        print("Error: no entries match the filters", file=sys.stderr)
        return 2
    
    print(f"Auditing {len(entries)} repos with {args.workers} workers...", file=sys.stderr)
    
    # Audit repos
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit_one, entry): entry for entry in entries}
        for future in as_completed(futures):
            results.append(future.result())
    
    # Generate report
    report = generate_report(results, manifest_meta)
    
    # Write report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport written to: {args.output}", file=sys.stderr)
    
    # Print summary
    if not args.quiet:
        print_summary(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
