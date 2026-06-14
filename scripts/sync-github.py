#!/usr/bin/env python3
"""Sync stars / license / pushed_at from the GitHub API into skills.yaml.

For each skill with a `source` of the form `owner/repo`, GET
/repos/{owner}/{repo} and update the corresponding fields. Non-GitHub
sources are skipped.

The skills.yaml this writes to is the external link index
(`external-index/skills.yaml`), not the local skill vault
(`skills/`). Local skills live under `skills/<slug>/SKILL.md`
and are out of scope for this script.

Rate limits: 60 req/h unauthenticated, 5000/h with GITHUB_TOKEN.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml not installed. Run: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_YAML = REPO_ROOT / "external-index" / "skills.yaml"
API_BASE = "https://api.github.com"

DEFAULT_WORKERS_AUTH = 12
DEFAULT_WORKERS_ANON = 1


def _github_get(path: str, token: str | None) -> dict[str, Any]:
    req = urllib.request.Request(API_BASE + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "AI-SKILL-sync/1.0")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"_404": True}
        if e.code == 403:
            reset = e.headers.get("X-RateLimit-Reset", "?")
            remaining = e.headers.get("X-RateLimit-Remaining", "?")
            print(f"  ! 403 rate-limited, remaining={remaining}, reset at epoch {reset}",
                  file=sys.stderr)
        raise


def _parse_source(source: str) -> tuple[str, str] | None:
    """Parse owner/repo from source string with security validation.
    
    Prevents command injection by:
    - Rejecting sources with shell metacharacters
    - Only allowing alphanumeric and hyphen in owner
    - Only allowing alphanumeric, hyphen, dot, underscore in repo
    - Rejecting sources with path separators or special chars
    """
    if not source or source.count("/") != 1:
        return None
    owner, repo = source.split("/", 1)
    # Reject empty or whitespace-only values
    if not owner or not repo or " " in owner or " " in repo:
        return None
    # Security: reject shell metacharacters and path separators
    dangerous_chars = set('`$|;&<>(){}[]!#~*?\\\'"\n\r\t')
    if any(c in dangerous_chars for c in owner + repo):
        return None
    # Owner: only alphanumeric and hyphen (GitHub username rules)
    if not all(c.isalnum() or c == "-" for c in owner):
        return None
    # Repo: alphanumeric, hyphen, dot, underscore (GitHub repo rules)
    if not all(c.isalnum() or c in "-._" for c in repo):
        return None
    # Additional check: reject if it looks like a path traversal
    if ".." in owner or ".." in repo or "/" in owner or "/" in repo:
        return None
    return owner, repo


def _fetch_one(slug: str, source: str, token: str | None) -> dict[str, Any]:
    parsed = _parse_source(source)
    if not parsed:
        return {"slug": slug, "ok": False, "reason": f"non-github source: {source!r}"}
    owner, repo = parsed
    try:
        payload = _github_get(f"/repos/{owner}/{repo}", token)
    except Exception as e:
        return {"slug": slug, "ok": False, "reason": f"HTTP error: {e}"}
    if payload.get("_404"):
        return {"slug": slug, "ok": False, "reason": "404 not found / private / renamed"}
    return {
        "slug": slug,
        "ok": True,
        "stars": int(payload.get("stargazers_count", 0) or 0),
        "license": _normalise_license(payload.get("license") or {}),
        "pushed_at": (payload.get("pushed_at") or "")[:10],
        "archived": bool(payload.get("archived")),
    }


def _normalise_license(lic: dict[str, Any]) -> str:
    spdx = lic.get("spdx_id") or ""
    if spdx in ("NOASSERTION", "NONE"):
        return ""
    return spdx


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Don't write back to skills.yaml")
    ap.add_argument("--workers", type=int, default=0, help="Concurrency (default: 12 with token, 1 without)")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("WARNING: no GITHUB_TOKEN, falling back to 60 req/h limit (no parallelism)",
              file=sys.stderr)
        workers = DEFAULT_WORKERS_ANON
    else:
        workers = args.workers or DEFAULT_WORKERS_AUTH

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(SKILLS_YAML) as f:
        data = yaml.load(f)

    skills = data.get("skills", [])
    print(f"Loaded {len(skills)} skills from {SKILLS_YAML.relative_to(REPO_ROOT)}")
    print(f"Workers: {workers}, auth: {'yes' if token else 'no'}")

    started = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(_fetch_one, s.get("slug", "?"), s.get("source", ""), token): s
                for s in skills}
        results = [f.result() for f in as_completed(futs)]

    changes: list[tuple[str, dict[str, Any]]] = []
    skipped: list[tuple[str, str]] = []
    for r in results:
        if not r["ok"]:
            skipped.append((r["slug"], r.get("reason", "?")))
            continue
        s = next((x for x in skills if x.get("slug") == r["slug"]), None)
        if s is None:
            continue
        old_stars = s.get("stars", 0) or 0
        old_license = s.get("license") or ""
        old_pushed = s.get("pushed_at") or ""
        local: dict[str, Any] = {}
        if r["stars"] != old_stars:
            local["stars"] = (old_stars, r["stars"])
        if r["license"] and r["license"] != old_license:
            local["license"] = (old_license, r["license"])
        if r["pushed_at"] and r["pushed_at"] != old_pushed:
            local["pushed_at"] = (old_pushed, r["pushed_at"])
        if r["archived"] and not s.get("archived"):
            local["archived"] = (False, True)
        if local:
            changes.append((r["slug"], local))
            if not args.dry_run:
                s["stars"] = r["stars"]
                if r["license"]:
                    s["license"] = r["license"]
                if r["pushed_at"]:
                    s["pushed_at"] = r["pushed_at"]
                if r["archived"]:
                    s["archived"] = True

    elapsed = time.time() - started
    print(f"Done in {elapsed:.1f}s")
    print(f"  fetched: {len(results) - len(skipped)}")
    print(f"  changed: {len(changes)}")
    print(f"  skipped: {len(skipped)}")

    if changes:
        print("\n=== Changes ===")
        for slug, c in changes[:20]:
            parts = ", ".join(f"{k}: {old} → {new}" for k, (old, new) in c.items())
            print(f"  {slug}: {parts}")
        if len(changes) > 20:
            print(f"  ... and {len(changes) - 20} more")

    if skipped:
        print("\n=== Skipped ===")
        for slug, reason in skipped[:10]:
            print(f"  {slug}: {reason}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")

    if args.dry_run:
        print("\n(dry-run, not writing back)")
        return 0

    if changes:
        with open(SKILLS_YAML, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"\nWrote updates to {SKILLS_YAML.relative_to(REPO_ROOT)}")
    else:
        print("\nNo changes — skills.yaml is up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
