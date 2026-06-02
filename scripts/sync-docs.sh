#!/usr/bin/env bash
#
# Syncs the project-root documentation files into docs/_synced/ so
# mkdocs can render them as first-class pages with native URL
# resolution (and correct cross-references in the rendered site).
#
# The source files remain the single source of truth at the project
# root; this script only produces ephemeral build-time copies in
# docs/_synced/ (gitignored).
#
# For each file we also rewrite the cross-references to other
# project-root docs to point at the matching docs/_synced page.
# This is the only place where we need the rewrite map.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ROOT}/docs"
SRC="${ROOT}"

mkdir -p \
  "${DEST}/community" \
  "${DEST}/sdks" \
  "${DEST}/examples" \
  "${DEST}/operations"

# ---------------------------------------------------------------------------
# copy_readme
#
# Special-case the project README: it acts as the home page of the docs
# site.  We drop its H1 (the nav label "Home" is the title) and rewrite
# its links to point at the docs-site equivalents.  The output is
# written to docs/index.md, the home page of the docs site.
# ---------------------------------------------------------------------------
copy_readme() {
  local src="${SRC}/README.md"
  local dst="${DEST}/index.md"

  python3 - "$src" "$dst" <<'PY'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as f:
    text = f.read()

# Drop the first H1; the nav label "Home" is the page title.
text = re.sub(r"^# [^\n]*\n+", "", text, count=1, flags=re.MULTILINE)

# ----- link rewrites for the README -------------------------------------
# Project-root .md files  ->  docs-relative paths (or GitHub URLs for
# files that are not part of the docs site).
root_same = {
    "CODE_OF_CONDUCT.md": "community/code-of-conduct/",
    "CONTRIBUTING.md":    "community/contributing/",
    "FAQ.md":             "community/faq/",
    "ROADMAP.md":         "community/roadmap/",
    "CHANGELOG.md":       "community/changelog/",
    "TROUBLESHOOTING.md": "community/troubleshooting-short/",
    "LICENSE":            "https://github.com/badhope/AI-SKILL/blob/main/LICENSE",
    "SECURITY.md":        "operations/security/",
    "README.md":          "https://github.com/badhope/AI-SKILL#readme",
    "CITATION.cff":       "https://github.com/badhope/AI-SKILL/blob/main/CITATION.cff",
}
for k, v in root_same.items():
    # markdown link syntax ](k)  ->  ](v)
    text = re.sub(rf"\]\({re.escape(k)}(?P<anchor>#[^)]*)?\)",
                  lambda m, v=v: f"]({v}{m.group('anchor') or ''})", text)
    # HTML link syntax  href="k"  ->  href="v"
    text = re.sub(rf'href="{re.escape(k)}(?P<anchor>#[^"]*)?"',
                  lambda m, v=v: f'href="{v}{m.group("anchor") or ""}"', text)

# docs/<page>.md  ->  <page>/  (drop the "docs/" prefix; optionally
# preserve any anchor).  Handle both markdown link syntax
# (](docs/page.md)) and HTML anchor syntax (href="docs/page.md").
text = re.sub(
    r"\]\(docs/([a-z0-9\-]+)\.md(?P<anchor>#[^)]*)?\)",
    lambda m: f"]({m.group(1)}/{m.group('anchor') or ''})",
    text,
)
text = re.sub(
    r'href="docs/([a-z0-9\-]+)\.md(?P<anchor>#[^"]*)?"',
    lambda m: f'href="{m.group(1)}/{m.group("anchor") or ""}"',
    text,
)

# sdk/{python,typescript}/README.md  ->  sdks/python/ or sdks/typescript/
text = re.sub(
    r"\]\(sdk/(python|typescript)/README\.md\)",
    lambda m: f"](sdks/{m.group(1)}/)",
    text,
)

# examples/{rest,python,typescript,postman}/  ->  examples/<name>/
text = re.sub(
    r"\]\(examples/([a-z]+)/?\)",
    lambda m: f"](examples/{m.group(1)}/)",
    text,
)

# examples/README.md  ->  examples/  (the examples nav section's index).
text = re.sub(
    r"\]\(examples/README\.md\)",
    "](examples/)",
    text,
)

with open(dst, "w", encoding="utf-8") as f:
    f.write(text)
PY
}

# ---------------------------------------------------------------------------
# copy_one <src> <dst> <rewrite-kind>
#   rewrite-kind = "community" | "operations" | "sdks" | "examples"
# ---------------------------------------------------------------------------
copy_one() {
  local src="$1"
  local dst="$2"
  local kind="$3"

  python3 - "$src" "$dst" "$kind" <<'PY'
import re, sys
src, dst, kind = sys.argv[1], sys.argv[2], sys.argv[3]
with open(src, encoding="utf-8") as f:
    text = f.read()

# Drop the first H1 line; mkdocs uses the nav label as title.
text = re.sub(r"^# [^\n]*\n+", "", text, count=1, flags=re.MULTILINE)

# ----- cross-reference rewrites -----------------------------------------
# These are the only legitimate cross-references in the source docs
# that need to be remapped to the docs site layout.

# 1) Project-root "X.md" / "X"  →  "x"   (same nav section)
#
# For files that are *inside* a docs sub-section (community/, sdks/,
# examples/, operations/), the destination is one level deeper than
# "section root", so cross-references to sibling files in the same
# section need a leading "../".  We pick the right form per file kind.
root_same = {
    "CODE_OF_CONDUCT.md": "code-of-conduct/",
    "CONTRIBUTING.md":    "contributing/",
    "FAQ.md":             "faq/",
    "ROADMAP.md":         "roadmap/",
    "CHANGELOG.md":       "changelog/",
    "TROUBLESHOOTING.md": "troubleshooting-short/",
    "LICENSE":            "https://github.com/badhope/AI-SKILL/blob/main/LICENSE",
    "SECURITY.md":        "security/",
    "README.md":          "https://github.com/badhope/AI-SKILL#readme",
    "CITATION.cff":       "https://github.com/badhope/AI-SKILL/blob/main/CITATION.cff",
}
# When the file lives in a docs sub-section, sibling links in that
# section need a "../" prefix to be correct.
if kind in ("community", "sdks", "examples", "operations"):
    root_same = {k: ("../" + v if v.startswith(("code-of-conduct", "contributing", "faq", "roadmap", "changelog", "troubleshooting-short", "security")) else v)
                 for k, v in root_same.items()}
for k, v in root_same.items():
    text = re.sub(rf"\]\({re.escape(k)}[^)]*\)", f"]({v})", text)

# 2) "../X.md"  →  "../x/"   (parent-relative into the docs layout)
parent_same = {
    "CONTRIBUTING.md":    "../contributing/",
    "CODE_OF_CONDUCT.md": "../code-of-conduct/",
    "FAQ.md":             "../faq/",
    "ROADMAP.md":         "../roadmap/",
    "CHANGELOG.md":       "../changelog/",
    "TROUBLESHOOTING.md": "../troubleshooting-short/",
    "SECURITY.md":        "/operations/security/",
    "LICENSE":            "https://github.com/badhope/AI-SKILL/blob/main/LICENSE",
    "CITATION.cff":       "https://github.com/badhope/AI-SKILL/blob/main/CITATION.cff",
}
for k, v in parent_same.items():
    text = re.sub(rf"\]\(\.\./{re.escape(k)}[^)]*\)", f"]({v})", text)

# 3) Section-specific parents:
# Community/*  - ".. / ../../CONTRIBUTING.md" should become "contributing/"
text = re.sub(
    r"\]\((\.\./)+contributing\.md[^)]*\)",
    "](contributing/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+CODE_OF_CONDUCT\.md[^)]*\)",
    "](code-of-conduct/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+FAQ\.md[^)]*\)",
    "](faq/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+ROADMAP\.md[^)]*\)",
    "](roadmap/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+CHANGELOG\.md[^)]*\)",
    "](changelog/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+TROUBLESHOOTING\.md[^)]*\)",
    "](troubleshooting-short/)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+SECURITY\.md[^)]*\)",
    "](../operations/security/)",
    text,
)

# 3b) TROUBLESHOOTING.md / FAQ.md link to docs/troubleshooting.md
# (a sibling, but the full guide is at /troubleshooting/).
text = re.sub(
    r"\]\(docs/troubleshooting\.md[^)]*\)",
    "](/troubleshooting/)",
    text,
)

# 3c) FAQ.md links to ../SECURITY.md which sits in the operations
# section (../ is the project root; the docs equivalent is
# operations/security/).
text = re.sub(
    r"\]\(\.\./SECURITY\.md[^)]*\)",
    "](/operations/security/)",
    text,
)

# 4) SDK docs: "../X" in sdk/python/README.md was pointing to
# sdk/typescript/README.md; rewrite to the docs-relative path.
if kind == "sdks":
    # sdk files may link to their own sibling
    text = re.sub(
        r"\]\((\.\./typescript/README\.md)\)",
        "](typescript/)",
        text,
    )
    text = re.sub(
        r"\]\((\.\./python/README\.md)\)",
        "](python/)",
        text,
    )
    # turn "X/README.md" (within sdk tree) into "X"  (relative to sdks)
    text = re.sub(
        r"\]\((\.\./\.\./sdk/typescript/README\.md)\)",
        "](https://github.com/badhope/AI-SKILL/blob/main/sdk/typescript/README.md)",
        text,
    )
    text = re.sub(
        r"\]\((\.\./\.\./sdk/python/README\.md)\)",
        "](https://github.com/badhope/AI-SKILL/blob/main/sdk/python/README.md)",
        text,
    )

# 5) Examples: "../X" in examples/*/README.md was pointing to
# examples/X/README.md. Rewrite to the docs-relative path.
if kind == "examples":
    text = re.sub(
        r"\]\((\.\./([a-z]+)/README\.md)\)",
        lambda m: f"](../{m.group(2)}/)",
        text,
    )
    text = re.sub(
        r"\]\((\.\./\.\./examples/README\.md)\)",
        "](../)",
        text,
    )
    text = re.sub(
        r"\]\((\.\./README\.md)\)",
        "](../)",
        text,
    )

# 6) FAQ / TROUBLESHOOTING have `../../discussions/...` style
# absolute-ish links to GitHub — keep them as GitHub URLs.
text = re.sub(
    r"\]\(\.\./\.\./discussions/",
    "](https://github.com/badhope/AI-SKILL/discussions/",
    text,
)
text = re.sub(
    r"\]\(\.\./\.\./issues",
    "](https://github.com/badhope/AI-SKILL/issues",
    text,
)
text = re.sub(
    r"\]\(\.\./\.\./security/",
    "](https://github.com/badhope/AI-SKILL/security/",
    text,
)

# 7) Bug report / issue template refs:
text = re.sub(
    r"\]\(\.\./\.\./\.\.?/?\.github/ISSUE_TEMPLATE/bug_report\.md\)",
    "](https://github.com/badhope/AI-SKILL/issues/new?template=bug_report.md)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+\.github/ISSUE_TEMPLATE/bug_report\.md\)",
    "](https://github.com/badhope/AI-SKILL/issues/new?template=bug_report.md)",
    text,
)
text = re.sub(
    r"\]\((\.\./)+PULL_REQUEST_TEMPLATE\.md\)",
    "](https://github.com/badhope/AI-SKILL/blob/main/.github/PULL_REQUEST_TEMPLATE.md)",
    text,
)

# 8) Issue template 'security' link
text = re.sub(
    r"\]\((\.\./)*security/advisories/new\)",
    "](https://github.com/badhope/AI-SKILL/security/advisories/new)",
    text,
)

# 9) "docs/troubleshooting.md" — links to the full troubleshooting doc
# (not the short FAQ-style one we expose at community/troubleshooting-short/).
text = re.sub(
    r"\]\(docs/troubleshooting\.md(?P<anchor>#[^)]*)?\)",
    lambda m: f"](../troubleshooting/{m.group('anchor') or ''})",
    text,
)
text = re.sub(
    r"\]\(\.\./troubleshooting\.md(?P<anchor>#[^)]*)?\)",
    lambda m: f"](../troubleshooting/{m.group('anchor') or ''})",
    text,
)

with open(dst, "w", encoding="utf-8") as f:
    f.write(text)
PY
}

# Community
copy_one "${SRC}/CONTRIBUTING.md"    "${DEST}/community/contributing.md"            "community"
copy_one "${SRC}/CODE_OF_CONDUCT.md" "${DEST}/community/code-of-conduct.md"         "community"
copy_one "${SRC}/FAQ.md"             "${DEST}/community/faq.md"                     "community"
copy_one "${SRC}/ROADMAP.md"         "${DEST}/community/roadmap.md"                 "community"
copy_one "${SRC}/CHANGELOG.md"       "${DEST}/community/changelog.md"               "community"
copy_one "${SRC}/TROUBLESHOOTING.md" "${DEST}/community/troubleshooting-short.md"   "community"

# Operations
copy_one "${SRC}/SECURITY.md"        "${DEST}/operations/security.md"               "operations"

# SDKs
copy_one "${SRC}/sdk/python/README.md"     "${DEST}/sdks/python.md"                 "sdks"
copy_one "${SRC}/sdk/typescript/README.md"  "${DEST}/sdks/typescript.md"             "sdks"

# Examples
copy_one "${SRC}/examples/README.md"        "${DEST}/examples/index.md"              "examples"
copy_one "${SRC}/examples/rest/README.md"   "${DEST}/examples/rest.md"               "examples"
copy_one "${SRC}/examples/python/README.md" "${DEST}/examples/python.md"             "examples"
copy_one "${SRC}/examples/typescript/README.md" "${DEST}/examples/typescript.md"     "examples"
copy_one "${SRC}/examples/postman/README.md"    "${DEST}/examples/postman.md"         "examples"

# Home page (the project README is the docs home).
copy_readme

echo "Synced $(find "${DEST}/community" "${DEST}/sdks" "${DEST}/examples" "${DEST}/operations" -name '*.md' 2>/dev/null | wc -l | tr -d ' ') synced files into ${DEST}"
