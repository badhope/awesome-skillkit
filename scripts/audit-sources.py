#!/usr/bin/env python3
"""Probe each repo in sources.json for skill-shaped content.

For every entry, we ask the GitHub git/trees API for the repo's
default-branch tree (recursive), then look for files named
SKILL.md, AGENT.md, PROMPT.md, .prompt.yaml, etc. We log what
we find so the operator can decide which paths to add to
sources.json as real entries (vs. keeping them on `skip: true`).

We DO NOT modify sources.json — this is a read-only audit. The
operator reviews the output, decides which repos actually have
skill-shaped content, and adds the discovered paths as
non-skipped entries in a second pass.

Why we don't just mass-add every SKILL.md
-----------------------------------------
- Most of the 18 repos in sources.json are framework repos
  (langchain, autogen, llama_index, vector DBs) that don't have
  skill-shaped content at all — they have source code.
- A few (anthropic-cookbook, openai-cookbook) have recipe-style
  notebooks that COULD be turned into skills, but only some
  recipes are skill-shaped (single-purpose, agent-executable).
- Forcing 100+ "SKILL.md" files into the vault because they
  have the right name would dilute the catalog with stuff
  that doesn't fit the contract (one clear behaviour, one
  working example, one I/O spec).

The audit output is grouped by:
  - "found": at least one skill-shaped file in the tree
  - "code-only": the repo exists but is a code framework, not
    a skill library
  - "missing" / "http_error" / "timeout": couldn't reach the
    API for that repo (404, rate limit, network)
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "scripts" / "sources.json"
DEFAULT_REF = "main"
UA = "ai-skill-auditor/1.0 (+https://github.com/badhope/AI-SKILL)"
TIMEOUT_S = 20
WORKERS = 6

# Filename patterns we treat as "skill-shaped". Kept short — the
# point is to flag candidates, not validate them. The next pass
# (a human or extend-skill.py) decides if they're worth importing.
SKILL_PATTERNS = (
    "SKILL.md", "AGENT.md", "PROMPT.md", "INSTRUCTIONS.md",
    "skill.md", "agent.md",
)


def raw_url(source: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{source}/{ref}/{path.lstrip('/')}"


def api_url(source: str, ref: str) -> str:
    # GitHub's git/trees endpoint with recursive=1 returns the
    # full file tree of a ref. For most repos this is < 1MB.
    return f"https://api.github.com/repos/{source}/git/trees/{ref}?recursive=1"


def fetch_tree(source: str, ref: str) -> tuple[list[str] | None, str]:
    """Return (list_of_paths, status).

    `status` is one of: ok, http_error, network_error.
    On success, paths is a list of in-repo file paths.
    """
    try:
        req = urllib.request.Request(
            api_url(source, ref),
            headers={"User-Agent": UA, "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None, f"http_error: {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"network_error: {type(e).__name__}: {e}"
    if data.get("truncated"):
        # Repos with 100k+ files. We can't enumerate everything.
        # Surface this so the operator knows to fall back to a
        # targeted search.
        return None, "truncated: repo too large to enumerate"
    return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"], "ok"


def categorize(paths: list[str]) -> dict:
    """Bucket the repo's files into the kinds of content we care about."""
    out = {
        "skill_shaped": [],   # exact SKILL.md / AGENT.md / etc.
        "readme": None,       # top-level README.md
        "docs_dirs": [],      # paths under docs/, examples/, cookbooks/
        "code_files": 0,      # .py / .ts / .js count
        "total": len(paths),
    }
    for p in paths:
        base = p.rsplit("/", 1)[-1]
        if base in SKILL_PATTERNS:
            out["skill_shaped"].append(p)
        if p == "README.md":
            out["readme"] = p
        if p.startswith(("docs/", "docs\\", "examples/", "examples\\",
                         "cookbook/", "cookbooks/", "skills/", "prompts/")):
            out["docs_dirs"].append(p)
        if p.endswith((".py", ".ts", ".js", ".go", ".rs", ".java")):
            out["code_files"] += 1
    return out


def audit_one(entry: dict) -> dict:
    source = entry.get("source", "")
    ref = entry.get("ref") or DEFAULT_REF
    paths, status = fetch_tree(source, ref)
    if paths is None:
        return {"source": source, "ref": ref, "status": status, "category": "missing", "info": {}}
    info = categorize(paths)
    if info["skill_shaped"]:
        category = "found"
    elif info["code_files"] > info["total"] * 0.5:
        # More than half the repo is code → it's a framework
        category = "code-only"
    elif info["docs_dirs"]:
        category = "docs-heavy"
    else:
        category = "unknown"
    return {"source": source, "ref": ref, "status": status, "category": category, "info": info}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--sources", type=Path, default=SOURCES,
                    help=f"manifest to audit (default: {SOURCES})")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--out", type=Path,
                    help="write JSON report here (in addition to stdout)")
    args = ap.parse_args()

    if not args.sources.exists():
        print(f"sources file not found: {args.sources}", file=sys.stderr)
        return 2
    data = json.loads(args.sources.read_text())
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        print(f"{args.sources}: items must be a list", file=sys.stderr)
        return 2

    print(f"Auditing {len(data)} repos with {args.workers} workers...\n")
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(audit_one, e): e for e in data}
        for fut in as_completed(futs):
            results.append(fut.result())

    by_cat: dict[str, list[dict]] = {"found": [], "code-only": [], "docs-heavy": [], "missing": [], "unknown": []}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    # Print a compact report
    print(f"== {len(results)} repos audited ==\n")
    for cat in ("found", "docs-heavy", "code-only", "missing", "unknown"):
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        print(f"## {cat} ({len(rows)})")
        for r in rows:
            src = r["source"]
            info = r["info"]
            if cat == "found":
                sk = info.get("skill_shaped", [])
                print(f"  {src}  →  {len(sk)} skill-shaped file(s):")
                for p in sk[:8]:
                    print(f"     - {p}")
                if len(sk) > 8:
                    print(f"     - ... and {len(sk) - 8} more")
            elif cat == "docs-heavy":
                docs = info.get("docs_dirs", [])
                print(f"  {src}  →  {info['total']} files, {len(docs)} under docs/examples/cookbook/skills/prompts")
            elif cat == "code-only":
                print(f"  {src}  →  {info['total']} files, {info['code_files']} are code")
            else:
                print(f"  {src}  →  {r['status']}")
        print()

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"wrote report to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
