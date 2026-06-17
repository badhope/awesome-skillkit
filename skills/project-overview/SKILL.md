---
name: project-overview
name_zh: project-overview
description: 'LobeHub open-source monorepo architecture map. Use when locating code
  layers, understanding apps/packages/src layout, business stubs, project structure,
  or onboarding to the repository.'
description_zh:
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
needs_review: false
slug: project-overview
version: '1.0.0'
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
author: AI-SKILL
license: MIT
---
# When to use

Use this skill when you need guidance on project-overview.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# LobeHub Project Overview

> The directory listings below are a **curated map of key locations**, not an
> exhaustive tree. `packages/`, `src/store/`, route groups etc. grow over time —
> run `ls` against the real directory for the current set.

## Project Description

Open-source, modern-design AI Agent Workspace: **LobeHub** (previously LobeChat).
This repo is the **open-source root** (`github.com/lobehub/lobehub`, package `@lobehub/lobehub`).

**Supported platforms:**

- Web desktop/mobile
- Desktop (Electron) — `apps/desktop`
- Mobile app (React Native) — **separate repo, already launched** (not in this monorepo)

**Logo emoji:** 🤯

## Complete Tech Stack

| Category      | Technology                                 |
| ------------- | ------------------------------------------ |
| Framework     | Next.js 16 + React 19                      |
| Routing       | SPA inside Next.js with `react-router-dom` |
| Language      | TypeScript                                 |
| UI Components | `@lobehub/ui`, antd                        |
| CSS-in-JS     | antd-style                                 |
| Icons         | lucide-react, `@ant-design/icons`          |
| i18n          | react-i18next                              |
| State         | zustand                                    |
| URL Params    | nuqs                                       |
| Data Fetching | SWR                                        |
| React Hooks   | aHooks                                     |
| Date/Time     | dayjs                                      |
| Utilities     | es-toolkit                                 |
| API           | TRPC (type-safe)                           |
| Database      | Neon PostgreSQL + Drizzle ORM              |
| Testing       | Vitest                                     |

> Exact versions live in the root `package.json` — check there, not here.

## Monorepo Layout

Flat layout — `apps/`, `packages/`, and `src/` all sit at the repo root. No
git submodules.

```
(repo root)
├── apps/
│   ├── cli/                  # LobeHub CLI
│   ├── desktop/              # Electron desktop app
│   ├── device-gateway/       # Device gateway service
│   └── server/               # Next.js-backed server: featureFlags, globalConfig, modules, routers, services, utils, workflows (`@/server/*` alias)
├── docs/                     # changelog, development, self-hosting, usage
├── locales/                  # en-US, zh-CN, ...
├── packages/                 # ~80 @lobechat/* workspace packages — `ls` for the full set. Key ones:
│   ├── agent-runtime/        # Agent runtime core
│   ├── agent-signal/         # Agent Signal pipeline
│   ├── agent-tracing/        # Tracing / snapshots
│   ├── builtin-tool-*/       # Per-tool packages (calculator, web-browsing, claude-code, ...)
│   ├── builtin-tools/        # Central registries that compose builtin-tool-*
│   ├── context-engine/
│   ├── database/             # src/{models,schemas,repositories}
│   ├── model-bank/           # Model definitions & provider cards
│   ├── model-runtime/        # src/{core,providers}
│   ├── business/             # Open-source stubs (config, const, model-bank, model-runtime) — overridden by cloud
│   ├── types/
│   └── utils/
└── src/
    ├── app/
    │   ├── (backend)/        # api, f, market, middleware, oidc, trpc, webapi
    │   ├── spa/              # SPA HTML template service
    │   └── [variants]/(auth)/ # Auth pages (SSR required)
    ├── routes/               # SPA page segments (thin — delegate to features/)
    │   └── (main)/ (mobile)/ (desktop)/ (popup)/ onboarding/ share/
    ├── spa/                  # SPA entries + router config
    │   ├── entry.{web,mobile,desktop,popup}.tsx
    │   └── router/
    ├── business/             # Open-source stubs (client/server) — cloud repo provides real impls
    ├── features/             # Domain business components
    ├── store/                # ~30 zustand stores — `ls` for the full set
    ├── server/               # standalone-Hono server pieces only: agent-hono, workflows-hono (main backend lives in `apps/server`)
    └── ...                   # components, hooks, layout, libs, locales, services, types, utils
```

## Architecture Map

| Layer            | Location                                                 |
| ---------------- | -------------------------------------------------------- |
| UI Components    | `src/components`, `src/features`                         |
| SPA Pages        | `src/routes/`                                            |
| React Router     | `src/spa/router/`                                        |
| Global Providers | `src/layout`                                             |
| Zustand Stores   | `src/store`                                              |
| Client Services  | `src/services/`                                          |
| REST API         | `src/app/(backend)/webapi`                               |
| tRPC Routers     | `apps/server/src/routers/{async\|lambda\|mobile\|tools}` |
| Server Services  | `apps/server/src/services` (can access DB)               |
| Server Modules   | `apps/server/src/modules` (no DB access)                 |
| Feature Flags    | `apps/server/src/featureFlags`                           |
| Global Config    | `apps/server/src/globalConfig`                           |
| DB Schema        | `packages/database/src/schemas`                          |
| DB Model         | `packages/database/src/models`                           |
| DB Repository    | `packages/database/src/repositories`                     |
| Third-party      | `src/libs` (analytics, oidc, etc.)                       |
| Builtin Tools    | `packages/builtin-tool-*`, `packages/builtin-tools`      |
| Open-source stub | `src/business/*`, `packages/business/*` (this repo)      |

## Data Flow

```
React UI → Store Actions → Client Service → TRPC Lambda → Server Services → DB Model → PostgreSQL
```

## Note: Relationship to the Cloud Repo

This open-source repo is consumed by a **separate, private cloud (SaaS) repo**
as a git submodule mounted at `lobehub/`. The cloud repo provides:

- **`src/business/{client,server}`** and **`packages/business/*`** implementations
  that override the stubs shipped here.
- Cloud-only routes (e.g. `(cloud)/`, `embed/`), cloud-only stores (e.g.
  `subscription/`), cloud-only TRPC routers (billing, budget, risk control, …),
  and Vercel cron routes under `src/app/(backend)/cron/`.
- File-resolution order in cloud: `@/store/x` → cloud `src/store/x` first, then
  `lobehub/packages/store/src/x`, then `lobehub/src/store/x`. **Cloud override wins.**

When working in this repo alone, ignore the cloud layer — the stubs in
`src/business/` and `packages/business/` are the source of truth here.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.
