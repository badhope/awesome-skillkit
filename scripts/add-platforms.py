#!/usr/bin/env python3
"""Add platforms field + body disclaimer to platform-specific skills."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# slug → (platforms, disclaimer_line)
PLATFORM_SKILLS = {
    "pdf-vision-extractor": (
        "claude",
        None,  # already has **Claude-only** in body
    ),
    "claude-api": (
        "claude",
        "> **Claude-only** — this skill references Claude API / Anthropic SDK specifics.",
    ),
    "migrate-to-codex": (
        "codex",
        "> **Codex-only** — this skill migrates artifacts into OpenAI Codex format.",
    ),
}


def add_platforms(path: Path, platform: str, disclaimer: str | None) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)(.*)$', text, re.DOTALL)
    if not m:
        return False
    fm = m.group(2)
    body = m.group(4)

    # Add platforms field if not present
    if "platforms:" not in fm:
        # Insert before needs_review or before source, or at end
        if "needs_review:" in fm:
            fm = re.sub(
                r'^(needs_review:.*$)',
                f'platforms:\n  - {platform}\n\\1',
                fm,
                count=1,
                flags=re.MULTILINE,
            )
        elif "source:" in fm:
            fm = re.sub(
                r'^(source:.*$)',
                f'platforms:\n  - {platform}\n\\1',
                fm,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            fm += f"\nplatforms:\n  - {platform}"
    else:
        return False  # already has platforms

    # Add disclaimer to body if needed
    if disclaimer and disclaimer not in body:
        # Insert after the first H1 line
        lines = body.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = i + 1
                break
        # Skip blank lines after H1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, disclaimer)
        lines.insert(insert_at + 1, "")
        body = "\n".join(lines)

    new_text = m.group(1) + fm + m.group(3) + body
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    for slug, (platform, disclaimer) in PLATFORM_SKILLS.items():
        path = REPO / "skills" / slug / "SKILL.md"
        if not path.exists():
            print(f"  SKIP  {slug}: not found")
            continue
        if add_platforms(path, platform, disclaimer):
            print(f"  OK    {slug:30s} → platforms: [{platform}]")
        else:
            print(f"  SAME  {slug:30s} (already has platforms)")


if __name__ == "__main__":
    main()
