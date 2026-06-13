---
name: spa-routes
name_zh: spa-routes
description: 'LobeHub SPA route architecture. Use when editing src/routes, src/features'
description_zh: 'LobeHub SPA route architecture. Use when editing src/routes, src/features'
category: dev-tools
tags:
  - ai
  - api
  - backend
  - frontend
  - git
source: null
needs_review: false
slug: spa-routes
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

Use this skill when you need to work with spa-routes.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks. Ensure you understand the requirements and constraints before proceeding.

# SPA Routes and Features Guide

SPA structure:

- **`src/spa/`** – Entry points (`entry.web.tsx`, `entry.mobile.tsx`, `entry.desktop.tsx`) and router config (`router/`). Router lives here to avoid confusion with `src/routes/`.
- **`src/routes/`** – Page segments only (roots).
- **`src/features/`** – Business logic and UI by domain.

This project uses a **roots vs features** split: `src/routes/` only holds page segments; business logic and UI live in `src/features/` by domain.

**Agent constraint — desktop router parity:** Edits to the desktop route tree must update **both** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` in the same change (same paths, nesting, index routes, and segment registration). Updating only one causes drift; the missing tree can fail to register routes and surface as a **blank screen** or broken navigation on the affected build.

## When to Use This Skill

- Adding a new SPA route or route segment
- Defining or refactoring layout/page files under `src/routes/`
- Moving route-specific components or logic into `src/features/`
- Deciding where to put a new component (route folder vs feature folder)

---

## 1. What Belongs in `src/routes/` (roots)

Each route directory should contain **only**:

| File / folder                                 | Purpose                                                                                                                                                      |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `_layout/index.tsx` or `layout.tsx`           | Layout for this segment: wrap with `<Outlet />`, optional shell (e.g. sidebar + main). Should be thin: prefer re-exporting or composing from `@/features/*`. |
| `index.tsx` or `page.tsx`                     | Page entry for this segment. Only import from features and render; no business logic.                                                                        |
| `[param]/index.tsx` (e.g. `[id]`, `[cronId]`) | Dynamic segment page. Same rule: thin, delegate to features.                                                                                                 |

**Rule:** Route files should only **import and compose**. No new `features/` folders or heavy components inside `src/routes/`.

---

## 2. What Belongs in `src/features/`

Put **domain-oriented** UI and logic here:

- Layout building blocks: sidebars, headers, body panels, drawers
- Hooks and store usage for that domain
- Domain-specific forms, lists, modals, etc.

Organize by **domain** (e.g. `Pages`, `Home`, `Agent`, `PageEditor`), not by route path. One route can use several features; one feature can be used by several routes.

Each feature should:

- Live under `src/features/<FeatureName>/`
- Export a clear public API via `index.ts` or `index.tsx`
- Use `@/features/<FeatureName>/...` for internal imports when needed

---

## 3. How to Add a New SPA Route

1. **Choose the route group**
   - `(main)/` – desktop main app
   - `(mobile)/` – mobile
   - `(desktop)/` – Electron-specific
   - `onboarding/`, `share/` – special flows

2. **Create only segment files under `src/routes/`**
   - e.g. `src/routes/(main)/my-feature/_layout/index.tsx` and `src/routes/(main)/my-feature/index.tsx` (and optional `[id]/index.tsx`).

3. **Implement layout and page content in `src/features/`**
   - Create or reuse a domain (e.g. `src/features/MyFeature/`).
   - Put layout (sidebar, header, body) and page UI there; export from the feature’s `index`.

4. **Keep route files thin**
   - Layout: `export { default } from '@/features/MyFeature/MyLayout'` or compose a few feature components + `<Outlet />`.
   - Page: import from `@/features/MyFeature` (or a specific subpath) and render; no business logic in the route file.

5. **Register the route (desktop — two files, always)**
   - **`desktopRouter.config.tsx`:** Add the segment with `dynamicElement` / `dynamicLayout` pointing at route modules (e.g. `@/routes/(main)/my-feature`).
   - **`desktopRouter.config.desktop.tsx`:** Mirror the **same** `RouteObject` shape: identical `path` / `index` / parent-child structure. Use the static imports and elements already used in that file (see neighboring routes). Do **not** register in only one of these files.
   - **Mobile-only flows:** use `mobileRouter.config.tsx` instead (no need to duplicate into the desktop pair unless the route truly exists on both).

---

## 3a. Desktop router pair (`desktopRouter.config` × 2)

| File                               | Role                                                                                                                      |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `desktopRouter.config.tsx`         | Dynamic imports via `dynamicElement` / `dynamicLayout` — code-splitting; used by `entry.web.tsx` and `entry.desktop.tsx`. |
| `desktopRouter.config.desktop.tsx` | Same route tree with **synchronous** imports — kept for Electron / local parity and predictable bundling.                 |

Anything that changes the tree (new segment, renamed `path`, moved layout, new child route) must be reflected in **both** files in one PR or commit. Remove routes from both when deleting.

---

## 3b. Other `.desktop.{ts,tsx}` variants inside `src/routes/`

The router pair is **not** the only `.desktop` variant pattern in this repo. Some route trees colocate a `<name>.desktop.{ts,tsx}` next to its base `<name>.{ts,tsx}` — Vite's resolver swaps in the `.desktop` file for Electron builds. Same drift risk as the router pair: editing only one side can break Electron silently.

Known variants today:

| Base file (web)                                       | Desktop file (Electron)                                       | Purpose                                                                                                                                    |
| ----------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/routes/(main)/settings/features/componentMap.ts` | `src/routes/(main)/settings/features/componentMap.desktop.ts` | Settings tab → component map. Web uses dynamic `import()`; desktop uses sync imports. `componentMap.sync.test.ts` enforces identical keys. |
| `src/routes/(main)/agent/index.tsx`                   | `src/routes/(main)/agent/index.desktop.tsx`                   | Page entry. Desktop variant overrides the web page wholesale (e.g. extra popup guards).                                                    |
| `src/routes/(main)/group/index.tsx`                   | `src/routes/(main)/group/index.desktop.tsx`                   | Same pattern as agent.                                                                                                                     |

**Rules:**

1. After editing **any** `.ts`/`.tsx` under `src/routes/`, glob the same directory for a `<filename>.desktop.{ts,tsx}` sibling. If one exists, apply the equivalent change there in the same commit.
2. When adding a new SettingsTab, register it in **both** `componentMap.ts` (with `dynamic(...)`) and `componentMap.desktop.ts` (with a sync `import`). `componentMap.sync.test.ts` will fail the build otherwise.
3. When adding a new desktop-only page wholesale-override, prefer a single base file with platform-aware code over introducing a new `.desktop.tsx` variant — only add a new variant when the two trees genuinely diverge (different store wiring, different popup guards, etc.).
4. When deleting, remove **both** files together.

---

## 4. How to Divide Files (route vs feature)

| Question                                                 | Put in `src/routes/`                                     | Put in `src/features/`       |
| -------------------------------------------------------- | -------------------------------------------------------- | ---------------------------- |
| Is it the route’s layout wrapper or page entry?          | Yes – `_layout/index.tsx`, `index.tsx`, `[id]/index.tsx` | No                           |
| Does it contain business logic or non-trivial UI?        | No                                                       | Yes – under the right domain |
| Is it a reusable layout piece (sidebar, header, body)?   | No                                                       | Yes                          |
| Is it a hook, store usage, or domain logic?              | No                                                       | Yes                          |
| Is it only re-exporting or composing feature components? | Yes                                                      | No                           |

**Examples**

- **Route (thin):**\
  `src/routes/(main)/page/_layout/index.tsx` → `export { default } from '@/features/Pages/PageLayout'`
- **Feature (real implementation):**\
  `src/features/Pages/PageLayout/` → Sidebar, DataSync, Body, Header, styles, etc.
- **Route (thin):**\
  `src/routes/(main)/page/index.tsx` → Import `PageTitle`, `PageExplorerPlaceholder` from `@/features/Pages` and `@/features/PageExplorer`; render with `<PageTitle />` and placeholder.
- **Feature:**\
  Page list, actions, drawers, and hooks live under `src/features/Pages/`.

---

## 5. Progressive Migration (existing code)

We are migrating existing routes to this structure step by step:

- **Phase 1 (done):** `/page` route – segment files in `src/routes/(main)/page/`, implementation in `src/features/Pages/`.
- **Later phases:** home, settings, agent/group, community/resource/memory, mobile/share/onboarding.

When touching an old route that still has logic or `features/` inside `src/routes/`:

1. Prefer adding **new** code in `src/features/<Domain>/` and importing from routes.
2. For larger refactors, move existing route-only logic into the right feature and then thin out the route files (re-export or compose from features).
3. Use `git mv` when moving files so history is preserved.

---

## 6. Reference Structure (after Phase 1)

**Route (thin):**

```
src/routes/(main)/page/
├── _layout/index.tsx   → re-export or compose from @/features/Pages/PageLayout
├── index.tsx          → import from @/features/Pages, @/features/PageExplorer
└── [id]/index.tsx     → import from @/features/Pages, @/features/PageExplorer
```

**Feature (implementation):**

```
src/features/Pages/
├── index.ts            → export PageLayout, PageTitle
├── PageTitle.tsx
└── PageLayout/
    ├── index.tsx       → Sidebar + Outlet + DataSync
    ├── DataSync.tsx
    ├── Sidebar.tsx
    ├── style.ts
    ├── Body/           → list, actions, drawer, etc.
    └── Header/         → breadcrumb, add button, etc.
```

Router config continues to point at **route** paths (e.g. `@/routes/(main)/page`, `@/routes/(main)/page/_layout`); route files then delegate to features.

# When NOT to use

Do not use this skill for tasks outside its scope or when simpler alternatives are available.


# Example

```python
# 使用 spa-routes 技能
skill = load_skill("spa-routes")
result = skill.execute()
print(result)
```

