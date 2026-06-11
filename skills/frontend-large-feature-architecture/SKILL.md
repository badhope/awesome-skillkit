---
slug: frontend-large-feature-architecture
name: Frontend Large-Feature Architecture
name_zh: 前端大型功能架构
version: 0.1.0
description: Plan a non-trivial frontend feature before coding — controller components, state location, list vs detail fetch, virtualization. Generic patterns, framework-aware but not framework-bound.
description_zh: 在写代码前规划非平凡的前端功能 —— 控制器组件、状态归属、列表 vs 详情获取、虚拟化。通用模式，框架感知但不绑死。

category: applications
tags: [frontend, react, architecture, state-management, performance]
platforms: []

inputs:
  - name: feature
    type: string
    required: true
    description: |
      One-sentence description of the feature (e.g. "user can
      pin a row in the table and the pin persists across
      sessions").
  - name: framework
    type: enum
    required: false
    values: [react, vue, svelte, solid, other]
    default: react
    description: |
      Target framework. Most of the principles are
      framework-agnostic; some (controller components,
      tRPC) default to React/Next.
  - name: state_libraries
    type: array
    required: false
    items: { type: string }
    description: |
      State management libraries the app already uses
      (e.g. `[zustand, react-query, jotai, redux]`).
      Default to react-query + zustand for new code.
  - name: data_scale
    type: enum
    required: false
    values: [small, medium, large, huge]
    description: |
      Approximate size of the data the feature touches.
      `huge` (>=10K rows, >=50 columns) forces
      virtualization. `large` (>=1K rows) usually
      virtualizes too.

output:
  format: text
  description: |
    An architecture plan covering: which state lives where,
    the component split, the list vs detail fetch decision,
    virtualization choice, and the edge cases to handle
    before writing code. No JSON envelope — the plan is
    text.
  schema:
    type: object
    properties:
      state_map: { type: string, description: "Where each piece of state lives (URL / server / local / cache)" }
      components: { type: array, items: { type: string } }
      fetch_strategy: { type: string, description: "Server component vs react-query vs URL state" }
      virtualization: { type: string, enum: [none, window, fixed, custom] }
      edge_cases: { type: array, items: { type: string } }

author: "Langfuse (downstream pack: badhope)"
license: MIT
source:
  url: https://github.com/langfuse/langfuse/tree/main/.agents/skills/frontend-large-feature-architecture
  ref: main
  commit: latest
created: 2026-06-10
updated: 2026-06-10
---

# When to use

You're about to build a **non-trivial frontend feature** —
something that has more than two screens, more than one fetch,
or a piece of state that has to survive navigation. The
"just write it and see" approach works for CRUD; for
everything else, the wrong choice of state location or
component split wastes a sprint.

The skill forces you to decide, before coding, four things
that compound once the feature exists:

1. **Where state lives** — URL / server / local / cache
2. **How components split** — controller / presentational
3. **List vs detail fetch** — server-rendered page vs
   client-side hydration
4. **Virtualization** — none / window / fixed

If you skip these and start with the page component, you'll
build the feature three times: once to ship, once to add
caching, once to fix perf.

**Don't use this skill for** trivial CRUD (just use a
scaffolder). And don't use it for the visual design itself
(use a frontend-design skill or designer).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `feature` | yes | One-sentence feature description. |
| `framework` | no | Defaults to `react`. Most patterns are framework-agnostic. |
| `state_libraries` | no | What the app already uses. Defaults: react-query + zustand. |
| `data_scale` | no | `small` / `medium` / `large` / `huge`. Drives virtualization. |

# Output

Plain-text architecture plan. Typical return:

```
State map:
  - selectedRowId        → URL (?row=...)
  - sort + filter state  → URL (?sort=...&filter=...)
  - "has user pinned"    → server (Zustand re-fetched on
                           change, optimistic)
  - dropdown open/closed → local useState
  - search query (debounced) → URL + local echo

Component split:
  - <TableController>     : owns the page-level state,
                            tRPC call, route params
  - <TableToolbar>        : sort, filter, search, density
  - <TableBody>           : virtualization + rows
  - <PinRowButton>        : presentational, takes
                            rowId + isPinned as props
  - <RowDetailDrawer>     : presentational, fetches detail
                            on demand via tRPC by id

Fetch strategy:
  - Initial list: server component with tRPC, streamed
    RSC. No client fetch.
  - Sort/filter changes: tRPC queries, debounced 250ms
    before firing.
  - Row pin: client mutation, optimistic update on
    list, refetch on success/failure.
  - Row detail: client fetch (lazy), cached in
    react-query.

Virtualization: tanstack-virtual (window), keep ~50 rows
in DOM, overscan 5.

Edge cases:
  - empty list state
  - row-pin with row count > 10K (server-side
    cursor pagination, not offset)
  - filter + sort combination that returns 0 rows
  - sort/filter change while a row-detail drawer is
    open (close drawer? clear selected id?)
  - concurrent pin + unpin (optimistic queueing)
```

# Prompt

```prompt
You are planning a non-trivial frontend feature. Decide four
things in order; do not start coding before the plan is
written.

1. Map state to location.

   For each piece of state, pick one of:
     - URL (?param=value) — shareable, survives refresh,
       back button restores it. Use for: filters, sort,
       selected id, pagination cursor, view mode.
     - Server state (react-query / tRPC) — the source
       of truth, owned by the database. Use for: data
       fetched from the API.
     - Local component state (useState) — UI ephemera.
       Use for: dropdown open/closed, hover, debounced
       search text, form fields.
     - URL state derived from local state — for example
       a search input that mirrors a debounced value
       in the URL. (The local state drives the input
       responsiveness; the URL is the truth for share /
       refresh.)

   The most common mistake is putting UI ephemera in the
   URL, or putting shareable filter state in local state.
   Filters go in the URL. "Is this dropdown open" goes
   in local state.

2. Pick the component split.

   Default to controller + presentational:
     - Controller component: owns the page-level state,
       fetches the data, derives props, dispatches
       mutations.
     - Presentational component: receives typed props,
       renders. No data fetching, no global state access.
       Easier to Storybook, easier to reuse.

   One controller per feature. Multiple presentationals.
   The controller is the only place that knows the
   tRPC / react-query / state hooks for this feature.

   If the controller is getting too large (>300 lines),
   split by *sub-feature*, not by *sub-component*:
     - <PageHeader>
     - <PageBody>
     - <PageFooter>
   Not:
     - <PageHeaderController>
     - <PageHeaderPresentational>

3. Decide list vs detail fetch.

   Initial page load:
     - Server component + tRPC + streamed RSC if the
       page is read-mostly. No client fetch.
     - Client fetch + react-query if the page is
       interactive from frame 1 (filters, edits, real
       time).

   List → detail navigation:
     - Lazy: fetch detail only when the user opens
       the detail. Cached in react-query. Best for
       long lists where most users don't open detail.
     - Eager: fetch detail alongside the list. Best
       for short lists where most users open detail.

   For "open detail in a drawer" patterns, lazy is
   almost always right.

4. Decide virtualization.

   None       — < 100 rows. No virtualization. The
                 browser handles it.
   Window     — 100 to 10K rows. tanstack-virtual or
                 react-window.
   Fixed      — 10K+ rows. Server-side pagination +
                 cursor. The client only ever sees
                 a page of the data.
   Custom     — irregular row heights, sticky headers
                 inside rows, etc. Build your own on
                 top of window.

   For a "table" UI in a B2B app, default to window
   with server-side pagination behind it. The client
   is never asked to render 10K rows in DOM.

5. List edge cases BEFORE coding.

   Common ones the planning round catches:
     - empty list (zero state, no error, no spinner)
     - filter returns zero rows
     - filter + sort + cursor pagination (cursor must
       respect sort)
     - selection persisted in URL but item no longer
       exists (404 in drawer, close drawer on mount)
     - user mutation while a fetch is in flight
       (disable the trigger, queue the action)
     - long-running mutation (>10s) — show progress
       or a separate "in flight" indicator, not a
       blocking spinner

   For each edge case, the plan should say:
     a) what the user sees
     b) which component owns the handling
     c) which state flag drives the rendering
```

# When NOT to use

- **The feature is a single component with no fetch.**
  That's not architecture, that's just code. Write it.
- **The feature is a CRUD scaffold with no
  novel state.** Use a scaffolder. The architecture
  is implied (server component + form + tRPC mutation).
- **You skip step 1 (state map) and go straight to
  components.** State location is the most expensive
  decision to change later. Decide it first.
- **You use the URL for ephemeral UI state**
  (dropdown open, hover). It's a footgun: the URL
  becomes a UI-state warehouse that's hard to clean
  up, the browser history fills with "open dropdown
  one, two, three", and the back button is broken.
- **You virtualize the wrong axis.** If rows are
  tall but there are only 30, virtualize columns
  or don't virtualize at all. If there are 30K rows
  in a grid that the user scrolls through, server
  pagination is better than client virtualization.
- **You use a controller component for a single
  presentational widget.** No data fetching, no
  state, no global access — just a `<Button>`. No
  controller needed.
- **You split components by *type* instead of
  *feature*.** Pages split by sub-feature
  (`<PageHeader>`, `<PageBody>`), not by sub-type
  (`<PageHeaderController>`, `<PageHeaderView>`).
  Type-split components leak state coupling and
  make Storybook harder.
- **You skip the edge-case list.** Every shipped
  feature has been bitten by the case nobody
  thought of. List the cases, name who handles
  them, and the post-merge bug count drops.
- **You plan with an "all-in-one" mega component
  that fetches + state + UI.** It will hit 1000
  lines in a week, and the next developer will
  not be able to refactor it without touching
  every screen at once.

# Example

**Input:**

```yaml
feature: |
  User can pin a row in the table and the pin persists
  across sessions.
framework: react
state_libraries: [react-query, zustand]
data_scale: large
```

**Output:**

```
State map:
  - selectedRowId       → URL (?row=...)
  - sort + filter       → URL (?sort=name&filter=active)
  - pin state           → server (mutation refetches list)
  - drawer open/closed  → local useState
  - search debounce     → local echo + URL on debounce

Components:
  - <TablePage>          controller, owns URL state +
                         fetches, refetches on mutation
  - <TableToolbar>       sort/filter/search inputs
  - <TableBody>          window-virtualized rows
  - <PinRowButton>       presentational, calls
                         onPin(rowId) prop
  - <RowDetailDrawer>    presentational, lazy fetch
                         via tRPC by id

Fetch strategy:
  - list: server component + tRPC streamed
  - pin: client mutation, optimistic, refetch on settle
  - detail: client fetch on drawer open, react-query
            cache by rowId

Virtualization: tanstack-virtual window, 50 in DOM,
                overscan 5. Server-side cursor pagination
                at 1K rows.

Edge cases:
  - empty list  → empty state, no error
  - filter returns 0 → "no rows match" inline
  - selected row id in URL but row deleted → close
    drawer on mount if not found
  - pin + sort change → sort is independent of pin;
    pin order is by pinned_at desc server-side
  - concurrent pin/unpin → debounce 250ms; refetch
    list on settle
```
