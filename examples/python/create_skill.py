"""Create a new skill with categories and tags."""
from __future__ import annotations

import asyncio
import os

from skill_sdk import SkillClient, SkillError


async def main() -> int:
    base_url = os.environ.get("SKILL_BASE_URL", "http://localhost:8000")
    email = os.environ.get("SKILL_EMAIL", "you@example.com")
    password = os.environ.get("SKILL_PASSWORD", "SuperSecret123!")

    async with SkillClient(base_url=base_url) as client:
        await client.login_async(email=email, password=password)

        # Look up the frontend category id
        categories = await client.list_categories_async()
        frontend = next(c for c in categories if c.slug == "frontend")
        print(f"Frontend category: {frontend.id}")

        # Create the skill
        try:
            skill = await client.create_skill_async(
                name="React useMemo deep-dive",
                slug="react-usememo-deep-dive",
                description="A practical guide to React useMemo with examples",
                content="# React useMemo\n\nuseMemo lets you cache...",
                category_id=frontend.id,
                tags=["react", "performance"],
                version="1.0.0",
                is_public=True,
            )
            print(f"✓ Created skill: {skill.slug}  id={skill.id}")
        except SkillError as e:
            if e.status_code == 409:
                print(f"… skill already exists")
            else:
                raise
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
