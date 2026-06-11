---
slug: react-router-search-params
name: React Router Search Param State
name_zh: React Router 搜索参数/哈希状态管理
version: 0.1.0
description: Decide between `replace` and `push` for URL state changes in React Router — the #1 cause of "back button is broken" bugs. Includes the `useSearchParamState` hook pattern, the `null`-to-clear convention, and the wizard-vs-filter decision table.
description_zh: 在 React Router 里为 URL 状态变化选 `replace` 还是 `push` —— 这是"浏览器后退键坏了"的 #1 病因。包含 `useSearchParamState` hook 模式、`null` 清空约定，以及 wizard vs filter 的决策表。

category: dev-tools
tags: [react, react-router, url, state, frontend]
platforms: []

inputs:
  - name: change_type
    type: enum
    required: true
    values: [in-page-state, navigable-step, normalize-after-save]
    description: |
      What kind of URL change you're making:
        - `in-page-state` — filter, sort, tab switch, search query,
          pagination. The URL mirrors UI state.
        - `navigable-step` — wizard step, multi-step form. The URL
          represents a step the user traverses with the back button.
        - `normalize-after-save` — the URL needs an ID added after
          a create / save operation (no user-visible action).
  - name: router_api
    type: enum
    required: true
    values: [useSearchParamState, setSearchParams, navigate]
    description: |
      Which router API you'll use:
        - `useSearchParamState` — preferred for a single validated
          param.
        - `setSearchParams` — for multiple params at once, or raw
          access when validation is overkill.
        - `navigate` — for hash-based navigation or full URL
          replacement.
  - name: param_count
    type: enum
    required: true
    values: [single, multiple]
    description: |
      `single` = one param. Use the hook.
      `multiple` = several params at once. Use setSearchParams.
  - name: validation
    type: enum
    required: false
    values: [none, zod, manual]
    description: |
      How to validate the param value. Default `zod` for typed
      enums. `manual` for legacy / string-only. `none` when the
      param is a free-form string (e.g. a search query).

output:
  format: text
  description: |
    A short summary of the pattern chosen, the code snippet to
    apply, and a one-line reminder of the anti-patterns.
  schema:
    type: object
    properties:
      pattern: { type: string, description: "Pattern name, e.g. `useSearchParamState`" }
      code_snippet: { type: string }
      replace_vs_push: { type: string, enum: [replace, push] }
      gotchas: { type: array, items: { type: string } }

author: "Promptfoo (downstream pack: badhope)"
license: MIT
source:
  url: https://github.com/promptfoo/promptfoo/tree/main/.claude/skills/search-params
  ref: main
  commit: latest
created: 2026-06-10
updated: 2026-06-10
---

# When to use

You're wiring up **URL state in a React app** — a filter, a
sort, a tab, a wizard step, a search query. The URL needs to
mirror the UI so users can share links, refresh, and use the
back button. You're using **React Router v6+** (or compatible
— TanStack Router, Remix).

The skill exists because **one mistake here is the #1 cause
of "back button is broken" bug reports**: pushing in-page
state changes (filter toggles, sort changes) into history.
Users click "back" expecting to leave the page; instead the
filter un-toggles, and the user is stuck in a UI they can't
get out of without using the browser history menu.

The fix is mechanical: every URL change has to be classified
as **in-page state** (use `replace`, don't pollute history) or
**navigable step** (use `push`, back button should return to
the previous step). There is no third option.

**Don't use this skill for** server-side URL handling (route
matching, SSR data loading — that's React Router loaders /
Remix loaders, not this). And don't use it for non-React
frontends.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `change_type` | yes | `in-page-state`, `navigable-step`, or `normalize-after-save`. Drives the replace/push decision. |
| `router_api` | yes | `useSearchParamState` (preferred), `setSearchParams`, or `navigate`. |
| `param_count` | yes | `single` (use the hook) or `multiple` (use setSearchParams). |
| `validation` | no | `zod` (default for typed enums), `manual`, or `none`. |

# Output

Plain-text summary. Typical return:

```
Pattern: useSearchParamState
Code: see below
Replace vs push: replace
Gotchas:
  - pass null to clear, not ''
  - Zod schema decides the type at runtime, not the call site
```

# Prompt

```prompt
You are adding a URL state change to a React Router app.
Decide replace vs push FIRST, then pick the API.

1. Decide: replace or push?

   Change type                 | replace or push | Why
   --------------------------- | --------------- | ---
   filter / sort / tab         | replace         | in-page state; back
                               |                 | button should leave
                               |                 | the page
   search query                | replace         | same as filter
   pagination                  | replace         | same as filter
   wizard step                 | push            | user expects to step
                               |                 | through with back
   multi-step form             | push            | same as wizard
   post-save URL normalization | replace         | not a user action;
                               |                 | no history entry
                               |                 | needed

   If unsure, ASK. Do not default to push — pushing
   in-page state is the bug.

2. Pick the API.

   `useSearchParamState` (preferred for one validated param):

     import { useSearchParamState } from '@app/hooks/useSearchParamState';
     import { z } from 'zod';

     const TabSchema = z.enum(['overview', 'details', 'settings']);
     const [activeTab, setActiveTab] =
       useSearchParamState('tab', TabSchema, 'overview');

   The hook handles validation AND uses `replace: true`
   internally. You get both for free. Do NOT write
   `useSearchParamState` differently — the replace
   behaviour is the whole point.

   `setSearchParams` (for multiple params at once):

     const [searchParams, setSearchParams] = useSearchParams();

     // in-page state — replace
     setSearchParams(
       (params) => {
         params.set('status', 'active');
         params.set('sort', 'name');
         return params;
       },
       { replace: true },
     );

     // wizard step — push (default; do not pass replace)
     setSearchParams((params) => {
       params.set('step', 'review');
       return params;
     });

   `navigate` (for hash or full URL replacement):

     // wizard hash — push (default)
     navigate('#review');

     // tab switch on a detail page — replace
     navigate(`#${section}`, { replace: true });

     // post-save URL normalization
     navigate(`/items/${newItemId}`, { replace: true });

3. Validation rules.

   - Always use a Zod schema for enums. The hook throws
     an invariant error if the URL value is not in the
     schema. That's a feature — it means the URL state
     can never be inconsistent with the schema.

   - Use `null` to clear a param, not `''`:

     setTab(null);              // RIGHT — removes the param
     setTab('');                // WRONG — hook throws
                                 //         invariant error

   - For free-form strings (search query, etc.), use
     `z.string().min(1).max(200)` or accept the raw
     string and validate downstream.

4. Anti-patterns.

   - Pushing in-page state (breaks back button):

       setSearchParams((p) => {
         p.set('filter', value);
         return p;
       });                          // WRONG — no { replace: true }

       navigate(`?tab=${newTab}`);  // WRONG — push is default

   - Using raw `useSearchParams` for a single param:

       const [searchParams, setSearchParams] = useSearchParams();
       const tab = searchParams.get('tab');
       const setTab = (v) => {
         setSearchParams((p) => { p.set('tab', v); return p; });
       };                           // WRONG — no validation,
                                    //         easy to forget
                                    //         { replace: true }

       // RIGHT — use the hook
       const [tab, setTab] = useSearchParamState('tab', TabSchema, 'overview');

   - Setting the param to `''` to "clear" it:

       setTab('');                  // WRONG — throws invariant
       setTab(null);                // RIGHT — clears cleanly

5. Hash-based navigation: still classify the change.

   For wizard / multi-step flows where the back button
   should traverse steps, use push (the default):

     // wizard step navigation — push, intentional
     const updateHash = (newStep) => {
       navigate(`#${newStep}`);
     };

   For hash changes that represent in-page state (a tab
   switch on a detail page), use replace:

     // tab switch on detail page — replace, no history clutter
     navigate(`#${section}`, { replace: true });

6. Post-save URL normalization.

   When the URL needs to include a new ID after a create
   or save operation (and it's not a user action), use
   replace. Adding a history entry here would mean the
   user clicks back, lands on the unsaved "new" page, and
   either sees a 404 or accidentally re-creates the
   resource.

     navigate(`/items/${newId}`, { replace: true });
```

# When NOT to use

- **You're in a non-React framework.** This skill targets
  React Router v6+ patterns. Vue Router, SvelteKit, Solid
  Router have their own equivalents but the
  decision-table rules still apply.
- **You're matching on server-rendered routes, not
  search params.** That's route matching, not state
  management. Use loaders / SSR data flow, not
  `useSearchParams`.
- **You push in-page state into history.** "It works
  locally" — wait until a user clicks back nine times to
  undo your nine filter toggles. The fix is `replace: true`.
- **You set a param to `''` to "clear" it.** The hook
  (and most typed URL-state libraries) throw on empty
  string. Use `null`.
- **You hand-roll `useSearchParams` + manual validation
  for a single param.** Use `useSearchParamState`. The
  hook's replace behaviour is the whole reason to use it.
- **You use `push` for post-save URL normalization.** A
  history entry for a non-user action breaks back
  navigation. Use `replace`.
- **You confuse hash state with search-param state.**
  Hash (`#section`) is for in-page anchors and is not
  sent to the server. Search params (`?tab=x`) are sent
  to the server and survive a hard refresh. Pick the
  right one for the semantics — don't use `#` to mimic
  search params, you'll lose server-side rendering.
- **You classify the change as "navigable step" when
  the user is on a filterable list.** That's still
  in-page state. Wizard steps are sequential paths the
  user has to traverse; filter changes are mutable
  view-state on a single page.

# Example

**Input:**

```yaml
change_type: in-page-state
router_api: useSearchParamState
param_count: single
validation: zod
```

**Output:**

```
Pattern: useSearchParamState
Replace vs push: replace (built-in)

Code:

  import { z } from 'zod';
  import { useSearchParamState } from '@app/hooks/useSearchParamState';

  const TabSchema = z.enum(['overview', 'details', 'settings']);
  const [activeTab, setActiveTab] =
    useSearchParamState('tab', TabSchema, 'overview');

  // later
  setActiveTab('details');   // pushes to ?tab=details
                             //   using replace, NOT push
  setActiveTab(null);        // clears the ?tab= param

Gotchas:
  - 'overview' | 'details' | 'settings' is the only valid value
  - null clears, '' throws
  - the hook uses replace internally — do not wrap it
    in setSearchParams
```
