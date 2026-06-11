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
- 5 QA skills from major OSS projects, fetched and re-templated
  to match this vault's vendor-neutral convention:
  - `pdf-vision-extractor` (`platforms: [claude]`) — first
    Claude-only skill, end-to-end test of the platform chip
    pipeline.
  - `deepeval-otel` — OpenTelemetry trace export to Confident
    AI's Observatory. No deepeval Python package required.
  - `deepeval-tracing` — DeepEval SDK Python `@observe`
    decorator + framework integrations.
  - `deepeval-eval-suite` — end-to-end pytest eval suite with
    DeepEval metrics.
  - `promptfoo-evals` — regression / coverage eval suite
    author for promptfoo.
  - `promptfoo-redteam` — redteam plugin + grader author.
- 5 skills sourced from mainstream big-factory and reference
  repos, genericised to be vendor-neutral and merged into the
  vault template:
  - `mcp-builder` — Anthropic's MCP server authoring guide,
    kept as the canonical reference; covers research, schema,
    implementation, and the 10-question eval set.
  - `webapp-testing` — Playwright + Python harness with
    static-vs-SPA decision tree and black-box server
    lifecycle helper.
  - `llm-pricing-file-update` — genericised from Langfuse's
    `add-model-price` skill; covers matchPattern regex,
    pricing tiers, tokenizer alignment, regex self-check.
  - `realtime-eval-bootstrap` — genericised from OpenAI
    cookbook's bootstrap-realtime-eval; covers harness
    selection (crawl / walk / run), scaffold + smoke + full
    eval validation.
  - `react-router-search-params` — genericised from
    promptfoo's `search-params`; covers the `replace` vs
    `push` decision table, the `useSearchParamState` hook
    pattern, and the `null`-to-clear convention.
- 10 more skills from mainstream big-factory repos, all
  vendor-neutral after de-Langfusing / de-Anthropic-fying:
  - `clickhouse-best-practices` — genericised from Langfuse
    `.agents/skills/clickhouse-best-practices/SKILL.md`;
    preserves the 28 ClickHouse Inc rules (Apache-2.0),
    strips Langfuse-internal TS references. Author is
    "ClickHouse Inc + Langfuse (downstream pack: badhope)".
  - `frontend-large-feature-architecture` — genericised
    from Langfuse; controller / presentational / state-
    location / list-vs-detail / virtualization decision
    table.
  - `security-review` — genericised from Langfuse; SSRF /
    secrets / cross-tenant / RBAC catalog with file:line
    finding format.
  - `storybook` — genericised from Langfuse; CSF Next,
    state-named stories, no MSW rule, presentational
    component rule.
  - `pnpm-upgrade-package` — genericised from Langfuse;
    release-age check, override-prove, dedupe-churn
    rejection, 4 explicit "do not" traps.
  - `turborepo` — genericised from Langfuse; the two
    primary rules (Package Tasks Not Root Tasks / `turbo
    run` not `turbo`) and 8 anti-patterns.
  - `code-review` — genericised from Langfuse; findings-
    first, severity-ordered, defers to specialised skills.
  - `skill-creator` — genericised from Anthropic; the
    loop is the skill (draft / test / evaluate / iterate /
    expand).
  - `doc-coauthoring` — genericised from Anthropic;
    Context Gathering / Refinement & Structure / Reader
    Testing.
  - `internal-comms` — genericised from Anthropic; 7
    comm types, each with structure / tone / gather
    checklist.
- Vault now at 26 skills, all 0/0/0. Total upstream source
  URLs: 20, all HEAD-200 verified. Skipped upstream
  SKILL.md: 23 (Langfuse 11, Anthropic 12) — see SOURCE.md
  for the "skipped and why" inventory.
- 9 more skills sourced from 3 additional mainstream
  big-factory repos (`openai/skills`, `letta-ai/skills`,
  `huggingface/skills`). All vendor-neutralised to match the
  vault's 4-H1 + I/O contract convention:
  - `goal-definition` — genericised from
    `openai/skills/.curated/define-goal`; the
    REWRITE / GOAL two-shape output and the
    quantitative-evidence gate.
  - `cli-builder` — genericised from
    `openai/skills/.curated/cli-creator`; runtime
    selection, command surface sketch before coding,
    default-JSON contract, dry-run / auth / install.
  - `threat-modeling` — from
    `openai/skills/.curated/security-threat-model`;
    repo-grounded trust boundaries + abuse paths
    tied to assets, likelihood × impact, 5-10
    high-quality threats (not 50).
  - `secure-code-by-language` — from
    `openai/skills/.curated/security-best-practices`;
    language / framework reference lookup with
    proactive / passive-detect / full-report modes.
  - `ownership-bus-factor` — from
    `openai/skills/.curated/security-ownership-map`;
    git-history ownership graph + co-change Jaccard
    + Louvain communities + 5 default analysis
    queries.
  - `pr-yeet` — from
    `openai/skills/.curated/yeet`; the four-step
    stage → commit → push → open flow with
    PR-template discovery.
  - `frontend-visual-design` — from
    `letta-ai/skills/tools/frontend-skill`; visual
    thesis + content plan + interaction thesis,
    Beautiful Defaults, anti-pattern catalog
    (pill soup, card-stack hero, etc.).
  - `browser-ml-in-js` — from
    `huggingface/skills/transformers-js`; pipeline
    API + device selection + mandatory
    `pipe.dispose()` + Web Worker pattern for
    browsers.
  - `embedding-model-training` — from
    `huggingface/skills/train-sentence-transformers`;
    bi-encoder / cross-encoder / sparse-encoder
    training router with loss + evaluator + base
    model selection and the training-time
    footguns.
- Vault now at 35 skills, all 0/0/0. Total upstream
  source URLs: 29, all HEAD-200 verified. New
  upstream vendors: `openai/skills` (6),
  `letta-ai/skills` (1), `huggingface/skills` (2).
  Per-vendor skipped inventory: 17 Hugging Face
  (HF-platform-specific) + 41 Letta (Letta-SDK-
  and single-tool-specific) + 33 OpenAI skills
  (Codex/single-tool-specific).

### Removed

- `catalog/skills.yaml` and `catalog/own_skills.yaml` (moved /
  replaced — see Changed above).
- `data/health.json` (moved to `external-index/health.json`).
- `awesome-list` framing in CITATION.cff / README; this is a
  vault, not a list.
