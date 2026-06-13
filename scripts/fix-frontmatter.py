#!/usr/bin/env python3
"""Batch-fix common SKILL.md frontmatter issues.

Fixes:
1. description: '|' → use first meaningful body line
2. source: followed by ref: main → source: null (remove stray ref)
3. language: en → remove (not a schema field)
"""
import os
import re
import glob

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


def fix_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not m:
        return False

    fm_text = m.group(1)
    body = m.group(2)

    fm_lines = fm_text.split("\n")
    new_fm_lines = []
    i = 0
    changed = False

    while i < len(fm_lines):
        line = fm_lines[i]

        # Fix 1: description: '|' or description: ">" or description: "|"
        # (YAML literal/folded block markers used as literal values)
        if re.match(r"""^description:\s*['"][|>]['"]\s*$""", line):
            # Get first meaningful line from body
            body_lines = [
                l.strip()
                for l in body.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]
            first_body_line = body_lines[0] if body_lines else "See skill content for details."

            # Truncate if too long
            if len(first_body_line) > 200:
                first_body_line = first_body_line[:197] + "..."

            # Escape single quotes
            escaped = first_body_line.replace("'", "''")
            new_fm_lines.append(f"description: '{escaped}'")
            changed = True
            i += 1
            continue

        # Fix 2: source: followed by ref: main on next line (not indented)
        if line.strip() == "source:" and i + 1 < len(fm_lines) and re.match(
            r"^ref:\s+", fm_lines[i + 1]
        ):
            new_fm_lines.append("source: null")
            # Skip the ref: line
            i += 2
            changed = True
            continue

        # Fix 3: Remove language: en (extra field, not in schema)
        if re.match(r"^language:\s+", line):
            changed = True
            i += 1
            continue

        new_fm_lines.append(line)
        i += 1

    if changed:
        new_fm = "\n".join(new_fm_lines)
        new_content = f"---\n{new_fm}\n---\n{body}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed_count = 0
    for path in sorted(glob.glob(os.path.join(SKILLS_DIR, "*/SKILL.md"))):
        if fix_file(path):
            fixed_count += 1
            print(f"Fixed: {path}")
    print(f"\nTotal fixed: {fixed_count} files")


if __name__ == "__main__":
    main()
