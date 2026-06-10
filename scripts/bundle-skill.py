#!/usr/bin/env python3
"""Bundle skills into a distributable zip.

  python scripts/bundle-skill.py pdf-summarizer -o bundles/pdf.zip
  python scripts/bundle-skill.py --all -o bundles/all.zip
  python scripts/bundle-skill.py pdf-summarizer code-reviewer -o bundles/handpicked.zip

Output structure mirrors skills/:

  pdf-summarizer/SKILL.md
  pdf-summarizer/assets/...
  code-reviewer/SKILL.md
  ...

Unzip into any agent's skills dir:

  unzip pdf.zip -d ~/.claude/skills/

By default, bundles land under bundles/ in the repo. That
directory is gitignored (except for its .gitkeep) — zips are
build artefacts, not source.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
DEFAULT_OUT_DIR = REPO / "bundles"


def collect_slugs(args: argparse.Namespace) -> list[str]:
    if args.all:
        return sorted(p.name for p in SKILLS_DIR.iterdir()
                      if p.is_dir() and not p.name.startswith(("_", ".")))
    return list(args.slugs)


def bundle(slugs: list[str], out_path: Path, *, dry_run: bool) -> tuple[int, int, list[str]]:
    """Bundle the given slugs. Returns (files_added, bytes_written, missing)."""
    if not slugs:
        return (0, 0, [])
    missing = [s for s in slugs if not (SKILLS_DIR / s).is_dir()]
    if missing:
        return (0, 0, missing)

    if dry_run:
        total = sum(1 for s in slugs for _ in (SKILLS_DIR / s).rglob("*") if _.is_file())
        return (total, 0, [])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()  # zipfile doesn't append, but make the intent explicit

    files_added = 0
    bytes_written = 0
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for slug in slugs:
            src = SKILLS_DIR / slug
            for f in sorted(src.rglob("*")):
                if f.is_file():
                    arcname = f.relative_to(SKILLS_DIR).as_posix()
                    zf.write(f, arcname)
                    files_added += 1
                    bytes_written += f.stat().st_size
    return (files_added, bytes_written, [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("slugs", nargs="*", help="skill slugs to bundle")
    ap.add_argument("--all", action="store_true", help="bundle every skill under skills/")
    ap.add_argument("-o", "--out", type=Path, required=True,
                    help="output zip path (relative to repo root, or absolute)")
    ap.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    args = ap.parse_args()

    if not args.all and not args.slugs:
        ap.error("give at least one slug, or use --all")

    slugs = collect_slugs(args)
    if not slugs:
        print("no skills to bundle", file=sys.stderr)
        return 0

    # Pre-flight: refuse to print a happy "Bundling …" line if any
    # slug is bogus. (caller can't tell the difference otherwise.)
    missing = [s for s in slugs if not (SKILLS_DIR / s).is_dir()]
    if missing:
        print(f"ERROR: missing skill(s): {missing}", file=sys.stderr)
        return 1

    out_path = args.out
    if not out_path.is_absolute():
        out_path = (REPO / out_path).resolve()

    print(f"Bundling {len(slugs)} skill(s) → {out_path} "
          f"{'(dry-run)' if args.dry_run else ''}\n")

    files, raw_bytes, _missing = bundle(slugs, out_path, dry_run=args.dry_run)
    print(f"  files:    {files}")
    print(f"  raw size: {raw_bytes:,} B  ({raw_bytes / 1024:.1f} KiB)")
    if not args.dry_run and out_path.exists():
        zipped = out_path.stat().st_size
        print(f"  zipped:   {zipped:,} B  ({zipped / 1024:.1f} KiB)  "
              f"[{zipped / max(raw_bytes, 1):.1%} of raw]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
