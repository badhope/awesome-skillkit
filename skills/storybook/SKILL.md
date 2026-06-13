---
name: Storybook Component Stories
name_zh: Storybook 组件故事编写
description: 'You''re writing or reviewing a **Storybook story** for a'
description_zh: 为 React 组件编写或审查 Storybook 故事（.stories.tsx）—— CSF Next 
  格式、纯展示组件规则、类型化元数据、故事命名按状态、禁止 MSW。"一个文件一个导出组件"的规则是一把双刃剑。
category: dev-tools
tags:
  - ai
  - api
  - backend
  - cli
  - database
source: null
license: MIT
author: 'Langfuse (downstream pack: badhope)'
version: 0.1.0
needs_review: false
slug: storybook
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

You're writing or reviewing a **Storybook story** for a
React component — a `.stories.tsx` file under
`stories/` or alongside the component.

Stories are not just "show the component in isolation".
A good story:

- Catches the component in a specific, named **state**
  (Default, Empty, Error, Loading, Disabled,
  WithLongName). Naming after the state, not the
  implementation, makes the story list scannable.
- Uses **CSF Next** format with `satisfies` and typed
  Storybook metadata. Invalid args, decorators, and
  play functions are type-checked at build time.
- Stays presentational. Components that need context,
  fetch data, or call a private API are **not** story
  candidates; refactor them so the presentational part
  is the story target.
- Has play functions for **user-relevant interactions**
  (clicking a button to open a menu) but never as a
  compensation for complex setup or hidden dependencies.

The wrong story is one that wraps a real API client
behind MSW (we don't use MSW) or recreates a complex
context tree to render a single button.

**Don't use this skill for** Cypress / Playwright
component tests (use their own config). And don't use
it for a page-level integration test.

# Inputs

| Field | Required | Notes |
|---|---|---|
| `component_path` | yes | Path to the React component. |
| `component_name` | yes | Component name. |
| `review_mode` | no | `write` (default) or `review`. |

# Output

Plain-text confirmation. Typical return (write mode):

```
Story: src/components/Button/Button.stories.tsx
Stories (6):
  - Default
  - Disabled
  - Loading
  - WithIcon
  - AsLink
  - AllVariants
```

Typical return (review mode):

```
Review findings:
  - File uses CSF 2 default export, not CSF Next
    with `satisfies`. Migrate.
  - Story "Test1" — rename to a state name
    (e.g. "WithLongName").
  - Story uses `render: () => <App>` — that's a
    page-level composition, not a story. Move to
    Playwright / Cypress.
  - Component fetches data via context; refactor to
    a presentational sub-component before writing
    the story.
```

# Prompt

```prompt
You are writing or reviewing a Storybook story. Decide
first whether the component is story-eligible; if it
isn't, suggest a refactor.

1. Decide if the component is story-eligible.

   Story-eligible components do NOT:
     - depend on context (provider, theme, router)
     - fetch data via a private API (project's own
       tRPC, internal HTTP, or any dependency the
       story cannot replicate without MSW)

   If the component does any of these, STOP. The
   skill does not write a story for it. Instead:
     a) Suggest a refactor: extract a presentational
        sub-component that takes the relevant data
        via props.
     b) Keep the original component but use the new
        presentational sub-component for rendering.
     c) Write the story for the new sub-component.

   This is the most common finding in review mode:
   "the component isn't story-eligible". The fix
   is a refactor, not a story.

2. Filename and structure.

   - File: `<ComponentName>.stories.tsx` next to the
     component.
   - Default export: `title`, `component`, parameters
     (e.g. `layout: 'centered'`).
   - Use `satisfies Meta<typeof Component>` and
     `satisfies StoryObj<typeof Component>` for type
     safety. Invalid args, decorators, and play
     functions surface as TS errors.
   - One exported or public component per file. If
     the file exports more than one, suggest splitting
     first.

3. Write stories by state, not by test name.

   Prefer:
     - Default
     - Empty
     - WithLongName
     - Error
     - Disabled
     - Loading
     - WithIcon
     - AsLink

   Avoid:
     - Test1
     - CustomRenderExample
     - ButtonWithLongNameAndIcon

   The story name should describe the state, not the
   implementation. A user scanning the story list
   should see "Loading" and know what to look at.

4. Avoid custom render functions by default.

   Use the default render. Custom `render: () => ...`
   is allowed only when:
     - the component needs a wrapper for a specific
       state that no other story needs
     - the wrapper is itself a presentational component

   If you find yourself writing `render: () => <App>`
   or any large composition, that's a page-level
   test. Move to Playwright / Cypress, not Storybook.

5. Set callbacks as Storybook Actions.

   ```tsx
   import { fn } from 'storybook/test';

   const meta = {
     component: Button,
     args: {
       onClick: fn(),
     },
   } satisfies Meta<typeof Button>;
   ```

   Don't pass inline arrow functions in args if you
   want consistent action logging.

6. Keep fixtures small.

   Use the smallest meaningful data shape. If a story
   needs fixtures:
     - check whether a reusable helper function
       exists in `stories/fixtures.ts` or similar
     - if not, create one for the shared fixture

   Avoid large inline fixtures. A 5-level nested
   object is a sign the story is testing the wrong
   thing.

7. Variant / design showcase stories.

   When a component has many variants and the point
   is to showcase the design (not the functionality),
   a story may render the component multiple times.

   Example: `<Button size="sm" />`, `<Button size="md" />`,
   `<Button size="lg" />` side by side. Or a matrix of
   `size × variant`.

   Variant stories:
     - may render the component multiple times
     - should NOT contain play functions
     - should NOT allow Storybook user to customise
       the variant args

8. Play functions for interactions only.

   Use a play function to test a user-relevant
   interaction after render (click a button to open
   a menu, type into a search field). Do NOT use a
   play function to compensate for complex setup or
   hidden dependencies — if the story needs elaborate
   setup, refactor the component to be more
   presentational.

9. We do not use MSW and are not planning to add it.

   If the story needs to mock network responses, the
   refactor is to extract a presentational component.
   Adding MSW is a project-level decision, not a
   per-story decision.
```

# When NOT to use

- **The component depends on context (provider, theme,
  router).** Stories must be presentational. Refactor
  the component first.
- **The component fetches data via a private API.**
  Same rule: extract a presentational sub-component.
- **You reach for MSW to mock a fetch.** We don't use
  MSW. The fix is a refactor, not a new mock
  framework.
- **You write a page-level composition as a story.**
  `render: () => <App>` is a Cypress / Playwright
  job, not Storybook.
- **The story name is "Test1" / "CustomRenderExample".**
  Story names are state names, not test names. The
  user scanning the list needs to know what they're
  looking at without reading the source.
- **The component file exports more than one
  component.** Split the file first. Stories cover
  one component at a time.
- **You add a play function to compensate for complex
  setup.** If the play function does `await
  setupContext()` and `await seedDatabase()`, the
  component is not story-eligible. Refactor.
- **The story depends on a wrapper component that
  itself has its own props.** The wrapper is then
  the actual subject. Either remove the wrapper or
  write the story for the wrapper, not the inner
  component.
- **The variant story has a play function.** Variant
  stories showcase design, not interaction. The play
  function is a giveaway that the story is actually
  a behavioural test masquerading as a variant
  showcase.

# Example

**Input (write mode):**

```yaml
component_path: src/components/Button/Button.tsx
component_name: Button
review_mode: write
```

**Output:**

```
Story: src/components/Button/Button.stories.tsx

Stories (6):
  - Default
  - Disabled
  - Loading
  - WithIcon
  - AsLink
  - AllSizes   (size × variant matrix, no play)
```
