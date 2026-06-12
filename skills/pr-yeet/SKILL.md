---
name: Single-Flow PR Yeet
name_zh: 一次性 PR 推送
slug: pr-yeet
description: 在一个线性流程里完成 stage、commit、push、开 PR。仅在用户明确说 yeet 或 ship 时触发。
description_zh: 在一个线性流程里完成 stage、commit、push、开 PR。仅在用户明确说 yeet 或 ship 时触发。
category: dev-tools
tags: [ai, api, frontend, git, llm]
source:
license: MIT
language: en
author: AI-SKILL
version: 1.0.0
created: 2026-06-12
updated: 2026-06-12
needs_review: false
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

The user said "yeet this", "ship it as a PR",
"open a PR for this", "stage, commit, push, and
open the PR", or any equivalent single-flow
request. The flow is: pick a branch → write a
terse commit → push → open the PR. Nothing
fancy.

Use this skill for:

- Linear, single-commit changes
- Fixes / chores / small features that need
  exactly one PR
- A clean way to land a local branch when the
  user wants the whole thing done in one shot

**Do not** use this for:

- Stacked PRs (one PR per commit, branching
  from a chain of branches) — use a stacked-
  PRs workflow
- Repos without GitHub or without `gh` auth —
  pick a different flow
- Multi-commit history that should be squashed
  — the user can ask for a squash-merge
  separately; this skill does not rewrite
  history
- Hotfixes that should bypass review — that
  is a force-push or admin-merge decision, not
  a PR

# Inputs

- `description` — single string that becomes
  branch, commit, and PR title. Required.
- `draft` — open the PR as a draft. Default
  `false`.
- `base_branch` — target branch. Default
  repo's default branch.
- `body_overrides` (optional) — extra sections
  to append to the PR body.

# Output

A `## Plan` block (branch, commit, PR title,
PR body, target branch) and a `## Commands`
block the agent actually runs. On success, the
final PR URL.

# Prompt

```prompt
You are running a single-flow PR: stage, commit,
push, open. Treat it as a four-step pipeline with
no surprises. If any step fails, stop and report
— do not improvise around the failure.

## 0. Prereqs

Before anything else, verify:

  - `gh --version` is on PATH. If not, ask
    the user to install it and stop.
  - `gh auth status` reports an authenticated
    user. If not, ask the user to run
    `gh auth login` and stop.
  - The current directory is a git repo with
    at least one remote that points at
    GitHub.

## 1. Pick the branch and commit

The user gave you a `description` string. Use
it three times, as-is:

  - **Branch name**: `description` (kebab-case
    if multi-word, lower-case). If the
    description contains characters that are
    not safe in branch names (`/`, spaces,
    `?`, `*`, etc.), kebab-case the words
    and strip the rest.
  - **Commit subject**: `description` (terse,
    no trailing period).
  - **PR title**: `description` (same as
    commit, summarizes the full diff).

When starting from `main` / `master` /
`default`, create the branch:

```bash
git checkout -b "<description>"
```

When the user is already on a feature branch
they want to ship, do not create a new one.
Confirm in chat before reusing the current
branch.

## 2. Discover the PR template

Resolve the repo root and look for the active
GitHub PR template:

```bash
repo_root="$(git rev-parse --show-toplevel)"
```

Template candidates, in order:

  - `.github/pull_request_template.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - One `*.md` file under
    `.github/pull_request_template/`
  - One `*.md` file under
    `.github/PULL_REQUEST_TEMPLATE/`

Use paths as emitted from the repo root, e.g.
`.github/pull_request_template.md`, **not**
`./.github/pull_request_template.md`.

If exactly one template is found, read it
before composing the final PR body and pass
it to `gh pr create` with
`--template "$template"`.

If multiple template files are found, stop
before PR creation and ask the user which to
use.

If no template exists, use the fallback body
shape below.

## 3. Stage, commit, push

Stage all tracked changes (don't sweep up
untracked files unless the user explicitly
said so):

```bash
git add -u
git status --short
```

Inspect the staged diff. If it touches more
files than the description implies, stop and
ask. Don't `git add .` blindly.

Commit with the description as the subject:

```bash
git commit -m "<description>"
```

If the commit fails because of a pre-commit
hook, fix the issue the hook flagged, do not
bypass with `--no-verify` unless the user
explicitly asked to.

Push the branch and set upstream:

```bash
git push -u origin HEAD
```

## 4. Open the PR

Construct the body. If a template was found,
use it as the body. Otherwise, use the
fallback body:

```markdown
## What
<one paragraph: what this change does and why>

## How
<bulleted list of the meaningful changes,
ordered by importance, not by appearance>

## Risk
<what could break, who should review, any
follow-up>
```

Append any `body_overrides` after the
template / fallback body, each as a `## `
heading.

Open the PR:

```bash
gh pr create \
  --base "<base_branch>" \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<description>" \
  --body-file <(cat <<'EOF'
<final body>
EOF
) \
  $([ "$draft" = "true" ] && echo --draft)
```

## 5. Output

Print the PR URL at the end. Do not summarize
the diff again — the PR is the artifact.

If any step failed:

  - report which step and the error
  - leave the working tree and branch in a
    state the user can recover from
  - do not retry blindly

## 6. Things this skill explicitly does not do

  - Does not rewrite history (no `git
    rebase`, no force-push, no `git commit
    --amend` of a pushed commit)
  - Does not squash at commit time — the PR
    can be squash-merged by the reviewer
  - Does not create a stacked chain
  - Does not push to multiple remotes
  - Does not handle merge conflicts — if the
    push is rejected, report and stop
  - Does not bypass branch protection rules
    or required reviews
```

# When NOT to use

- **Stacked PRs** — use a stacked workflow
  (Graphite, gh-stack, etc.)
- **Repos without GitHub or `gh`** — the
  skill assumes both. Use the platform's
  native flow.
- **Multi-commit history that must be
  squashed** — squash-merge on the PR
  side, not on the commit side.
- **Hotfixes bypassing review** — that's a
  force-push / admin-merge decision, not a
  PR flow.
- **The user has not said "yeet" / "ship" /
  equivalent** — this is a single-flow skill,
  not the default. Default to a normal
  multi-step review-and-PR flow.
- **The change is WIP and should not be
  reviewed yet** — open as draft with
  `draft=true`, or hold the PR.

# Example

**Input:**

```yaml
description: "fix stripe webhook idempotency"
draft: true
```

**Output (the agent runs):**

```markdown
## Plan
- Branch: `fix-stripe-webhook-idempotency`
- Commit subject: `fix stripe webhook
  idempotency`
- PR title: `fix stripe webhook idempotency`
- Base: `main`
- Template: `.github/pull_request_template.md`
  (found, single file)
- Body: template + Risk section

## Commands (run)
git checkout -b fix-stripe-webhook-idempotency
git add -u
git status --short        # inspected, only
                          # expected files
git commit -m "fix stripe webhook idempotency"
git push -u origin HEAD
gh pr create \
  --base main \
  --head fix-stripe-webhook-idempotency \
  --title "fix stripe webhook idempotency" \
  --body-file .github/pull_request_template.md \
  --draft

## Result
PR opened as draft:
https://github.com/owner/repo/pull/1234
```

The agent prints the URL and stops. No
follow-up summary.
