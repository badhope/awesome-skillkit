#!/usr/bin/env python3
"""Convert a raw .md into our standard SKILL.md format.

Three inputs are accepted:

  1. A single file:

       python scripts/convert-skill.py skills/foo/SKILL.md

  2. All skills under skills/:

       python scripts/convert-skill.py --all

  3. A list of files:

       python scripts/convert-skill.py skills/foo skills/bar/baz

What "convert" actually does
----------------------------

Most upstream skills are already roughly the right shape: a YAML
frontmatter + Markdown body. We do NOT rewrite the body. We only:

  - Read the existing frontmatter (if any)
  - Detect a few common upstream formats (Claude skills, OpenAI
    skills, Anthropic cookbook) and normalise the slug / category
    / source fields
  - Add `needs_review: true` whenever we had to guess or the
    source was in a non-standard format

We do NOT add a worked example, do NOT add "When NOT to use", do
NOT tighten the I/O contract — that's `extend-skill.py`'s job.
Keeping the two steps separate means you can review convert's
guesses in isolation, then run extend on top.

Idempotency: running convert twice on the same file is a no-op
the second time, unless `--overwrite` is set.
"""
from __future__ import annotations

import argparse
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

# Required keys we always emit (or accept unchanged). The schema
# (docs/schema.md) is the source of truth — this list is a
# conversion-time check, not an authority.
REQUIRED = {"slug", "name", "version", "description", "category",
            "tags", "inputs", "output", "author", "license",
            "created", "updated"}

# Heuristic: known upstream filename patterns → likely platform.
UPSTREAM_PLATFORM_HINTS = (
    ("anthropic", "claude"),
    ("claude", "claude"),
    ("openai", "codex"),
    ("codex", "codex"),
    ("cursor", "cursor"),
    ("continue", "continue"),
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _rel(p: Path) -> str:
    """Show a path relative to the repo if possible, else as-is."""
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    """Return (frontmatter, body, had_frontmatter).

    If there's no frontmatter, returns ({}, text, False).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, False
    yaml = YAML(typ="safe")
    try:
        fm = dict(yaml.load(m.group(1)) or {})
    except Exception as e:
        print(f"  ! frontmatter parse failed: {e}", file=sys.stderr)
        fm = {}
    return fm, m.group(2), True


def detect_platform(fm: dict, body: str) -> str | None:
    """Best-effort platform detection. Returns None if unclear."""
    blob = (fm.get("name", "") + " " + body[:500]).lower()
    for needle, plat in UPSTREAM_PLATFORM_HINTS:
        if needle in blob:
            return plat
    return None


def ensure_required(fm: dict, slug: str, today: str) -> tuple[dict, list[str]]:
    """Fill in any missing required fields with placeholders.

    Returns the (possibly-mutated) frontmatter and a list of
    `needs_review` reasons for fields we had to guess.
    """
    notes: list[str] = []
    if "slug" not in fm or not fm["slug"]:
        fm["slug"] = slug
        notes.append("slug guessed from directory")
    if "name" not in fm or not fm["name"]:
        fm["name"] = slug.replace("-", " ").title()
        notes.append("name guessed from slug")
    if "version" not in fm or not fm["version"]:
        fm["version"] = "0.1.0"
        notes.append("version defaulted to 0.1.0")
    if "description" not in fm or not fm["description"]:
        fm["description"] = "TODO: write a one-line description"
        notes.append("description placeholder — please rewrite")
    if "category" not in fm or not fm["category"]:
        fm["category"] = "uncategorized"
        notes.append("category defaulted to 'uncategorized'")
    if "tags" not in fm or not fm["tags"]:
        fm["tags"] = ["needs-tagging"]
        notes.append("tags placeholder — please fix")
    if "inputs" not in fm:
        fm["inputs"] = []
        notes.append("inputs not declared")
    if "output" not in fm:
        fm["output"] = {"format": "markdown"}
        notes.append("output defaulted to markdown")
    if "author" not in fm or not fm["author"]:
        fm["author"] = "unknown"
        notes.append("author unknown")
    if "license" not in fm or not fm["license"]:
        fm["license"] = "UNKNOWN"
        notes.append("license unknown — see source block")
    if "created" not in fm:
        fm["created"] = today
        notes.append("created set to today")
    if "updated" not in fm:
        fm["updated"] = today
    if notes:
        fm["needs_review"] = True
    return fm, notes


def render(fm: dict, body: str) -> str:
    """Re-emit frontmatter + body."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    from io import StringIO
    buf = StringIO()
    yaml.dump(fm, buf)
    return f"---\n{buf.getvalue()}---\n{body.lstrip()}"


def convert_file(path: Path, *, overwrite: bool, dry_run: bool) -> tuple[str, str, list[str]]:
    """Convert one file. Returns (slug, status, notes)."""
    slug = path.parent.name
    text = path.read_text(encoding="utf-8")
    fm, body, had_fm = split_frontmatter(text)

    notes: list[str] = []
    if not had_fm:
        notes.append("no frontmatter — full SKILL.md template needed")
        # bare .md with no frontmatter is not salvageable by convert alone;
        # hand it to extend-skill.py next.
    plat = detect_platform(fm, body)
    if plat and "platforms" not in fm:
        fm["platforms"] = [plat]
        notes.append(f"platform detected: {plat} (reviewer: confirm)")

    import datetime as dt
    today = dt.date.today().isoformat()
    fm, ensure_notes = ensure_required(fm, slug, today)
    notes.extend(ensure_notes)

    needs_review = bool(notes)
    fm["needs_review"] = needs_review

    if not notes and not overwrite:
        return (slug, "ok", [])  # idempotent — nothing to do
    if dry_run:
        return (slug, "ok", notes)
    path.write_text(render(fm, body), encoding="utf-8")
    return (slug, "ok" if not needs_review else "review", notes)


def collect_targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(p for p in SKILLS_DIR.glob("*/SKILL.md"))
    if not args.paths:
        print("no paths given and --all not set", file=sys.stderr)
        sys.exit(2)
    out: list[Path] = []
    for raw in args.paths:
        p = (REPO / raw) if not Path(raw).is_absolute() else Path(raw)
        if p.is_dir():
            out.extend(sorted(p.rglob("SKILL.md")))
        else:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("paths", nargs="*", help="file or dir paths (relative to repo root)")
    ap.add_argument("--all", action="store_true",
                    help="convert every skills/*/SKILL.md")
    ap.add_argument("--overwrite", action="store_true",
                    help="rewrite the file even if nothing changed")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would change, write nothing")
    args = ap.parse_args()

    targets = collect_targets(args)
    if not targets:
        print("no SKILL.md files to convert", file=sys.stderr)
        return 0

    print(f"Converting {len(targets)} file(s) { '(dry-run)' if args.dry_run else ''}\n")
    by_status: dict[str, list[tuple[Path, list[str]]]] = {"ok": [], "review": []}
    for p in targets:
        slug, status, notes = convert_file(p, overwrite=args.overwrite, dry_run=args.dry_run)
        by_status.setdefault(status, []).append((p, notes))

    for status in ("ok", "review"):
        rows = by_status.get(status, [])
        if not rows:
            continue
        print(f"## {status} ({len(rows)})")
        for p, notes in rows[:60]:
            extra = f"  notes: {'; '.join(notes)}" if notes else ""
            print(f"  {p.relative_to(REPO)}{extra}")
        if len(rows) > 60:
            print(f"  ... and {len(rows) - 60} more")
        print()

    needs_review = len(by_status.get("review", []))
    print(f"== {needs_review} flagged needs_review / {len(targets)} total ==")
    if needs_review:
        print("\nNext: run extend-skill.py to add worked examples and I/O contracts,")
        print("or edit the flagged files directly. validate-skill.py will warn until")
        print("needs_review is cleared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
