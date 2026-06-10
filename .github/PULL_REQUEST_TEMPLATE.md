## What

<!-- One-paragraph description of the change. -->
<!-- If you are submitting a new local skill under skills/, say so plainly. -->

## Why

<!-- Motivation. Link any issue this PR fixes (Fixes #123). -->

## Checklist

Pick the section that matches your change. Delete the other one.

### Adding / changing an entry in `external-index/skills.yaml`

- [ ] `slug` is unique and kebab-case
- [ ] `source_url` returns 2xx (link-check CI will verify)
- [ ] `category` matches an existing category in the same file
- [ ] `summary` and `summary_zh` (if present) are each one line
- [ ] I did NOT manually add `stars` / `license` / `pushed_at` / `archived` (sync workflow fills those)
- [ ] I did **not** commit any secrets, tokens, or credentials

### Adding / changing a local skill under `skills/<slug>/SKILL.md`

- [ ] Frontmatter is complete (see `docs/schema.md`)
- [ ] `platforms:` is correct — multi-platform when the skill is generic, a specific platform when it depends on vendor features
- [ ] `needs_review: true` is set if `extend-skill.py` flagged anything
- [ ] `source.url` and `source.commit` point at the upstream commit the file was taken from
- [ ] `validate-skill.py skills/<slug>/SKILL.md` exits 0
- [ ] I did **not** commit any secrets, tokens, or credentials
