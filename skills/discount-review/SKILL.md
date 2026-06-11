---
name: discount-review
description: Inspect the discount policy fixture with a repeatable review 
  checklist and helper script.
slug: discount-review
version: 0.1.0
category: uncategorized
tags:
  - needs-tagging
inputs: []
output:
  format: markdown
author: unknown
license: UNKNOWN
created: '2026-06-11'
updated: '2026-06-11'
needs_review: true
---
Use this skill when asked to review the discount-policy fixture under `skill_fixture/repo`.

1. Do not enumerate this skill directory; the workflow below is complete.
2. Run `python3 skills/discount-review/scripts/analyze_discount_policy.py skill_fixture/repo`.
3. Use the helper output as the source of truth for ticket id, severity, owner, primary file, and minimal fix.
4. Inspect `skill_fixture/repo/src/discount_policy.py` before answering.
5. Return a concise maintainer report that includes the helper command you ran.
