"""Run a semantic search and pretty-print the top results."""
from __future__ import annotations

import os
import sys

from skill_sdk import SkillClient


def main() -> int:
    base_url = os.environ.get("SKILL_BASE_URL", "http://localhost:8000")
    query = sys.argv[1] if len(sys.argv) > 1 else "React performance optimization hooks"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    with SkillClient(base_url=base_url) as client:
        results = client.search_skills(query=query, limit=limit, min_score=0.5)

        if not results.items:
            print(f"No matches for {query!r}.")
            return 0

        print(f"Top {len(results.items)} results for {query!r}:\n")
        for r in results.items:
            score = f"{r.score:.3f}" if r.score is not None else "  - "
            print(f"  {score}  {r.skill.name}  ({r.skill.slug})")
            print(f"          {r.skill.description[:100]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
