#!/usr/bin/env python3
"""Batch-fix all SKILL.md frontmatter and body issues.

Fixes:
1. version: X.Y.Z → version: 'X.Y.Z' (YAML float → string)
2. source: (empty) → source: null
3. source: followed by stray ref: → source: null (remove stray ref)
4. language: en → remove (not a schema field)
5. description/description_zh: '|' or '>' → use first meaningful body line
6. description/description_zh: multi-line without quotes → single-line quoted
7. created/updated: YYYY-MM-DD → 'YYYY-MM-DD' (YAML date → string)
8. Body not starting with '# When to use' → prepend the section
9. version: X.Y.Z-suffix → 'X.Y.Z-suffix' (non-semver quoted)
"""
import os
import re
import glob

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


def fix_multiline_description(lines: list[str], start_idx: int) -> tuple[str, int]:
    """Join a multi-line YAML value into a single quoted line.

    Returns (new_line, next_index).
    """
    # Collect the first line's value
    first_line = lines[start_idx]
    m = re.match(r"^(description(?:_zh)?):\s*(.*)", first_line)
    field = m.group(1)
    value = m.group(2).strip()

    # If already quoted, skip
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        return first_line, start_idx + 1

    # Collect continuation lines (indented)
    j = start_idx + 1
    parts = [value]
    while j < len(lines) and lines[j].startswith("  ") and lines[j].strip():
        parts.append(lines[j].strip())
        j += 1

    # Join and truncate
    full = " ".join(p for p in parts if p)
    if len(full) > 200:
        full = full[:197] + "..."

    # Escape single quotes
    full = full.replace("'", "''")
    return f"{field}: '{full}'", j


def fix_file(path: str) -> tuple[bool, list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not m:
        return False, ["No valid frontmatter"]

    fm_text = m.group(1)
    body = m.group(2)

    changes = []

    # ── Fix body: must start with "# When to use" ──
    body_changed = False
    body_stripped = body.lstrip("\n")
    if not body_stripped.startswith("# When to use"):
        # Don't prepend — instead, replace the first H1 or add it
        # Check if there's already an H1 that's not "When to use"
        body_lines_list = body_stripped.split("\n")
        first_h1_idx = None
        for idx, bl in enumerate(body_lines_list):
            if bl.startswith("# ") and not bl.startswith("## "):
                first_h1_idx = idx
                break

        if first_h1_idx is not None:
            # Replace the first H1 with "# When to use"
            body_lines_list[first_h1_idx] = "# When to use"
            body = "\n".join(body_lines_list)
        else:
            # No H1 at all — prepend "# When to use"
            body = "# When to use\n\n" + body_stripped
        body_changed = True
        changes.append("body: ensured '# When to use' as first H1")

    # ── Fix frontmatter lines ──
    fm_lines = fm_text.split("\n")
    new_fm_lines = []
    i = 0

    while i < len(fm_lines):
        line = fm_lines[i]

        # Fix 1: version: X.Y.Z → version: 'X.Y.Z'
        ver_match = re.match(r"^version:\s*(.+)$", line)
        if ver_match and not re.match(r"""^version:\s*['"]""", line):
            ver_val = ver_match.group(1).strip()
            # Quote it
            new_fm_lines.append(f"version: '{ver_val}'")
            changes.append(f"version: quoted '{ver_val}'")
            i += 1
            continue

        # Fix 2: source: (empty, no value on same line)
        if re.match(r"^source:\s*$", line):
            new_fm_lines.append("source: null")
            changes.append("source: empty → null")
            i += 1
            continue

        # Fix 3: source: followed by stray ref: on next line
        if line.strip() == "source:" and i + 1 < len(fm_lines) and re.match(
            r"^ref:\s+", fm_lines[i + 1]
        ):
            new_fm_lines.append("source: null")
            i += 2  # skip source: and ref:
            changes.append("source: + ref: → source: null")
            continue

        # Fix 4: language: en → remove
        if re.match(r"^language:\s+", line):
            changes.append("language: removed")
            i += 1
            continue

        # Fix 5: description/description_zh: '|' or '>'
        if re.match(r"""^(description(?:_zh)?):\s*['"][|>]['"]\s*$""", line):
            field = re.match(r"""^(description(?:_zh)?):""", line).group(1)
            body_lines = [
                l.strip()
                for l in body.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]
            first_body_line = body_lines[0] if body_lines else "See skill content for details."
            if len(first_body_line) > 200:
                first_body_line = first_body_line[:197] + "..."
            escaped = first_body_line.replace("'", "''")
            new_fm_lines.append(f"{field}: '{escaped}'")
            changes.append(f"{field}: '|'/'>' → '{escaped[:50]}...'")
            i += 1
            continue

        # Fix 6: description/description_zh: multi-line without quotes
        desc_match = re.match(r"^(description(?:_zh)?):\s*(.*)", line)
        if desc_match and not re.match(r"""^(description(?:_zh)?):\s*['"]""", line):
            field = desc_match.group(1)
            value = desc_match.group(2).strip()
            # Check if there's a continuation on the next line
            has_continuation = (
                i + 1 < len(fm_lines)
                and fm_lines[i + 1].startswith("  ")
                and fm_lines[i + 1].strip()
            )
            if has_continuation or not value:
                new_line, next_i = fix_multiline_description(fm_lines, i)
                new_fm_lines.append(new_line)
                changes.append(f"{field}: multi-line → single-line quoted")
                i = next_i
                continue

        # Fix 7: created/updated: YYYY-MM-DD → 'YYYY-MM-DD'
        date_match = re.match(r"^(created|updated):\s*(\d{4}-\d{2}-\d{2})\s*$", line)
        if date_match and not re.match(r"""^(created|updated):\s*['"]""", line):
            field = date_match.group(1)
            date_val = date_match.group(2)
            new_fm_lines.append(f"{field}: '{date_val}'")
            changes.append(f"{field}: quoted date '{date_val}'")
            i += 1
            continue

        new_fm_lines.append(line)
        i += 1

    changed = bool(changes) or body_changed
    if changed:
        new_fm = "\n".join(new_fm_lines)
        new_content = f"---\n{new_fm}\n---\n{body}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return changed, changes


def main():
    total_fixed = 0
    total_changes = 0
    for path in sorted(glob.glob(os.path.join(SKILLS_DIR, "*/SKILL.md"))):
        changed, changes = fix_file(path)
        if changed:
            total_fixed += 1
            total_changes += len(changes)
            rel = os.path.relpath(path, SKILLS_DIR)
            # Show first 3 changes per file
            for c in changes[:3]:
                print(f"  {rel}: {c}")
            if len(changes) > 3:
                print(f"  ... and {len(changes) - 3} more changes")

    print(f"\nTotal: {total_fixed} files fixed, {total_changes} changes made")


if __name__ == "__main__":
    main()
