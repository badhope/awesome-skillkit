---
name: Turborepo Monorepo Authoring
name_zh: Turborepo Monorepo 编写
description: 'You have a **Turborepo monorepo** and you''re doing one of'
description_zh: 'Turborepo monorepo 构建系统指南 —— 包任务与根任务、task 流水线、dependsOn、缓存、远程 cache、--filter、--affected、环境变量、内部包、边界。覆盖八个让 Turborepo 并行失效的反模式。'
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - frontend
source: null
license: MIT
author: 'Langfuse (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: turborepo
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

You have a **Turborepo monorepo** and you're doing one of
ten things to it: configuring a task, debugging cache
misses, running only changed packages, filtering packages,
fixing environment variables, setting up CI, starting
watch/dev mode, creating a new internal package, deciding
the repo structure, or enforcing architectural boundaries.

The skill is built around two primary rules and eight
anti-patterns. The two rules are non-negotiable:

1. **Package Tasks, Not Root Tasks.** Tasks belong in each
   package's `package.json`. The root `package.json` only
   delegates via `turbo run <task>`. Putting task logic in
   the root `package.json` defeats Turborepo's parallelization.
2. **`turbo run`, not `turbo`.** Always use the explicit
   `turbo run` form in `package.json` scripts, CI
   workflows, and any code path. The shorthand `turbo
   <task>` is for human-typed terminal commands only.

If you violate either, every other Turborepo feature is
moot — the parallelism is gone, the cache is wrong,
remote cache is broken, and `--affected` cannot find the
right packages.

**Don't use this skill for** npm workspaces without
Turborepo, Nx monorepos, or Bazel. The build graph
paradigm is different.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `task` | yes | One of the 10 tasks above. |
| `package_filter` | no | `--filter` value. |
| `base_branch` | no | For `--affected`. Default: repo default. |

# Output

Plain-text answer. Typical return:

```
Command: turbo run build --filter=web...
Config: { "tasks": { "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] } } }
Anti-pattern: don't put `cd apps/web && next build` in root package.json
Reference: references/configuration/tasks.md
```

# Prompt

```prompt
You are working in a Turborepo monorepo. Apply the two
primary rules first; do not skip the anti-patterns.

1. PRIMARY RULE — Package tasks, not root tasks.

   Every task's logic lives in the relevant package's
   `package.json`. The root `package.json` ONLY
   delegates via `turbo run <task>`.

   DO:
     apps/web/package.json:
       { "scripts": { "build": "next build", "lint": "eslint .", "test": "vitest" } }
     apps/api/package.json:
       { "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }
     packages/ui/package.json:
       { "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }
     turbo.json:
       { "tasks": { "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] }, ... } }
     root package.json:
       { "scripts": { "build": "turbo run build", "lint": "turbo run lint", "test": "turbo run test" } }

   DO NOT:
     root package.json:
       { "scripts": { "build": "cd apps/web && next build && cd ../api && tsc", ... } }

   Root Tasks (`//#taskname`) are for the rare case a
   task truly cannot live in a package. Default to
   package tasks.

2. PRIMARY RULE — Use `turbo run`, not `turbo`.

   In code (package.json, CI, scripts), always use
   `turbo run`. The shorthand is for terminal use.

   package.json:        "build": "turbo run build"
   GitHub Actions:      - run: turbo run build --affected
   Turbo shorthand:     ONLY for one-off terminal commands
                        typed by humans or agents

3. Walk the decision tree for the user's task.

   Configure a task?
     - dependencies: references/configuration/tasks.md
     - lint/check-types: use the Transit Nodes pattern
     - outputs: references/configuration/tasks.md#outputs
     - env vars: references/environment/RULE.md
     - watch: references/configuration/tasks.md#persistent
     - global: references/configuration/global-options.md

   Cache not working?
     - outputs not restored: missing `outputs` key
     - unexpected misses: references/caching/gotchas.md
     - debug hash: --summarize or --dry
     - skip cache: --force or cache: false
     - remote cache: references/caching/remote-cache.md
     - env causes misses: references/environment/gotchas.md

   Run only changed packages?
     - DEFAULT: turbo run build --affected
     - custom base: --affected --affected-base=origin/develop
     - manual: --filter=...[origin/main]
     - see all: references/filtering/RULE.md

   Filter packages?
     - by name: --filter=web
     - by directory: --filter=./apps/*
     - + deps: --filter=web...
     - + dependents: --filter=...web
     - complex: references/filtering/patterns.md

   Env vars not working?
     - vars not at runtime: strict mode (default)
     - cache hits with wrong env: var not in `env` key
     - .env changes not rebuilding: .env not in `inputs`
     - CI vars missing: references/environment/gotchas.md
     - framework vars: auto-included via inference

   CI setup?
     - GitHub Actions: references/ci/github-actions.md
     - Vercel: references/ci/vercel.md
     - remote cache: references/caching/remote-cache.md
     - only changed: --affected
     - skip when no changes: turbo-ignore

   Watch / dev?
     - re-run on change: turbo watch
     - dev servers with deps: `with` key
     - restart on dep change: interruptible: true
     - persistent: persistent: true

   Create / structure a package?
     - internal package: references/best-practices/packages.md
     - repo structure: references/best-practices/structure.md
     - dep management: references/best-practices/dependencies.md
     - JIT vs compiled: references/best-practices/packages.md#compilation-strategies
     - sharing code: references/best-practices/RULE.md#package-types

   Repo structure?
     - apps/ vs packages/: references/best-practices/RULE.md
     - package types: references/best-practices/RULE.md#package-types
     - TS config: references/best-practices/structure.md#typescript-configuration
     - ESLint: references/best-practices/structure.md#eslint-configuration
     - deps: references/best-practices/dependencies.md
     - boundaries: references/boundaries/RULE.md

   Enforce boundaries?
     - check: turbo boundaries
     - tags: references/boundaries/RULE.md#tags
     - restrict imports: references/boundaries/RULE.md#rule-types
     - prevent file imports: references/boundaries/RULE.md
```

# When NOT to use

- **The repo is not a Turborepo monorepo.** Use the
  build system you're on (npm workspaces, Nx, Bazel,
  Rush, Lerna).
- **You put a task's logic in the root `package.json`.**
  This is the #1 Turborepo anti-pattern. Tasks belong
  in each package; the root only delegates via `turbo
  run`.
- **You write `turbo build` (shorthand) into a script
  or CI step.** Always `turbo run build`. The shorthand
  is for one-off terminal commands.
- **You use `&&` to chain Turborepo tasks.** Let Turborepo
  orchestrate via `dependsOn`. Chaining forces serial
  execution and breaks the cache graph.
- **You add a task without specifying `outputs`.** The
  cache cannot restore what it does not know exists.
  The default for `build` is `dist/**`; the default for
  `test` is usually nothing. Be explicit.
- **You use `cache: false` to "fix" a cache miss.** That
  is the wrong fix. Find the missing `outputs` / `inputs`
  / `env` key. Disabling the cache removes the feature.
- **You use `--filter=...` (with the trailing dots)
  when you wanted `--filter=...` meaning dependents.**
  The three dots AFTER the package = dependents
  (upstream consumers). The three dots BEFORE the package
  = dependencies. Wrong direction wastes a CI run.
- **You hand-edit `turbo.json` and forget to set
  `cacheDir` / `daemon` globally.** Both are sane
  defaults; the daemon keeps the build warm.
- **You skip the boundary check.** A monorepo without
  boundary enforcement is a code dump with a
  `package.json` on top. Run `turbo boundaries` in CI.

# Example

**Input:**

```yaml
task: run-changed
base_branch: origin/main
```

**Output:**

```
Command: turbo run build lint test --affected --affected-base=origin/main
Config (turbo.json):
  {
    "tasks": {
      "build":  { "dependsOn": ["^build"], "outputs": ["dist/**"] },
      "lint":   { "outputs": [] },
      "test":   { "dependsOn": ["build"], "outputs": ["coverage/**"] }
    }
  }
Anti-pattern:
  - do NOT use `turbo build` shorthand in CI
  - do NOT chain with && — let turbo orchestrate
  - do NOT use --force as a default; --affected is the
    way to scope to changes
Reference: references/filtering/RULE.md
```
