---
name: Code Ownership & Bus Factor
name_zh: 代码所有权与巴士因子
description: 'The user said "build me an ownership map", "what'
description_zh: 从 git 历史里画出一张安全导向的所有权图谱 —— 
  谁拥有哪些文件、谁在维护敏感代码、巴士因子是多少、哪些敏感路径已经无人维护。导出 CSV / JSON 给图数据库（Neo4j / Gephi），再画一张 
  co-change 图给聚类分析用。仅在用户明确要求 AppSec / 巴士因子分析时触发，不接普通 maintainer 列表的活。
category: dev-tools
tags:
  - ai
  - database
  - frontend
  - git
  - javascript
source:
license: MIT
author: 'OpenAI (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: ownership-bus-factor
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
---
# When to use

The user said "build me an ownership map", "what
is the bus factor of the auth service", "find
orphaned sensitive code", "who actually maintains
the crypto module", "I need a CODEOWNERS reality
check for risk", or "show me sensitive code with
no clear owner". The output is a graph of
people-to-files plus a co-change graph of
files-that-move-together, exported to CSV / JSON
/ GraphML for further analysis.

Use this skill for:

- AppSec ownership review (who is on the hook
  for each sensitive file?)
- Bus-factor analysis (how many people
  understand each subsystem?)
- CODEOWNERS reality check (does what CODEOWNERS
  claims match what git history shows?)
- Sensitive-hotspot discovery (which auth /
  crypto / billing files have the fewest recent
  committers?)
- Ownership clustering (which files are
  modified together — a strong signal for
  missing module boundaries)
- Onboarding prep for a new team lead

**Do not** use this for:

- A general maintainer list (use
  `CODEOWNERS` directly)
- A non-security ownership question (use a
  different skill — this one is explicitly
  AppSec-framed)
- A code review of specific changes (use
  `code-review`)
- A repo you cannot read — the skill needs
  `git log` access; if the repo is not local,
  clone it first

# Inputs

- `repo_path` — the repo to analyze.
- `since` / `until` (optional) — commit
  history window. Default: 1 year, ending
  today.
- `sensitivity_rules` (optional) — custom
  sensitivity CSV. If omitted, use defaults.
- `out_dir` (optional) — where to write
  outputs. Default `./ownership-map-out`.

# Output

A `## Pipeline` block (commands to run, in
order), a `## Outputs` block (file map of what
gets written), a `## Sensitivity defaults`
block, and a `## Analysis queries` block with
the JSON queries to ask of the resulting data.

The agent actually runs the pipeline and writes
the files; the output is the result on disk,
not a description of the result.

# Prompt

```prompt
You are building a security-oriented ownership
map of a git repo. The output is a bipartite
graph of people and files from git history,
plus a co-change graph of files-that-move-
together. You will then query the output to
answer AppSec questions.

## 1. Scope

  - **Repo**: the local path the user provided
  - **Time window**: default 1 year, ending
    today. Honor `since` / `until` if set.
  - **Co-change exclusion**: by default,
    ignore common "glue" files so clusters
    reflect actual code movement instead of
    shared infra edits. Default exclude
    patterns: lockfiles (`**/package-lock.json`,
    `**/pnpm-lock.yaml`, `**/yarn.lock`,
    `**/Cargo.lock`, `**/go.sum`, `**/Gemfile.lock`,
    `**/poetry.lock`, `**/composer.lock`),
    `.github/**`, `.gitignore`, `.editorconfig`,
    `CODEOWNERS`. Override with
    `--cochange-exclude`.
  - **Author exclusion**: by default, exclude
    `dependabot[bot]`, `github-actions[bot]`,
    `renovate[bot]`, `snyk-bot`, and any
    commit whose subject starts with
    `chore(deps):`. Override with
    `--no-default-author-excludes` or
    `--author-exclude-regex`.

## 2. Build the ownership map

Run the bundled script with sensible defaults
and write all outputs to `out_dir`:

```bash
python ownership-map.py build \
  --repo "$REPO" \
  --since "$SINCE" \
  --until "$UNTIL" \
  --out "$OUT_DIR" \
  --cochange-max-files 50      # ignore supernode
                                # commits with > 50
                                # files
```

The build command produces:

  - `people.csv` — one row per person with
    their total commits, distinct files,
    tenure
  - `files.csv` — one row per file with its
    primary owner, top-3 contributors,
    commit count, last-touched
  - `people_files.csv` — edges: one row per
    (person, file) with commit count and
    share of the file's history
  - `cochange.csv` — edges: one row per
    (file_a, file_b) with the Jaccard
    similarity of their shared commit set
  - `communities.csv` — one row per file
    with its community id (Louvain
    community detection on the co-change
    graph)
  - `summary.json` — top-level metrics
    (total people, total files, total
    edges, orphan count, median bus factor)

## 3. Graph export (optional but recommended)

Export the graphs for Neo4j / Gephi:

```bash
python ownership-map.py export \
  --in "$OUT_DIR" \
  --graphml
```

This produces:

  - `people_files.graphml` — the bipartite
    graph for direct import
  - `cochange.graphml` — the co-change graph
    for clustering visualization

To load into Neo4j, see the bundled
`references/neo4j-import.md`. The standard
load is a CSV import per file with
`MERGE`-based node / relationship upserts.

## 4. Sensitivity defaults

If `sensitivity_rules` is not provided, use
the built-in defaults. A file matches a rule
if its path matches the git pathspec glob.

  - `auth/**` — category `auth`, "identity,
    session, token, password handling"
  - `**/auth*` — category `auth`, same
  - `**/login*` — category `auth`, same
  - `**/session*` — category `auth`, same
  - `crypto/**` — category `crypto`,
    "cryptographic primitives, key handling"
  - `**/keys*` — category `crypto`, same
  - `payments/**` — category `payments`,
    "money movement, billing, invoicing"
  - `**/billing*` — category `payments`,
    same
  - `secrets/**` — category `secrets`,
    "secret material, vault access"
  - `admin/**` — category `admin`,
    "elevated-privilege operations"
  - `**/rbac*` — category `rbac`, "role
    and permission handling"
  - `**/permission*` — category `rbac`,
    same
  - `payouts/**` — category `payments`,
    same
  - `migrations/**` — category `schema`,
    "database schema, irreversible changes"
  - `**/migrations/*` — category `schema`,
    same

Override any pattern with the custom CSV. The
CSV format is one rule per line:
`pattern,category,description`. Use
`--rules sensitivity.csv` to load.

## 5. Default analysis queries

Run these against the produced JSON / CSV
after the build step. The bundled
`scripts/query_ownership.py` accepts the
same JSON shape and outputs bounded slices.

### Q1. Orphaned sensitive code
Files in a sensitive category with exactly
one recent committer. These are the
single-point-of-failure candidates.

```bash
python query_ownership.py \
  --in "$OUT_DIR" \
  --query orphan-sensitive
```

Expected output: a JSON list of
`{file, category, sole_owner, tenure_days,
last_touched_days}`. Read the list; anything
with `last_touched_days > 365` is a real risk,
not a hot path.

### Q2. Bus factor per subsystem
For each Louvain community, the minimum
number of people whose removal would leave
>50% of the community's files unmaintained.
A bus factor of 1 is a single-person
subsystem; flag everything ≤ 2.

```bash
python query_ownership.py \
  --in "$OUT_DIR" \
  --query bus-factor
```

### Q3. CODEOWNERS reality check
Cross-reference the ownership map against
the repo's `CODEOWNERS`. Report files where
CODEOWNERS names a team but the map shows
zero recent commits from anyone in that
team. This is a "claimed but not actually
owned" finding.

```bash
python query_ownership.py \
  --in "$OUT_DIR" \
  --query codeowners-reality \
  --codeowners CODEOWNERS
```

### Q4. Sensitive hotspots
Files in sensitive categories that have
changed the most in the window. Sensitive
+ hot = the place to focus AppSec review
effort.

```bash
python query_ownership.py \
  --in "$OUT_DIR" \
  --query sensitive-hotspots
```

### Q5. Ownership clusters
For each Louvain community, the top
contributor. Communities with no clear top
contributor are the cross-team
collaboration zones.

```bash
python query_ownership.py \
  --in "$OUT_DIR" \
  --query ownership-clusters
```

## 6. Output

The build step writes all files to
`out_dir`. Summarize in chat:

  - **Total**: N people, M files, K edges
  - **Orphans in sensitive code**: count,
    with the top 3 files
  - **Bus factor 1 subsystems**: count, with
    community ids
  - **CODEOWNERS drift**: count of files
    claimed but not actually owned

If the user asked for a specific question
(Q1-Q5), answer that question with the
specific files / people / community ids, and
save the full report to `ownership_report.md`
next to the outputs.

## 7. Co-change caveats

  - A high co-change score between two files
    is **evidence**, not proof, that they
    belong in the same module. False
    positives: cross-cutting refactors
    (lint fixes, import reorders), generated
    code, vendored deps.
  - A low co-change score between two files
    in the same module is **evidence** that
    the module boundary is wrong, or that
    one file is dead code.
  - Co-change is not a substitute for
    dependency analysis. Two files that
    import each other but never change in
    the same commit have a low co-change
    score.
```

# When NOT to use

- **General maintainer list** — read
  `CODEOWNERS` directly. This skill is for
  the AppSec-framed ownership analysis, not
  the human-org-chart view.
- **Non-security ownership question** — "who
  should I ask about X" is a different
  question. Use a different skill.
- **No access to git history** — the skill
  needs `git log`. Clone the repo first.
- **One specific file** — read the file's
  `git log -- <path>` directly.
- **A code review of specific changes** —
  use `code-review`.
- **A repo with no commits in the window**
  — the analysis is empty. Pick a longer
  window or skip the skill.

# Example

**Input:**

```yaml
repo_path: ./billing-service
since: 2025-06-11
out_dir: ./ownership-billing
```

**Output (the agent runs the pipeline and
reports):**

```markdown
## Pipeline
Ran the build and export steps with the
default sensitivity rules. Time window:
2025-06-11 to 2026-06-11.

## Outputs (in ./ownership-billing/)
- `people.csv` (47 rows)
- `files.csv` (812 rows)
- `people_files.csv` (4,213 rows)
- `cochange.csv` (28,540 rows)
- `communities.csv` (812 rows, 23 communities)
- `summary.json`
- `people_files.graphml` (for Neo4j / Gephi)
- `cochange.graphml` (for clustering viz)

## Findings
- **3 orphaned sensitive files**:
  - `src/crypto/legacy_token.py` — sole
    owner `@maya`, last touched 412 days
    ago. Category: `crypto`. Risk: high.
  - `src/auth/legacy_oauth.py` — sole
    owner `@li`, last touched 287 days
    ago. Category: `auth`. Risk: medium.
  - `src/payouts/manual_reversal.py` —
    sole owner `@sam`, last touched 203
    days ago. Category: `payments`. Risk:
    high.
- **2 subsystems with bus factor 1**:
  - community `c17` (Stripe webhook
    handlers) — 14 files, sole owner
    `@priya`
  - community `c22` (legacy billing
    calculator) — 9 files, sole owner
    `@maya`
- **4 CODEOWNERS drift findings**: 4 files
  claimed by `@team/billing` with zero
  recent commits from anyone in `@team/
  billing` (see `codeowners_drift.csv`).

Full report: `ownership_report.md`.
```

The report cites specific files and
community ids. The agent can be re-run with
different sensitivity rules or a different
window to compare snapshots.
