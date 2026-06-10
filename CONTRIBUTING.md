# Contributing

Two ways to help:

1. **Add a local skill** under `skills/<slug>/SKILL.md`. This is the main
   product. Most PRs should be this.
2. **Add an external link** to `external-index/skills.yaml`. Discovery
   only. The skill itself has to be fetched separately.

## Adding a local skill

```bash
cp skills/_TEMPLATE.md skills/<your-slug>/SKILL.md
# edit it
python scripts/validate-skill.py skills/<your-slug>/SKILL.md
```

If the file is from upstream, also fill in the `source` block (URL,
commit SHA, license). See `SOURCE.md` for the rules.

If `extend-skill.py` flagged your file with `needs_review: true`,
explain in the PR body what you guessed. Don't silently ship a guess.

## Adding an external link

Append to `external-index/skills.yaml`. Its current schema
(`summary` / `summary_zh`) is the only schema for that file — the
local skill vault (`skills/`) uses a different schema (`description`
/ `description_zh` per `docs/schema.md`), and we don't plan to
migrate one to the other. Keeping them apart avoids re-writing
the sync workflow.

Rules:

- `slug` is unique and kebab-case
- `source_url` returns 2xx
- `category` matches an existing entry in the same file
- Don't add `stars` / `license` / `pushed_at` / `archived` — the sync
  workflow fills those

## Reporting a dead link

Open an issue, use the **Dead link** template. Slug + broken URL +
a sentence of context (renamed? moved? private?).

## Suggesting a new category

Open an issue first. Most entries fit an existing one. New category
needs a reason.

## PR hygiene

- **One skill per PR.** Easier to review, easier to revert.
- **Squash merge.**
- **Don't** commit secrets, tokens, generated bundles, large
  binaries, or somebody else's code without a license.
- Wait for CI green. `validate-skills.yml` runs on every push;
  `check-links.yml` runs on a weekly cron and on manual dispatch.

## License

By contributing, you agree your contribution is licensed under
MIT, the same as the rest of the project. See [LICENSE](./LICENSE).
