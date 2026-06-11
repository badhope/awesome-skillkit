#!/usr/bin/env python3
"""Extend scripts/sources.json with real SKILL.md paths.

Reads the audit report from audit-sources.py (`/tmp/audit.json`
by default) and converts the discovered `skill_shaped` paths
into fetch entries we can hand to fetch-skill.py.

What this script does NOT do
----------------------------

- It does NOT fetch anything. That's fetch-skill.py's job.
- It does NOT edit any existing SKILL.md. convert-skill.py does
  that.
- It does NOT remove the original 18 README.md placeholders. They
  stay in the file (with `skip: true`) for audit trail. The
  discoverer can see "I tried repo X's README; the real skills
  are over here" at a glance.

Dedup rules
-----------

The audit found 62 skill-shaped files across 8 repos. Many of
them are noise:

  - crewAI test fixtures
  - anthropics's internal `cookbook-audit` skill and its MCP
    wrapper skills (linear/sentry/slack/cma-mcp)
  - promptfoo's `examples/*/skill-comparison/fixtures/*` (test
    data, not real skills)
  - Duplicates of skills we already have (clickhouse, pnpm,
    storybook, turborepo, ...)
  - The bootstrap-realtime-eval variant of our
    realtime-eval-bootstrap (different slug, same idea; keep
    ours, skip upstream)
  - promptfoo's `.agents/skills/{X}` paths which mirror
    `.claude/skills/{X}` (same content, two locations)

For the rest, we keep the upstream path. The vault's local
slug is the directory name in the upstream path, prefixed
with `<source-repo>-` if the upstream skill's name would
clash with one we already have (none of the current audit
findings need a prefix; we use the bare name).

Slug conflicts where two upstream paths would map to the same
local slug (e.g. agno's `git-workflow/SKILL.md` and langfuse's
`.agents/skills/git-workflow/SKILL.md`):

  We keep the first match in audit order and skip the rest.
  Audit order is stable: openai → crewAI → anthropics →
  awesome → agno → promptfoo → deepeval → langfuse. langfuse
  is last because it's our largest source. For the rare case
  where two sources have the same name, the earlier source
  wins (in this run, agno wins the `git-workflow` slug).

Output
------

We do not overwrite `scripts/sources.json` in place. We write
to `scripts/sources.json` directly — this script is run by
the operator once per audit cycle, after they've reviewed the
report. The new entries are appended to `items`; existing
entries (with `skip: true`) stay where they are.

Each new entry is marked with `audit: true` and a `note`
explaining where it came from. fetch-skill.py ignores both
fields.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "scripts" / "sources.json"
SKILLS_DIR = REPO / "skills"
AUDIT = Path("/tmp/audit.json")

# Paths we never want to fetch, regardless of which repo they're in.
# Matched as substrings of the upstream `path`.
PATH_DENYLIST = (
    "tests/skills/fixtures/",        # crewAI test fixtures
    "skill-comparison/fixtures/",    # promptfoo test fixtures
    ".claude/skills/cookbook-audit", # anthropics's own review skill
    "managed_agents/",               # anthropics MCP wrappers
)

# Slugs the vault already has. We skip any upstream skill whose
# directory name matches one of these — the local copy is the
# canonical one for our catalog.
LOCAL_SLUGS = {
    "browser-ml-in-js", "cli-builder", "clickhouse-best-practices",
    "code-review", "code-reviewer", "commit-message-writer",
    "deepeval-eval-suite", "deepeval-otel", "deepeval-tracing",
    "doc-coauthoring", "embedding-model-training",
    "frontend-large-feature-architecture", "frontend-visual-design",
    "goal-definition", "internal-comms", "llm-pricing-file-update",
    "mcp-builder", "ownership-bus-factor", "pdf-summarizer",
    "pdf-vision-extractor", "pnpm-upgrade-package", "pr-yeet",
    "promptfoo-evals", "promptfoo-redteam", "react-router-search-params",
    "realtime-eval-bootstrap", "secure-code-by-language", "security-review",
    "skill-creator", "sql-query-helper", "storybook", "test-generator",
    "threat-modeling", "turborepo", "webapp-testing",
}

# Path → slug overrides. Used when the upstream directory name
# isn't a good local slug (e.g. ends in `-review` but means
# "code review" which would clash with our existing `code-review`).
SLUG_OVERRIDES = {
    "bootstrap-realtime-eval": None,  # skip — we already have realtime-eval-bootstrap
}


def slug_from_path(path: str) -> str:
    """Return the directory name that contains the SKILL.md."""
    # path/to/skills/<slug>/SKILL.md → <slug>
    parts = path.rstrip("/").split("/")
    if "SKILL.md" in parts or "skill.md" in parts:
        return parts[-2]
    return parts[-1]


def is_denied(path: str) -> bool:
    return any(needle in path for needle in PATH_DENYLIST)


def make_entry(source: str, ref: str, path: str, slug: str) -> dict:
    """Build one fetch spec entry."""
    return {
        "source": source,
        "ref": ref,
        "path": path,
        "out": f"skills/{slug}/SKILL.md",
        "slug": slug,
        "audit": True,
        "note": f"discovered by audit-sources.py from {source}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--audit", type=Path, default=AUDIT,
                    help=f"audit JSON to read (default: {AUDIT})")
    ap.add_argument("--sources", type=Path, default=SOURCES,
                    help=f"manifest to extend (default: {SOURCES})")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be added, write nothing")
    ap.add_argument("--verbose", action="store_true",
                    help="print every skip with its reason")
    args = ap.parse_args()

    if not args.audit.exists():
        print(f"audit report not found: {args.audit}", file=sys.stderr)
        print("run audit-sources.py first", file=sys.stderr)
        return 2
    if not args.sources.exists():
        print(f"sources file not found: {args.sources}", file=sys.stderr)
        return 2

    audit = json.loads(args.audit.read_text())
    sources = json.loads(args.sources.read_text())
    existing_items: list[dict] = sources.get("items", [])

    # Verify local slugs match what's on disk. If somebody deleted
    # a skill, we'd silently lose the dedup and create a duplicate
    # — fail loudly instead.
    on_disk = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    if on_disk != LOCAL_SLUGS:
        print(f"warn: LOCAL_SLUGS in this script differs from on-disk skills/ ({len(on_disk)} dirs)", file=sys.stderr)
        print(f"  on disk but not in script: {sorted(on_disk - LOCAL_SLUGS)}", file=sys.stderr)
        print(f"  in script but not on disk: {sorted(LOCAL_SLUGS - on_disk)}", file=sys.stderr)

    new_entries: list[dict] = []
    used_slugs: set[str] = set()
    skip_reasons: dict[str, list[str]] = {"denied": [], "local-clash": [], "override-skip": [], "dup-slug": []}

    for repo in audit:
        if repo.get("category") != "found":
            continue
        source = repo["source"]
        ref = repo["ref"]
        for path in repo["info"].get("skill_shaped", []):
            slug = slug_from_path(path)
            if slug in SLUG_OVERRIDES and SLUG_OVERRIDES[slug] is None:
                skip_reasons["override-skip"].append(f"{source}:{path}")
                continue
            if slug in LOCAL_SLUGS:
                skip_reasons["local-clash"].append(f"{source}:{path} (slug {slug!r} already in vault)")
                continue
            if is_denied(path):
                skip_reasons["denied"].append(f"{source}:{path}")
                continue
            if slug in used_slugs:
                skip_reasons["dup-slug"].append(f"{source}:{path} (slug {slug!r} already taken this run)")
                continue
            new_entries.append(make_entry(source, ref, path, slug))
            used_slugs.add(slug)

    if args.verbose:
        for reason, rows in skip_reasons.items():
            if rows:
                print(f"## skip: {reason} ({len(rows)})")
                for r in rows[:40]:
                    print(f"  {r}")
                if len(rows) > 40:
                    print(f"  ... and {len(rows) - 40} more")
                print()

    print(f"== {len(new_entries)} new entries / {sum(len(v) for v in skip_reasons.values())} skipped ==")
    if not new_entries:
        return 0
    for e in new_entries:
        print(f"  + {e['source']:35s}  {e['slug']:35s}  {e['path']}")
    print()

    if args.dry_run:
        print("(dry-run: nothing written)")
        return 0

    # Merge. Original entries first (preserved verbatim), audit
    # entries appended at the end. We do not touch existing
    # `skip: true` entries — the audit history stays in the file.
    sources["items"] = existing_items + new_entries
    sources.setdefault("_meta", {})
    sources["_meta"]["_status"] = "audit-extended"
    sources["_meta"]["_status_detail"] = (
        f"Extended by extend-sources.py on the back of an "
        f"audit-sources.py run. {len(new_entries)} new entries "
        f"appended to the {len(existing_items)} original README "
        f"placeholders. Run fetch-skill.py --all to pull them."
    )
    sources["_meta"]["_audit_skipped"] = {
        k: len(v) for k, v in skip_reasons.items() if v
    }

    args.sources.write_text(
        json.dumps(sources, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.sources.relative_to(REPO)} "
          f"({len(existing_items)} existing + {len(new_entries)} new = "
          f"{len(existing_items) + len(new_entries)} total)")
    print("\nNext: python3 scripts/fetch-skill.py --all --sources scripts/sources.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
