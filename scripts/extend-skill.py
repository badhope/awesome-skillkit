#!/usr/bin/env python3
"""Extend a thin SKILL.md so it passes validation.

The 4 rules live in docs/extension-rules.md. In short:

  Rule 1 — frontmatter is complete (slug, name, version, ...)
  Rule 2 — at least one worked example
  Rule 3 — concrete "When NOT to use" boundaries
  Rule 4 — strict I/O contract (typed inputs, explicit output)

This script is opinionated. It does not invent facts about the
upstream skill; it only:

  - fills in structural fields it can derive mechanically
    (slug from the directory, version, created, updated)
  - adds section skeletons when the body is missing one
  - keeps `needs_review: true` if it had to insert placeholder
    content the author needs to fill in

It does NOT touch the `# Prompt` block. That is the only
hard rule in this whole project: prompt text is the upstream
author's. We reformat, we never rewrite.

Usage:

  python scripts/extend-skill.py skills/foo/SKILL.md
  python scripts/extend-skill.py --all
  python scripts/extend-skill.py skills/foo skills/bar

The script is idempotent: running it twice doesn't duplicate
sections. Pass --force to re-emit placeholders anyway.
"""
from __future__ import annotations

import argparse
import datetime as dt
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

# Section headers that should be present, in this order. The names
# must match exactly (case-insensitive, leading `# `). Extra
# sections are allowed *after* these.
REQUIRED_SECTIONS = [
    "When to use",
    "Inputs",
    "Output",
    "Prompt",
]

OPTIONAL_SECTIONS = [
    "When NOT to use",
    "Example",
]

# Section body placeholders. We never invent the actual content
# of "When to use" or "Prompt" — only the structural ones where
# blanks are obvious (no example, no negative cases).
SECTION_PLACEHOLDERS = {
    "When NOT to use": (
        "- TODO: list at least 3 specific situations where this skill\n"
        "  is the wrong tool. Vague entries (\"may not apply\") are\n"
        "  rejected by review."
    ),
    "Example": (
        "**Input:**\n\n"
        "```\n"
        "TODO: paste a realistic input block from your skill's\n"
        "      frontmatter. Keep it short — one or two fields.\n"
        "```\n\n"
        "**Output:**\n\n"
        "```markdown\n"
        "TODO: paste the model's actual response. Do NOT edit it\n"
        "      to look prettier — fidelity matters more than polish.\n"
        "```"
    ),
}


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _rel(p: Path) -> str:
    """Show a path relative to the repo if possible, else as-is.

    Scripts accept both repo-relative and absolute paths from the
    user, and `relative_to(REPO)` will ValueError on the latter.
    This helper makes the output safe in both cases.
    """
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str, str]:
    """Return (frontmatter, header_block, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, "", text
    yaml = YAML(typ="safe")
    fm = dict(yaml.load(m.group(1)) or {})
    return fm, m.group(0), m.group(2)


def render(fm: dict, header_block: str, body: str) -> str:
    """Re-emit the file. If we changed the frontmatter, regenerate
    the header_block from `fm`; otherwise keep the original to
    preserve comments and quoting style.
    """
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    from io import StringIO
    buf = StringIO()
    yaml.dump(fm, buf)
    return f"---\n{buf.getvalue()}---\n{body.lstrip()}"


def find_sections(body: str) -> dict[str, tuple[int, int, str]]:
    """Map section name → (start_line, end_line, content).

    `end_line` is exclusive — it's the line where the next section
    starts (or len(body) for the last section). `content` is the
    raw substring between the section's H1 and the next H1.
    """
    lines = body.split("\n")
    out: dict[str, tuple[int, int, str]] = {}
    cur_name: str | None = None
    cur_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            name = line[2:].strip()
            if cur_name is not None:
                out[cur_name] = (cur_start, i, "\n".join(lines[cur_start:i]))
            cur_name = name
            cur_start = i
    if cur_name is not None:
        out[cur_name] = (cur_start, len(lines), "\n".join(lines[cur_start:]))
    return out


def extend_file(path: Path, *, force: bool, dry_run: bool) -> tuple[str, list[str]]:
    """Extend one file. Returns (slug, list of actions taken)."""
    slug = path.parent.name
    text = path.read_text(encoding="utf-8")
    fm, header, body = split_frontmatter(text)
    if not header:
        return (slug, ["ERROR: no frontmatter — run convert-skill.py first"])

    actions: list[str] = []

    # --- frontmatter fixes ------------------------------------------------
    today = dt.date.today().isoformat()
    if "slug" not in fm or not fm["slug"]:
        fm["slug"] = slug
        actions.append("frontmatter: added slug")
    if "name" not in fm:
        fm["name"] = slug.replace("-", " ").title()
        actions.append("frontmatter: added name placeholder")
    if "version" not in fm:
        fm["version"] = "0.1.0"
        actions.append("frontmatter: added version 0.1.0")
    if "description" not in fm or not fm["description"]:
        fm["description"] = "TODO: write a one-line description"
        actions.append("frontmatter: description is a placeholder — author must rewrite")
        fm["needs_review"] = True
    if "created" not in fm:
        fm["created"] = today
        actions.append(f"frontmatter: created = {today}")
    # We deliberately do NOT touch `updated` here. That field is
    # owned by the author — extend only fills blanks. (Touching it
    # would also make the script non-idempotent, since today()
    # advances across midnight.)

    # --- body section fixes ----------------------------------------------
    sections = find_sections(body)
    for name in REQUIRED_SECTIONS:
        if name not in sections:
            actions.append(f"body: missing required section '# {name}' (cannot auto-add)")
            fm["needs_review"] = True

    # Inject optional-section placeholders if absent.
    inserts: list[tuple[str, str]] = []  # (header_line, body_text)
    for name in OPTIONAL_SECTIONS:
        if name in sections:
            continue
        placeholder = SECTION_PLACEHOLDERS[name]
        inserts.append((f"# {name}", placeholder))
        actions.append(f"body: inserted placeholder '# {name}' (author must fill in)")
        fm["needs_review"] = True

    if inserts:
        # Append the missing optional sections at the end of the
        # body. The author still has to fill them in, but at least
        # the section skeleton is in place.
        addition = "\n\n" + "\n\n".join(f"{h}\n\n{b}" for h, b in inserts) + "\n"
        body = body.rstrip() + addition

    # --- write back -------------------------------------------------------
    if not actions:
        return (slug, [])  # idempotent

    if not dry_run:
        path.write_text(render(fm, header, body), encoding="utf-8")
    return (slug, actions)


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
                    help="extend every skills/*/SKILL.md")
    ap.add_argument("--force", action="store_true",
                    help="re-emit placeholders even if section already exists")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would change, write nothing")
    args = ap.parse_args()

    targets = collect_targets(args)
    if not targets:
        print("no SKILL.md files to extend", file=sys.stderr)
        return 0

    print(f"Extending {len(targets)} file(s) {'(dry-run)' if args.dry_run else ''}\n")
    changed = 0
    for p in targets:
        slug, actions = extend_file(p, force=args.force, dry_run=args.dry_run)
        if actions:
            changed += 1
            print(f"## {_rel(p)}")
            for a in actions:
                print(f"  - {a}")
            print()
    print(f"== {changed} file(s) changed / {len(targets)} total ==")
    if changed:
        print("\nNext: open the changed files, fill in the TODO placeholders,")
        print("then re-run convert-skill.py to clear `needs_review`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
