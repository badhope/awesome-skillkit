#!/usr/bin/env python3
"""Health check: ping every source_url in external-index/skills.yaml.

Reports 4xx/5xx, timeouts, and DNS failures. Writes a summary to
external-index/health.json for trend tracking.

This only checks the external link index, not the local skill
vault. Local skills don't have remote URLs to ping.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
INDEX_YAML = REPO / "external-index" / "skills.yaml"
HEALTH_JSON = REPO / "external-index" / "health.json"

UA = "ai-skill-link-checker/1.0"
TIMEOUT_S = 8
WORKERS = 8
RETRY_BACKOFF_S = (1.0, 3.0)


def _classify(code: int) -> tuple[str, int, str]:
    if 200 <= code < 300:
        return ("ok", code, "ok")
    if 300 <= code < 400:
        return ("redirect", code, "redirect")
    if 400 <= code < 500:
        return (f"client_error {code}", code, "client_error")
    return (f"server_error {code}", code, "server_error")


def _err(e: Exception) -> tuple[str, int, str]:
    msg = str(e)[:120] or type(e).__name__
    return (f"error: {msg}", 0, "error")


def _validate_url(url: str) -> bool:
    """Validate URL to prevent path traversal and SSRF attacks.
    
    Security checks:
    - Only allow http/https schemes
    - Reject file://, ftp://, and other dangerous schemes
    - Reject localhost and loopback addresses (SSRF prevention)
    - Allow private IP ranges (192.168.x, 10.x, 172.x) for internal Git repos
    - Reject URLs with path traversal patterns
    """
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        # Only allow http/https
        if parsed.scheme not in ("http", "https"):
            return False
        # Reject localhost and loopback (SSRF prevention)
        # Allow private IPs (192.168.x, 10.x, 172.x) for internal Git repos
        hostname = parsed.hostname or ""
        dangerous_hosts = ("localhost", "127.0.0.1", "0.0.0.0", "::1")
        if hostname in dangerous_hosts:
            return False
        # Reject path traversal patterns
        if ".." in parsed.path or ".." in parsed.query:
            return False
        return True
    except Exception:
        return False


def head_or_get(url: str) -> tuple[str, int, str]:
    """GET a URL with a small Range, retrying transient failures."""
    # Security: validate URL before making request
    if not _validate_url(url):
        return ("error: invalid or unsafe URL", 0, "error")
    
    last_exc: Exception | None = None
    for attempt in range(1 + len(RETRY_BACKOFF_S)):
        req = urllib.request.Request(url, method="GET", headers={
            "User-Agent": UA,
            "Range": "bytes=0-1023",
        })
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                return _classify(r.getcode())
        except urllib.error.HTTPError as e:
            if e.code in (405, 403):
                try:
                    req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                    with urllib.request.urlopen(req2, timeout=TIMEOUT_S) as r2:
                        return _classify(r2.getcode())
                except urllib.error.HTTPError as e2:
                    return _classify(e2.code)
                except Exception as e2:
                    last_exc = e2
            else:
                return _classify(e.code)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_exc = e
        except Exception as e:
            last_exc = e
        if attempt < len(RETRY_BACKOFF_S):
            time.sleep(RETRY_BACKOFF_S[attempt])
    return _err(last_exc) if last_exc else ("error: unknown", 0, "error")


def load_index(path: Path) -> list[dict[str, Any]]:
    import yaml
    with path.open() as f:
        data = yaml.safe_load(f)
    return data.get("skills", []) or []


def collect_urls(skills: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [(s.get("slug", "?"), s["source_url"])
            for s in skills if s.get("source_url")]


def scan(pairs: list[tuple[str, str]]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(head_or_get, url): (slug, url) for slug, url in pairs}
        for fut in as_completed(futs):
            slug, url = futs[fut]
            status_text, code, group = fut.result()
            results[slug] = {"url": url, "code": code, "group": group, "status": status_text}
    return results


def main() -> int:
    p = argparse.ArgumentParser(
        description="Health check: ping every source_url in external-index/skills.yaml.",
    )
    p.add_argument("--fail", action="store_true", help="exit 1 on any broken link")
    p.add_argument("--workers", type=int, default=WORKERS)
    args = p.parse_args()

    if not INDEX_YAML.exists():
        print(f"index not found at {INDEX_YAML}", file=sys.stderr)
        return 1

    try:
        import yaml
    except ImportError:
        print("PyYAML is required: pip install pyyaml", file=sys.stderr)
        return 2

    skills = load_index(INDEX_YAML)
    pairs = collect_urls(skills)
    print(f"Checking {len(pairs)} URLs from {INDEX_YAML.relative_to(REPO)} …")
    started = time.time()
    results = scan(pairs)
    elapsed = time.time() - started

    by_group: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "ok": [], "redirect": [], "client_error": [], "server_error": [], "error": []
    }
    for slug, info in results.items():
        by_group.setdefault(info["group"], []).append((slug, info))

    print(f"\nDone in {elapsed:.1f}s — {len(pairs)} URLs, {args.workers} workers\n")
    for group, rows in by_group.items():
        if not rows:
            continue
        print(f"## {group} ({len(rows)})")
        for slug, info in sorted(rows)[:30]:
            print(f"  [{info['code']:>3}] {slug:48s}  {info['url']}")
        if len(rows) > 30:
            print(f"  …and {len(rows) - 30} more")
        print()

    broken = sum(len(v) for k, v in by_group.items()
                 if k in ("client_error", "server_error", "error"))
    print(f"== {broken} broken / {len(pairs)} total ==")

    HEALTH_JSON.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_JSON.write_text(json.dumps({
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_s": round(elapsed, 2),
        "total": len(pairs),
        "broken": broken,
        "by_group": {k: len(v) for k, v in by_group.items()},
        "results": results,
    }, indent=2, ensure_ascii=False, sort_keys=True))
    print(f"\nWrote {HEALTH_JSON.relative_to(REPO)}")

    return 1 if (args.fail and broken) else 0


if __name__ == "__main__":
    sys.exit(main())
