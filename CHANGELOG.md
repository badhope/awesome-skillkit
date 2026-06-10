# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project tries to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
where it makes sense.

## [Unreleased]

### Added

- **Local skill vault, take 1.** The repo used to be a curated
  link list (`catalog/skills.yaml`); now it ships a vault of
  real `skills/<slug>/SKILL.md` files you can drop into Claude /
  Codex / Cursor / Continue. Five hand-written reference skills
  land in this release:
  `pdf-summarizer`, `code-reviewer`, `test-generator`,
  `sql-query-helper`, `commit-message-writer`.
- **`scripts/sources.json`** — first draft of an upstream-fetch
  manifest. All 18 entries are currently `skip: true` because
  upstream `README.md` files turned out not to be SKILL.md-shaped.
  See `SOURCE.md` for what we tried and why.
- **Six Python scripts** under `scripts/`: `fetch-skill.py`,
  `convert-skill.py`, `extend-skill.py`, `validate-skill.py`,
  `install-skill.py`, `bundle-skill.py`. End-to-end pipeline
  for the vault.
- **`skills/_index.yaml`** — auto-generated machine-readable
  index of all valid skills. Re-written by `validate-skill.py`.
- **`SOURCE.md`** — provenance declaration: what's hand-written,
  what's fetched, what was tried and skipped.
- **`docs/`** — `plan.md`, `schema.md`, `extension-rules.md`,
  `frontend-design.md` for the curious contributor.
- **`frontend/`** — Vite + vanilla TypeScript static site.
  Three pages: list (search + filter), detail (markdown render +
  copy/download), bundle (client-side JSZip). Builds to
  ~36 KB gzipped JS. Wired into a Pages workflow.

### Changed

- Repo structure split into `skills/` (the vault) and
  `external-index/` (the old link list, kept for discovery only).
  Old `catalog/` and `data/` directories removed.
- `check-links.py` and `sync-github.py` rewired to point at
  `external-index/`. UA string and `CATALOG` variable renamed
  to drop legacy `catalog` word.
- PULL_REQUEST_TEMPLATE rewritten as two-section (vault entry vs
  external link) so contributors don't accidentally target a
  deleted path.
- `validate-skill.py` now writes a `description` + `name_zh`
  field into the slim index used by the list page, so each card
  shows the one-line summary.

### Fixed

- 5 FAIL items from Phase 1 prosecutor review (`.gitkeep` for
  empty dirs, `bundles/` in `.gitignore`, dead-link issue
  template, PR template, `CATALOG` variable).
- 5 FAIL items from Phase 2 review (`extend-skill.py` actually
  inserts placeholders now, idempotent on `updated`, `_index.yaml`
  no longer has `# #` prefix, three scripts handle out-of-repo
  paths, sync-github has UTF-8 encoding).
- 4 FAIL + 5 WARN items from Phase 4 review: `frontend/.gitignore`
  now ignores the data dumps; detail page puts "When to use"
  before inputs; recursive YAML dumper handles nested objects
  + arrays of objects; `npm run data:sync` points at the real
  Python pipeline; bundle search preserves the checked state;
  the GitHub-only link is hidden on phones; `document.title`
  updates per route.

### Removed

- `catalog/skills.yaml` and `catalog/own_skills.yaml` (moved /
  replaced — see Changed above).
- `data/health.json` (moved to `external-index/health.json`).
- `awesome-list` framing in CITATION.cff / README; this is a
  vault, not a list.
