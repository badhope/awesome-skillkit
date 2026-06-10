#!/usr/bin/env python3
"""Fetch a skill file from a GitHub repo into the local vault.

Two modes:

  1. Single skill, CLI args:

       python scripts/fetch-skill.py \\
           --source anthropics/anthropic-skills \\
           --ref main \\
           --path skills/pdf/SKILL.md \\
           --out skills/pdf-summarizer/SKILL.md

  2. Batch from a JSON list:

       python scripts/fetch-skill.py \\
           --all \\
           --sources scripts/sources.json

     The JSON file is a list of objects with the same fields as the
     single CLI mode (plus an optional `slug` for the output path).

How fetching works
------------------

We hit `https://raw.githubusercontent.com/<source>/<ref>/<path>`.
This is plain HTTPS, no auth needed for public repos. We do NOT
clone the upstream repo and we do NOT preserve a git remote —
the file lands in your local vault and that's it. If upstream
goes away tomorrow, your local copy is unaffected.

We always fetch a single file (not a directory). For multi-file
skills (assets, helpers) do one fetch per file, or use the batch
mode with a list.

Exit codes:

  0  all fetches succeeded
  1  any fetch failed (HTTP error, 404, parse error)
  2  invalid arguments
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
SOURCE_MD = REPO / "SOURCE.md"
DEFAULT_REF = "main"

UA = "ai-skill-fetcher/1.0 (+https://github.com/badhope/AI-SKILL)"
TIMEOUT_S = 20
WORKERS = 6


def _rel(p: Path) -> str:
    """Show a path relative to the repo if possible, else as-is."""
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def raw_url(source: str, ref: str, path: str) -> str:
    """Build a raw.githubusercontent.com URL.

    `source` is "owner/repo". `path` is the in-repo file path.
    We strip a leading slash so callers can pass either form.
    """
    return f"https://raw.githubusercontent.com/{source}/{ref}/{path.lstrip('/')}"


def http_get(url: str) -> tuple[bytes, str]:
    """GET a URL, return (body, final_url). Raise on non-2xx."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return r.read(), r.geturl()


def fetch_one(
    spec: dict, *, overwrite: bool = False, dry_run: bool = False
) -> tuple[str, str, str]:
    """Fetch one file. Returns (slug, status, detail).

    `status` is one of: ok, exists, missing, http_error, bad_args.
    `detail` is a one-line explanation.
    """
    source = spec.get("source") or ""
    ref = spec.get("ref") or DEFAULT_REF
    path = spec.get("path") or ""
    out_rel = spec.get("out") or ""

    if not source or not path or not out_rel:
        return ("?", "bad_args", "source/path/out all required")

    out_path = (REPO / out_rel) if not Path(out_rel).is_absolute() else Path(out_rel)
    if out_path.exists() and not overwrite:
        slug = out_path.parent.name if out_path.name == "SKILL.md" else out_path.stem
        return (slug, "exists", f"refusing to overwrite {_rel(out_path)}")

    if dry_run:
        slug = out_path.parent.name if out_path.name == "SKILL.md" else out_path.stem
        return (slug, "ok", f"(dry-run) would fetch {raw_url(source, ref, path)}")

    url = raw_url(source, ref, path)
    try:
        body, _ = http_get(url)
    except urllib.error.HTTPError as e:
        return ("?", "http_error", f"{e.code} {url}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return ("?", "http_error", f"{type(e).__name__}: {e} {url}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(body)

    slug = out_path.parent.name if out_path.name == "SKILL.md" else out_path.stem
    return (slug, "ok", f"wrote {len(body):>6} B to {_rel(out_path)}")


def load_sources(path: Path) -> list[dict]:
    """Load a fetch manifest.

    Two shapes are accepted:

      1. A top-level list of spec dicts.
      2. A dict with an `items` key (preferred) — the rest of the
         keys are treated as metadata and ignored. This is what
         scripts/sources.json uses, so we can keep `_meta` /
         `_status` / etc. alongside the data without confusing
         the fetcher.

    Specs with `skip: true` are filtered out. The skip + reason
    stay in the JSON for audit purposes.
    """
    with path.open() as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        raise SystemExit(f"{path}: items must be a list, got {type(data).__name__}")
    out = []
    for s in data:
        if not isinstance(s, dict):
            continue
        if s.get("skip"):
            continue
        out.append(s)
    return out


def write_source_md(records: list[dict], path: Path) -> None:
    """Append (or merge) a dated section to SOURCE.md for the run.

    We log ALL statuses, not just `ok` — failed/skipped entries
    matter for audit ("did we try this? did it work?").

    We dedupe per-day: if today's section header is already
    present, we replace the body under it instead of appending a
    second `## YYYY-MM-DD` block.
    """
    if not records:
        return
    today = dt.date.today().isoformat()
    header = f"## {today} — fetch-skill.py batch"

    # Group by status
    by_status: dict[str, list[dict]] = {}
    for r in records:
        by_status.setdefault(r["status"], []).append(r)

    body_lines: list[str] = [""]
    for status in ("ok", "exists", "http_error", "bad_args", "missing"):
        rows = by_status.get(status, [])
        if not rows:
            continue
        body_lines.append(f"### {status} ({len(rows)})")
        for r in rows[:50]:
            src = r["spec"].get("source", "?")
            body_lines.append(f"- `{src}` — {r['detail']}")
        if len(rows) > 50:
            body_lines.append(f"- ... and {len(rows) - 50} more")
        body_lines.append("")
    body = "\n".join(body_lines).rstrip() + "\n"

    if not path.exists():
        path.write_text(f"# fetch-skill.py log\n\n{header}\n{body}", encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    marker = f"{header}\n"
    if marker in existing:
        # Replace from header to next "## " or EOF, then re-append
        # the new body under the same header.
        idx = existing.index(marker) + len(marker)
        rest = existing[idx:]
        # find the next "## " at line start
        nxt = rest.find("\n## ")
        if nxt == -1:
            existing = existing[:idx] + body
        else:
            existing = existing[:idx] + body + rest[nxt + 1:]
    else:
        existing = existing.rstrip() + "\n\n" + header + "\n" + body
    path.write_text(existing, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--all", action="store_true",
                     help="use --sources JSON file")
    src.add_argument("--source", metavar="OWNER/REPO",
                     help="GitHub source repo (for single-fetch mode)")

    ap.add_argument("--ref", default=DEFAULT_REF,
                    help=f"git ref to fetch from (default: {DEFAULT_REF})")
    ap.add_argument("--path", help="in-repo path to the file (single mode)")
    ap.add_argument("--out", help="local output path, relative to repo root (single mode)")
    ap.add_argument("--sources", type=Path,
                    help="JSON file with a list of {source, ref, path, out} dicts")
    ap.add_argument("--overwrite", action="store_true",
                    help="overwrite existing output files")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen, write nothing")
    ap.add_argument("--workers", type=int, default=WORKERS,
                    help=f"concurrent fetches (default: {WORKERS})")
    ap.add_argument("--log-source", action="store_true",
                    help="append a section to SOURCE.md summarising what was fetched")
    args = ap.parse_args()

    specs: list[dict] = []
    if args.all:
        if not args.sources:
            print("--all requires --sources <path.json>", file=sys.stderr)
            return 2
        if not args.sources.exists():
            print(f"sources file not found: {args.sources}", file=sys.stderr)
            return 2
        specs = load_sources(args.sources)
    else:
        if not (args.path and args.out):
            print("--source requires both --path and --out", file=sys.stderr)
            return 2
        specs = [{
            "source": args.source,
            "ref": args.ref,
            "path": args.path,
            "out": args.out,
        }]

    if not specs:
        print("nothing to do: empty spec list", file=sys.stderr)
        return 0

    print(f"Fetching {len(specs)} file(s) with {args.workers} workers "
          f"{'(dry-run)' if args.dry_run else ''}\n")

    records: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(fetch_one, s, overwrite=args.overwrite, dry_run=args.dry_run): s
                for s in specs}
        for fut in as_completed(futs):
            spec = futs[fut]
            slug, status, detail = fut.result()
            records.append({"slug": slug, "status": status, "detail": detail, "spec": spec})

    by_status: dict[str, list[dict]] = {}
    for r in records:
        by_status.setdefault(r["status"], []).append(r)

    for status in ("ok", "exists", "bad_args", "http_error", "missing"):
        rows = by_status.get(status, [])
        if not rows:
            continue
        print(f"## {status} ({len(rows)})")
        for r in rows[:40]:
            print(f"  {r['slug']:30s}  {r['detail']}")
        if len(rows) > 40:
            print(f"  ... and {len(rows) - 40} more")
        print()

    failed = sum(len(v) for k, v in by_status.items() if k not in ("ok", "exists"))
    print(f"== {len(records) - failed} ok / {failed} failed / {len(records)} total ==")

    if args.log_source and not args.dry_run:
        write_source_md(records, SOURCE_MD)
        print(f"appended provenance to {_rel(SOURCE_MD)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
