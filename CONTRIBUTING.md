# Contributing to AI-SKILL

Thanks for helping improve the catalog. This repo is one YAML file
plus two helper scripts — contributions are straightforward.

## Adding an external skill

1. Fork the repo.
2. Append a new entry under `skills:` in `catalog/skills.yaml`.
3. Follow the entry schema (see README).
4. Open a PR.

Rules:

- `slug` must be unique (kebab-case).
- `source_url` must return 2xx (the link-check CI will verify).
- `category` must be one of the 49 defined categories.
- `summary` and `summary_zh` each one line.
- Don't add `stars`, `license`, `pushed_at`, or `archived` manually —
  the sync workflow fills those within a day after merge.

## Reporting a dead link

Open an issue with the slug and the current `source_url`. We'll fix
or remove the entry.

## Suggesting a new category

Open an issue first. New categories need a reason — most entries fit
an existing one.

## Publishing your own skill

See `skills/README.md` for the in-repo skill format.

## PR process

- Squash merge only.
- One entry per PR is preferred (easier to review).
- The CI workflows run automatically; wait for green before merging.
- Don't commit secrets, generated build output, large binaries, or
  someone else's code without a license.

## License

By contributing, you agree your contribution is licensed under the same
license as the rest of the project. See [LICENSE](./LICENSE).
