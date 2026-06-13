#!/usr/bin/env python3
"""Validate every SKILL.md under skills/ against docs/schema.md.

What this checks
----------------

  - frontmatter parses as YAML
  - all required fields are present (slug, name, version, ...)
  - types match (version is semver, tags is non-empty list, etc.)
  - inputs are typed and `required: true` fields have no default
  - output.format is one of the allowed set
  - body has the 4 required H1 sections in order
  - if platforms: [claude] (or similar) is set, the first body
    section contains a `**Claude-only**` (or platform-named)
    disclaimer in the first 800 chars
  - source.url + source.commit are present for non-trivial skills
  - slug matches the parent directory name
  - no two skills share a slug

Side effect: regenerates skills/_index.yaml from the SKILL.md
files that pass validation. Skills that fail are skipped from
the index and reported.

Exit codes:

  0  all files pass (warnings are still allowed)
  1  one or more files fail
  2  invalid arguments / missing file / import error
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
INDEX_YAML = SKILLS_DIR / "_index.yaml"
FRONTEND_PUBLIC = REPO / "frontend" / "public"
FRONTEND_SKILLS_JSON = FRONTEND_PUBLIC / "skills.json"
FRONTEND_SKILLS_DIR = FRONTEND_PUBLIC / "skills"

REQUIRED_FIELDS = (
    "slug", "name", "version", "description", "category",
    "tags", "inputs", "output", "author", "license",
    "created", "updated",
)
OPTIONAL_FIELDS = (
    "name_zh", "description_zh", "platforms", "source",
    "needs_review", "tags_zh",
)
ALLOWED_OUTPUT_FORMATS = {"markdown", "json", "text", "code"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([\-+][0-9A-Za-z.\-]+)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
REQUIRED_SECTIONS = ["When to use", "Inputs", "Output", "Prompt"]


def _rel(p: Path) -> str:
    """Show a path relative to the repo if possible, else as-is."""
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[Path, str]] = []
        self.warnings: list[tuple[Path, str]] = []

    def err(self, p: Path, msg: str) -> None:
        self.errors.append((p, msg))

    def warn(self, p: Path, msg: str) -> None:
        self.warnings.append((p, msg))


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "", text
    yaml = YAML(typ="safe")
    try:
        fm = dict(yaml.load(m.group(1)) or {})
    except Exception:
        return None, "", text
    return fm, m.group(0), m.group(2)


def section_names(body: str) -> list[str]:
    return [line[2:].strip() for line in body.split("\n")
            if line.startswith("# ") and not line.startswith("## ")]


def has_platform_disclaimer(body: str, platforms: list[str]) -> bool:
    """If the skill is platform-locked, the body must call it out
    near the top. We accept any of the named platforms as a key
    inside a `**...only**` block.
    """
    head = body[:800].lower()
    for plat in platforms:
        if f"**{plat}-only**" in head or f"**{plat} only**" in head:
            return True
    return False


def validate_one(path: Path, report: Report, *, all_categories: set[str]) -> dict | None:
    text = path.read_text(encoding="utf-8")
    fm, _header, body = split_frontmatter(text)

    if fm is None:
        report.err(path, "frontmatter missing or unparseable")
        return None

    # required fields
    missing = [f for f in REQUIRED_FIELDS if f not in fm]
    if missing:
        report.err(path, f"missing required fields: {missing}")

    # slug
    slug = fm.get("slug")
    if not isinstance(slug, str) or not SLUG_RE.match(slug):
        report.err(path, f"slug is not kebab-case: {slug!r}")
    elif slug != path.parent.name:
        report.err(path, f"slug {slug!r} does not match directory {path.parent.name!r}")

    # version
    ver = fm.get("version")
    if not isinstance(ver, str) or not SEMVER_RE.match(ver):
        report.err(path, f"version is not semver: {ver!r}")

    # dates — accept both strings and datetime.date (ruamel.yaml
    # parses YYYY-MM-DD into a date object under some loaders)
    import datetime as _dt
    for d in ("created", "updated"):
        v = fm.get(d)
        if isinstance(v, _dt.date):
            v = v.isoformat()
        if not isinstance(v, str) or not DATE_RE.match(v):
            report.err(path, f"{d} is not YYYY-MM-DD: {v!r}")

    # category
    cat = fm.get("category")
    if not isinstance(cat, str):
        report.err(path, f"category is not a string: {cat!r}")
    elif all_categories and cat not in all_categories:
        report.warn(path, f"category {cat!r} is not in the 49 known categories (verify spelling)")

    # tags
    tags = fm.get("tags")
    needs_review = bool(fm.get("needs_review"))
    if not isinstance(tags, list) or not (2 <= len(tags) <= 5):
        # needs_review files are fresh imports whose tag set is a
        # placeholder; we let them through as a warning rather than
        # a hard error. The author has to fill the tags in as part
        # of clearing `needs_review`. Files without that flag still
        # fail hard — once it's cleared the validator expects a
        # real tag set.
        if needs_review:
            report.warn(path, f"tags must be 2-5 items, got {len(tags) if isinstance(tags, list) else 'not a list'} (will block clear of needs_review)")
        else:
            report.err(path, f"tags must be 2-5 items, got {len(tags) if isinstance(tags, list) else 'not a list'}")
    elif not all(isinstance(t, str) and t for t in tags):
        report.err(path, "tags must be non-empty strings")
    elif not all(t == t.lower() for t in tags):
        report.warn(path, "tags should be lowercase")

    # inputs
    inputs = fm.get("inputs")
    if not isinstance(inputs, list):
        report.err(path, "inputs must be a list")
    else:
        seen = set()
        for i, inp in enumerate(inputs):
            if not isinstance(inp, dict):
                report.err(path, f"inputs[{i}] is not a dict")
                continue
            name = inp.get("name")
            if not name:
                report.err(path, f"inputs[{i}] missing name")
            elif name in seen:
                report.err(path, f"duplicate input name: {name}")
            seen.add(name)
            if "type" not in inp:
                report.err(path, f"inputs[{i}] ({name}) missing type")
            if inp.get("required") and "default" in inp:
                report.err(path, f"inputs[{i}] ({name}) is required but has a default")

    # output
    output = fm.get("output")
    if not isinstance(output, dict):
        report.err(path, "output must be a dict")
    else:
        fmt = output.get("format")
        if fmt not in ALLOWED_OUTPUT_FORMATS:
            report.err(path, f"output.format must be one of {sorted(ALLOWED_OUTPUT_FORMATS)}, got {fmt!r}")

    # platforms — empty list is fine: it means "all platforms" (the
    # skill is vendor-neutral). Non-empty means it's locked to those
    # platforms, which requires a `**X-only**` disclaimer near the
    # top of the body.
    platforms = fm.get("platforms")
    if platforms is not None and not isinstance(platforms, list):
        report.err(path, "platforms must be a list if set")
    elif isinstance(platforms, list) and platforms and not has_platform_disclaimer(body, platforms):
        # Bug bait: don't say "**{platforms[0]}-only**" — the checker
        # only requires ONE of the listed platforms to have the
        # disclaimer, but the message should match the requirement,
        # not pin a specific platform.
        # Same logic as tags/sections: needs_review files are
        # fresh imports where the upstream didn't include our
        # "**<platform>-only**" disclaimer convention. The author
        # adds it (or removes `platforms:`) as part of clearing
        # the flag.
        if needs_review:
            report.warn(path, f"platforms={platforms} but body has no '**<one of {platforms}>-only**' disclaimer in first 800 chars (will block clear of needs_review)")
        else:
            report.err(path, f"platforms={platforms} but body has no '**<one of {platforms}>-only**' disclaimer in first 800 chars")

    # source
    src = fm.get("source")
    if isinstance(src, dict):
        for k in ("url", "commit"):
            if not src.get(k):
                report.warn(path, f"source.{k} missing — provenance incomplete")

    # sections
    secs = section_names(body)
    if secs[:len(REQUIRED_SECTIONS)] != REQUIRED_SECTIONS:
        # Freshly imported skills from upstream repos use the
        # upstream's own H1 layout (skill title + free-form H2
        # sections). Until the author rewraps the body into the
        # 4-section contract, that's a warning, not a hard
        # error — needs_review is exactly the flag we use to
        # mark "imported, not yet adapted to our shape".
        if needs_review:
            report.warn(path, f"first sections must be {REQUIRED_SECTIONS}, got {secs[:len(REQUIRED_SECTIONS)]} (will block clear of needs_review)")
        else:
            report.err(path, f"first sections must be {REQUIRED_SECTIONS}, got {secs[:len(REQUIRED_SECTIONS)]}")

    # needs_review is a soft flag — warn so authors see it
    if fm.get("needs_review"):
        report.warn(path, "needs_review: true — author must revisit")

    # If we got any errors, don't include this skill in the index
    if any(p == path for p, _ in report.errors):
        return None
    return fm


def load_categories() -> set[str]:
    """Read the 49 category slugs from external-index/skills.yaml.

    SKILL.md frontmatter `category:` should be one of these slugs.
    We don't fail if external-index/ is missing — the categories
    are just a soft warning then.
    """
    path = REPO / "external-index" / "skills.yaml"
    if not path.exists():
        return set()
    try:
        import yaml
        with path.open() as f:
            data = yaml.safe_load(f)
    except Exception:
        return set()
    cats = data.get("categories", []) or []
    return {c.get("slug") for c in cats if isinstance(c, dict) and c.get("slug")}


def write_index(entries: list[dict]) -> None:
    """Regenerate skills/_index.yaml from validated entries.

    The index is a slim projection: it keeps what the front-end /
    install-skill.py needs, and drops the heavy fields (inputs,
    output schema, source).
    """
    lines = ["# Local skill index — built by validate-skill.py.",
             "#",
             "# Do NOT edit by hand. Edit the corresponding",
             "# skills/<slug>/SKILL.md and re-run validate-skill.py.",
             ""]
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    from io import StringIO

    skills_out: list[dict] = []
    for fm in sorted(entries, key=lambda x: x.get("slug", "")):
        skills_out.append({
            "slug": fm.get("slug"),
            "name": fm.get("name"),
            "name_zh": fm.get("name_zh"),
            "description": fm.get("description", ""),
            "category": fm.get("category"),
            "tags": fm.get("tags", []),
            "platforms": fm.get("platforms", []),
            "needs_review": bool(fm.get("needs_review")),
            "path": f"skills/{fm.get('slug')}/SKILL.md",
        })
    data = {"skills": skills_out}
    buf = StringIO()
    yaml.dump(data, buf)
    INDEX_YAML.write_text("\n".join(lines) + "\n" + buf.getvalue(), encoding="utf-8")


def write_frontend_bundle(targets: list[Path], passed: list[dict]) -> None:
    """Write JSON files the frontend reads at runtime.

    Two outputs:

      frontend/public/skills.json
        The slim index (name, slug, category, tags, platforms,
        needs_review, path). Loaded by the list page on first
        paint.

      frontend/public/skills/<slug>.json
        The full Skill object including the body. Loaded by the
        detail page and the bundle page on demand.

    If `frontend/` doesn't exist (e.g. we're running CI on a
    tree where the frontend hasn't been bootstrapped yet), we
    silently skip — the operator can run `npm install` later.
    """
    if not FRONTEND_PUBLIC.exists():
        return
    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)
    FRONTEND_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    import json
    slim: list[dict] = []
    passed_slugs = {fm.get("slug") for fm in passed}
    for fm in sorted(passed, key=lambda x: x.get("slug", "")):
        slim.append({
            "slug": fm.get("slug"),
            "name": fm.get("name"),
            "name_zh": fm.get("name_zh"),
            "description": fm.get("description", ""),
            # description_zh on the index lets the list page
            # render cards fully translated when the user has
            # toggled to Chinese. None for skills that lack it;
            # the JS falls back to en in that case.
            "description_zh": fm.get("description_zh") or None,
            "category": fm.get("category"),
            "tags": fm.get("tags", []),
            "platforms": fm.get("platforms", []),
            "needs_review": bool(fm.get("needs_review")),
            "path": f"skills/{fm.get('slug')}/SKILL.md",
        })
    FRONTEND_SKILLS_JSON.write_text(
        json.dumps({"skills": slim}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Clean stale per-skill files first (so deleted skills don't
    # leave JSON ghosts in the public bundle).
    for old in FRONTEND_SKILLS_DIR.glob("*.json"):
        if old.stem not in passed_slugs:
            old.unlink()

    for p in targets:
        slug = p.parent.name
        if slug not in passed_slugs:
            continue
        try:
            text = p.read_text(encoding="utf-8")
            fm, _h, body = split_frontmatter(text)
            if fm is None:
                continue
            skill = dict(fm)
            # Ensure platforms is always present (frontend expects it)
            if "platforms" not in skill:
                skill["platforms"] = []
            skill["body"] = body
            skill["needs_review"] = bool(skill.get("needs_review"))
            # Preserve the original SKILL.md text so the detail /
            # bundle pages can hand the user the *exact* file we
            # vendored, byte-for-byte (no re-emitted YAML, no
            # field reordering). Used by the "Download .md" /
            # bundle .zip export buttons. (F1)
            skill["rawMarkdown"] = text
            (FRONTEND_SKILLS_DIR / f"{slug}.json").write_text(
                json.dumps(skill, ensure_ascii=False, indent=2, default=_json_default),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"  warn   {_rel(p)}: frontend JSON export failed: {e}", file=sys.stderr)


def _json_default(o):
    """Fallback JSON encoder for ruamel.yaml-loaded objects.

    ruamel parses YYYY-MM-DD into `datetime.date`, which `json`
    refuses. Convert to ISO string. Anything else is a bug
    and we let it raise so it shows up in the warning.
    """
    import datetime as _dt
    if isinstance(o, (_dt.date, _dt.datetime)):
        return o.isoformat()
    raise TypeError(f"{type(o).__name__} is not JSON serialisable")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("paths", nargs="*",
                    help="files or dirs; default = every skills/*/SKILL.md")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors")
    ap.add_argument("--no-index", action="store_true",
                    help="don't regenerate skills/_index.yaml")
    ap.add_argument("--quiet", action="store_true",
                    help="only print errors and the final summary")
    args = ap.parse_args()

    if args.paths:
        targets: list[Path] = []
        for raw in args.paths:
            p = (REPO / raw) if not Path(raw).is_absolute() else Path(raw)
            if p.is_dir():
                targets.extend(sorted(p.rglob("SKILL.md")))
            else:
                targets.append(p)
    else:
        targets = sorted(SKILLS_DIR.glob("*/SKILL.md"))

    if not targets:
        print("no SKILL.md files to validate", file=sys.stderr)
        if not args.no_index:
            write_index([])
        return 0

    report = Report()
    categories = load_categories()
    passed: list[dict] = []
    seen_slugs: dict[str, Path] = {}

    for p in targets:
        fm = validate_one(p, report, all_categories=categories)
        if fm is not None:
            slug = fm.get("slug")
            if slug in seen_slugs:
                report.err(p, f"duplicate slug {slug!r} (also in {seen_slugs[slug]})")
            else:
                seen_slugs[slug] = p
                passed.append(fm)

    if not args.quiet:
        for p, msg in report.warnings:
            print(f"  warn  {_rel(p)}: {msg}", file=sys.stderr)
    for p, msg in report.errors:
        print(f"  err   {_rel(p)}: {msg}", file=sys.stderr)

    print(f"\n== {len(passed)} pass / {len(report.errors)} err / {len(report.warnings)} warn / {len(targets)} total ==")

    if report.errors:
        return 1
    if args.strict and report.warnings:
        print("strict mode: warnings are errors", file=sys.stderr)
        return 1
    if not args.no_index:
        write_index(passed)
        write_frontend_bundle(targets, passed)
        if not args.quiet:
            print(f"wrote {INDEX_YAML.relative_to(REPO)}")
            if FRONTEND_PUBLIC.exists():
                print(f"wrote {FRONTEND_SKILLS_JSON.relative_to(REPO)} + "
                      f"{len(passed)} per-skill file(s) under "
                      f"{FRONTEND_SKILLS_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
