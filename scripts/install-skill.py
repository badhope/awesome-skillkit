#!/usr/bin/env python3
"""Install a local skill into a target agent's skills directory.

  python scripts/install-skill.py pdf-summarizer --target claude
  python scripts/install-skill.py pdf-summarizer --target codex
  python scripts/install-skill.py pdf-summarizer --target /opt/my-agent/skills
  python scripts/install-skill.py --all --target claude

The copy is a plain `shutil.copytree`. We do NOT install the
whole `skills/` directory — only the slug you name, including
its `assets/` subdirectory if present.

Recognised --target values:

  claude     →  ~/.claude/skills/<slug>/
  codex      →  ~/.codex/skills/<slug>/
  cursor     →  ~/.cursor/skills/<slug>/
  continue   →  ~/.continue/skills/<slug>/
  <path>     →  <path>/<slug>/  (parent dir must exist)

If the destination already exists, we refuse to overwrite unless
--force is given. This is on purpose: agent CLIs read the skills
dir on every turn, and a half-copied skill mid-overwrite is worse
than no skill.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

KNOWN_TARGETS = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
    "continue": Path.home() / ".continue" / "skills",
}


def resolve_target(t: str) -> Path:
    """Translate a --target value into a directory path."""
    if t in KNOWN_TARGETS:
        return KNOWN_TARGETS[t]
    p = Path(t).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def install_one(slug: str, target_root: Path, *, force: bool, dry_run: bool) -> tuple[str, str, str]:
    """Install one skill. Returns (slug, status, detail)."""
    src = SKILLS_DIR / slug
    if not src.is_dir():
        return (slug, "missing", f"no such skill: {src.relative_to(REPO)}")

    dst = target_root / slug
    if dst.exists():
        if not force:
            return (slug, "exists", f"{dst} already exists (use --force to overwrite)")
        if not dry_run:
            shutil.rmtree(dst)

    if dry_run:
        return (slug, "ok", f"(dry-run) would copy {src.relative_to(REPO)} → {dst}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return (slug, "ok", f"installed to {dst}")


def collect_slugs(args: argparse.Namespace) -> list[str]:
    if args.all:
        return sorted(p.name for p in SKILLS_DIR.iterdir()
                      if p.is_dir() and not p.name.startswith(("_", ".")))
    return list(args.slugs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("slugs", nargs="*", help="skill slugs to install (e.g. pdf-summarizer)")
    ap.add_argument("--all", action="store_true", help="install every skill under skills/")
    ap.add_argument("--target", required=True,
                    help=f"target name ({', '.join(KNOWN_TARGETS)}) or absolute path")
    ap.add_argument("--force", action="store_true", help="overwrite existing destination")
    ap.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    args = ap.parse_args()

    if not args.all and not args.slugs:
        ap.error("give at least one slug, or use --all")

    target_root = resolve_target(args.target)
    slugs = collect_slugs(args)
    if not slugs:
        print("no skills to install", file=sys.stderr)
        return 0

    print(f"Installing {len(slugs)} skill(s) to {target_root} "
          f"{'(dry-run)' if args.dry_run else ''}\n")

    by_status: dict[str, list[tuple[str, str]]] = {}
    for slug in slugs:
        _, status, detail = install_one(slug, target_root, force=args.force, dry_run=args.dry_run)
        by_status.setdefault(status, []).append((slug, detail))

    for status in ("ok", "exists", "missing"):
        rows = by_status.get(status, [])
        if not rows:
            continue
        print(f"## {status} ({len(rows)})")
        for slug, detail in rows[:40]:
            print(f"  {slug:30s}  {detail}")
        if len(rows) > 40:
            print(f"  ... and {len(rows) - 40} more")
        print()

    failed = sum(len(v) for k, v in by_status.items() if k not in ("ok",))
    print(f"== {len(slugs) - failed} ok / {failed} failed / {len(slugs)} total ==")
    if not args.dry_run and not KNOWN_TARGETS.get(args.target):
        print(f"\nNote: {target_root} is a custom path. Some agent CLIs watch")
        print("well-known directories; verify your CLI picks this up.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
