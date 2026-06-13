---
name: PNPM Upgrade Package
name_zh: pnpm 升级依赖
description: 'You''re bumping a dependency in a **pnpm workspace**.'
description_zh: '把 pnpm workspace 依赖升级到目标或最新版本 —— 直系与传递依赖 bump、发布时效检查、作用域 override、lockfile 与 dedupe 校验。覆盖四个"不要"陷阱：手编 lockfile、永久 override、静默升级 latest、dedupe 引入无关 churn。'
category: dev-tools
tags:
  - ai
  - api
  - cli
  - deployment
  - documentation
source: null
license: MIT
author: 'Langfuse (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: pnpm-upgrade-package
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

You're bumping a dependency in a **pnpm workspace**.
Maybe a security advisory, maybe a feature, maybe a
client wants the new version. The "just `pnpm up`"
approach is wrong in three ways:

1. **`pnpm up` will pick latest** unless you pin
   the version. The user asked for `14.2.0`; they
   didn't ask for whatever shipped at 3am.
2. **Transitive deps don't always move** with
   `pnpm up`. A bump to `next@15` may not move
   `react` if your direct deps already allow the
   old range. The bump is then silently incomplete.
3. **Lockfile churn from dedupe** can hide the real
   change. After `pnpm dedupe`, the diff includes
   unrelated package moves that obscure the upgrade.

This skill is a deterministic, step-by-step procedure
that avoids all three. Read the steps, follow them,
report the outcome.

**Don't use this skill for** npm / yarn / bun. And
don't use it for a brand-new package install (use
`pnpm add`).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `package` | yes | The package to upgrade. |
| `target_version` | no | If absent, ask. Never assume latest. |
| `workspace_filter` | no | Scopes the bump. |
| `release_age_window_days` | no | Override `minimumReleaseAge` from `pnpm-workspace.yaml`. |

# Output

Plain-text recipe:

```
Steps run:
  1. node check-release-age-window.mjs <pkg> <ver>  → pass
  2. pnpm why -r <pkg>  → transitive source: web > next@14
  3. pnpm -w up <pkg>@<ver>  → manifest + lockfile updated
  4. pnpm dedupe  → clean (no unrelated churn)
  5. pnpm why -r <pkg>  → only <ver> remains
  6. pnpm -r --filter !docs test  → 412 passed, 0 failed

Manifest diffs:
  - package.json: next 14.2.0 → 14.2.18

Release age check: pass (<pkg> <ver> is 4 days old,
  > 3-day minimum)

Lockfile diff: 28 lines

Dedupe outcome: clean

Final pnpm why: web → next@14.2.18, no other consumers
```

# Prompt

```prompt
You are upgrading a pnpm workspace dependency. Follow
the order; do not skip the release-age check; do not
silently upgrade to latest.

1. Ask for the missing inputs.

   Required: package name.
   Optional: target version.
   If the user gave only the package, ask for the
   target version. If they said "upgrade X to latest",
   resolve the latest from the registry and confirm
   before bumping.

2. Run the release-age check.

   The project's `pnpm-workspace.yaml` defines
   `minimumReleaseAge` (a cooldown in days for newly
   published versions). Run:

     node <skill>/scripts/check-release-age-window.mjs \
       <package> <targetVersion>

   The script reads `pnpm-workspace.yaml` and reports
   whether the target version satisfies the cooldown.
   Three outcomes:
     - pass: target is older than the window
     - blocked: target is newer than the window
     - ambiguous: version doesn't exist on registry

   If blocked, do NOT proceed without an explicit
   `minimumReleaseAgeExclude` entry. Ask the user
   before adding one.

3. Find the direct consumer.

   Run:
     pnpm why -r <package>

   This shows which top-level dep brings <package> in.
   If <package> is not directly declared anywhere, the
   answer is "transitive via <parent>".

4. Decide: bump direct or parent.

   - If <package> is directly declared in some
     workspace: bump the direct.
   - If <package> is transitive via <parent>:
       - Check whether the parent's range already
         covers the target version. If yes, prefer
         a lockfile refresh (delete node_modules,
         `pnpm install`) over a manifest change.
       - If not, upgrade the parent (and any peer
         cousins the parent requires).

   Do not add a direct declaration for a package
   that is transitive unless the user explicitly
   wants that.

5. Apply the bump.

   - Root workspace only: `pnpm -w up <pkg>@<ver>`
   - One workspace: `pnpm --filter <name> up <pkg>@<ver>`
   - All workspaces that should move together:
     `pnpm -r up <pkg>@<ver>`

   If a scoped `pnpm-workspace.yaml` `overrides` entry
   is needed (target is transitive, parent range is
   too tight, and the user wants to pin the version
   globally), add it TEMPORARILY. The override is
   removed in step 7.

6. Run `pnpm dedupe`.

   Always run `pnpm dedupe` after a manifest change.
   Inspect the diff. If dedupe introduces unrelated
   churn (moves to packages not touched by the
   upgrade), revert that specific change. The dedupe
   pass is meant to clean up the upgrade, not to be
   a stealth general refactor.

7. Prove the override (if any) is still required.

   If you added a scoped override in step 5:
     a) Remove the override.
     b) Run `pnpm install`.
     c) Run `pnpm why -r <pkg>` and check whether the
        target version remains.
     d) If yes, do NOT keep the override. Restore
        the original `pnpm-workspace.yaml`.
     e) If no (pnpm reverts or drifts), keep the
        override.

   Most of the time, the override is unnecessary. The
   point of the check is to avoid permanent overrides
   that rot.

8. Run the test suite.

     pnpm -r --filter !docs test

   (Adjust the filter to your project's convention.)
   0 failures is required before declaring done.

9. Final `pnpm why`.

     pnpm why -r <pkg>

   Confirm only the intended version remains. If a
   stale version lingers, identify the parent and
   decide whether to bump it or accept the staleness.
```

# When NOT to use

- **The package manager is npm, yarn, or bun.** Use
  the manager-specific upgrade procedure.
- **The user said "upgrade to latest" and that's
  genuinely what they want.** Resolve the latest,
  confirm, then run the upgrade. Don't pretend
  "latest" was not specified.
- **You skip the release-age check.** The check
  protects the project from a bad release that
  was published 2 hours ago. Skipping it is a
  silent footgun.
- **You add a direct declaration for a transitive
  package.** That's a sign you didn't read the
  consumer map. Either the parent's range already
  covers the target (lockfile refresh) or the
  parent needs a bump.
- **You keep a permanent scoped override.** The
  override is a temporary resolution tool. If the
  bump holds without it, remove it. Permanent
  overrides rot and surprise the next upgrade.
- **You hand-edit `pnpm-lock.yaml`.** Never. The
  lockfile is regenerated by pnpm. If a `pnpm`
  command produces unrelated churn, fix the
  command, not the lockfile.
- **You accept dedupe churn as "free refactoring".**
  Dedupe diffs must be inspected. Unrelated
  package moves obscure the upgrade and bloat
  the PR diff. Revert unrelated churn.
- **You upgrade `<parent>` to satisfy the target
  when the parent range already covers it.** A
  parent bump is a separate decision. Resolve
  the lockfile first.
- **You skip the test run.** The version bump
  may have broken a peer assumption. The test
  suite is the cheapest way to catch it.

# Example

**Input:**

```yaml
package: next
target_version: 14.2.18
workspace_filter: "--filter web"
```

**Output:**

```
Steps run:
  1. node check-release-age-window.mjs next 14.2.18
     → pass (5 days old, > 3-day minimum)
  2. pnpm why -r next
     → direct declaration in web
  3. pnpm --filter web up next@14.2.18
     → web/package.json: next 14.2.0 → 14.2.18
  4. pnpm dedupe
     → clean (3 lines deduped, all related)
  5. pnpm -r --filter !docs test
     → 412 passed, 0 failed
  6. pnpm why -r next
     → web → next@14.2.18 (only consumer)

Manifest diffs:
  - web/package.json: next 14.2.0 → 14.2.18

Release age check: pass

Lockfile diff: 6 lines

Dedupe outcome: clean
```
