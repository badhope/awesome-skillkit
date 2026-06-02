"""Walk the full skill catalog page by page."""
from __future__ import annotations

import os

from skill_sdk import SkillClient


def main() -> int:
    base_url = os.environ.get("SKILL_BASE_URL", "http://localhost:8000")
    page_size = 50

    with SkillClient(base_url=base_url) as client:
        total = 0
        for page in client.iter_skills(page_size=page_size, is_public=True):
            for skill in page.items:
                total += 1
                if total <= 5 or total % 100 == 0:
                    print(f"  [{total:>5}]  {skill.slug}  ({skill.name})")
        print(f"\nTotal public skills: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
