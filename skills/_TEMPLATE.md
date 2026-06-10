---
# Required fields — see docs/schema.md for full reference.

slug: my-skill                       # kebab-case, matches directory name
name: My Skill                       # display title, sentence case
name_zh: 我的技能                      # optional Chinese title
version: 0.1.0                       # semver
description: One sentence — what it does, for whom.
description_zh: 一句话，干什么、为谁。    # optional Chinese

category: official-cookbooks         # one of the 49 categories in external-index/
tags: [tag1, tag2, tag3]             # 2-5 lowercase tags
# platforms: [claude]                # omit for platform-neutral

inputs:
  - name: pdf_path
    type: path
    required: true
    description: local path to the PDF
  - name: audience
    type: enum
    required: false
    values: [engineer, pm, exec]
    default: pm
    description: who is reading the summary
  - name: length
    type: integer
    required: false
    default: 5
    constraints:
      min: 3
      max: 10
    description: number of bullets in the summary

output:
  format: markdown
  description: |
    `## Summary` with N bullets, then a `## Tags:` line.

author: your-github-handle
license: MIT
created: 2026-06-10
updated: 2026-06-10

# For skills fetched from an upstream repo, also include:
# source:
#   url: https://github.com/owner/repo/tree/main/skills/...
#   fetched_at: 2026-06-10
#   commit: a1b2c3d4
#   license: MIT
#   original_path: skills/foo/SKILL.md

# needs_review: true                # only if extend-skill.py guessed
---

# When to use

A reader wants a 5-bullet summary of a long PDF, written for a
specific audience. Be specific here — "for PDF summarization" is
too vague, "for a 50-page report that an exec needs in 30
seconds" is what we want.

# Inputs

The path to a PDF on disk, the audience, the bullet count. The
audience controls register and vocabulary; the bullet count
controls length.

# Output

Markdown with exactly `length` bullets under `## Summary`, then
a single `## Tags:` line.

# Prompt

```prompt
You are a senior analyst writing for the requested audience.

Voice:
- engineer: precise, technical, uses domain terms
- pm: outcomes-first, no jargon, quantifies where possible
- exec: 1-2 sentences per bullet, decisions and risks only

Process:
1. Read the PDF cover, abstract, intro, conclusion, key tables/figures
2. Identify the 1-3 findings the audience needs to act on
3. Distill to exactly N bullets
4. Order by importance, not by appearance

Output:

## Summary
1. <bullet>
2. <bullet>
…

## Tags
comma, separated, keywords
```

# When NOT to use

- The PDF is under 2 pages — read it directly.
- The reader needs the full text — use `pdf-extractor`.
- The reader needs exact quotes — this skill summarises.

# Example

**Input:**

```
pdf_path: ./q2-roadmap.pdf
audience: exec
length: 4
```

**Output:**

```markdown
## Summary
1. Q2 ships the federated-search rewrite (3× faster, half the
   cluster cost) and deprecates the v1 search API.
2. Hiring lag is the biggest risk: 2 of 4 open roles are still
   unfilled at the half.
3. The board asked about Anthropic vs. OpenAI as a vendor — we
   plan to stay multi-vendor with Bedrock as the primary.
4. ARR is tracking 8% above plan, mostly from the new enterprise
   tier.

## Tags
search, hiring, vendor, arr
```
