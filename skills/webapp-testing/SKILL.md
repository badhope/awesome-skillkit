---
name: Webapp Testing Harness
name_zh: Web 应用测试脚手架
slug: webapp-testing
description: 用 Playwright 和 Python 对本地 Web 应用做端到端测试。带服务器生命周期 helper、DOM 侦察行动模式、截图捕获。
description_zh: 用 Playwright 和 Python 对本地 Web 应用做端到端测试。带服务器生命周期 helper、DOM 侦察行动模式、截图捕获。
category: dev-tools
tags: [ai, api, backend, cli, database]
source:
ref: main
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

You need to test a local web application end-to-end — click
buttons, fill forms, check rendered output, capture screenshots,
inspect console logs. The target is on localhost, not a public
site. You want a script you can rerun, not an interactive session.

The skill is built around three rules:

1. **Playwright + Python, always.** `sync_playwright()` for
   synchronous scripts. Chromium headless by default.
2. **Server lifecycle belongs to a helper.** `scripts/with_server.py`
   starts servers, waits for ports, runs your script, tears
   everything down. Your test contains only Playwright logic.
3. **Static HTML vs dynamic SPA is the first decision.** If
   static, read the file directly. If SPA, navigate first, wait
   for `networkidle`, then inspect.

The decision tree is the most important part. Get it wrong and
you'll either over-engineer a static test or under-inspect a
dynamic app and click invisible buttons.

**Don't use this skill for** production testing against a
deployed URL (use a real CI test framework). And don't use it
for unit tests of JS components (use Vitest / Jest).

# Inputs

| Field | Required | Notes |
|---|---|---|
| `target_url` | yes | `http://localhost:PORT` or `file://...`. |
| `servers` | no | List of `{command, port}`. Omit if the server is already running or the target is static. |
| `headless` | no | Defaults to `true`. |
| `selectors` | no | Pre-known selectors. Empty list = reconnaissance. |

# Output

Plain-text summary. Typical return:

```
Script: /tmp/automation_2026-06-10.py
Screenshots: /tmp/inspect_initial.png, /tmp/inspect_after_submit.png
Result: pass

Discovered selectors:
  - text=Sign in
  - input[name=email]
  - button[type=submit]
  - .toast-success

Sequence:
  1. navigate to /login, wait for networkidle
  2. fill email, fill password
  3. click submit
  4. wait for .toast-success
  5. assert url matches /dashboard
```

# Prompt

```prompt
You are writing a Playwright + Python test for a local web app.
Follow the decision tree first; do not default to "run with_server
and write a complex script" before checking.

1. Decide: static HTML or dynamic SPA?

   If the URL is a file:// path or the project has no build/dev
   server, treat as static:
     - Read the HTML file directly.
     - Pick selectors from the source.
     - Skip the with_server helper entirely.
   If the URL is http://localhost:* (or the project has a dev
   server like Vite, Next, Rails), treat as dynamic:
     - Use with_server.py.
     - Run reconnaissance before action.

2. Check the server status.

   If `servers` is provided, ALWAYS use the helper — do not
   assume the server is already running. If `servers` is empty
   AND the target is dynamic, ask the user for the dev command
   (or detect it from package.json / Gemfile / Cargo.toml).
   Do not guess.

3. Inspect with_server.py BEFORE writing the test.

   Run:
     python scripts/with_server.py --help

   Read the help, then invoke. NEVER read the source of
   with_server.py first — the script is large, the help output
   is what you need, and the script is meant to be used as a
   black box.

4. Wire the Playwright script.

   The script contains ONLY Playwright logic. Server lifecycle
   is the helper's job. Template:

     from playwright.sync_api import sync_playwright

     with sync_playwright() as p:
         browser = p.chromium.launch(headless=True)  # always headless
         page = browser.new_page()
         page.goto('http://localhost:5173')  # server already up
         page.wait_for_load_state('networkidle')  # CRITICAL for SPAs
         # ... automation logic ...
         browser.close()

5. For dynamic apps: reconnaissance-then-action.

   a. Navigate.
   b. page.wait_for_load_state('networkidle'). Do NOT inspect
      DOM before this — you'll see pre-render state and the
      selectors will be wrong.
   c. Take a screenshot:
        page.screenshot(path='/tmp/inspect.png', full_page=True)
   d. Inspect:
        page.content()                # rendered HTML
        page.locator('button').all()  # enumerate buttons
   e. Pick selectors from the rendered state.
   f. Execute the actions.

6. For static HTML: skip reconnaissance, read the file.

     page.goto('file:///abs/path/to/index.html')
   The DOM IS the file. You can read it from disk first to pick
   selectors without burning a Playwright session.

7. Choose selectors with care.

   Prefer, in order:
     - role-based:  page.get_by_role('button', name='Submit')
     - text:        page.get_by_text('Sign in')
     - label:       page.get_by_label('Email')
     - test-id:     page.get_by_test_id('submit-button')
     - CSS:         page.locator('button[type=submit]')
   Avoid: nth-child, deep XPath, anything that depends on visual
   order.

8. Add waits — explicit, not timed.

   Good:
     page.wait_for_selector('.toast-success')
     page.wait_for_load_state('networkidle')
   Bad:
     page.wait_for_timeout(2000)  # flaky

9. Always close the browser.

   Use a `with sync_playwright()` block, OR a try/finally that
   calls browser.close().

10. Capture screenshots on failure.

    Wrap the action sequence in try/except. On any error, take
    a screenshot to /tmp/failure_<step>.png and dump
    page.content() to /tmp/failure_<step>.html. These are gold
    for debugging CI failures.

11. Console logging (optional).

    To capture browser console:

      page.on('console', lambda msg: print(f'[console.{msg.type}] {msg.text}'))
      page.on('pageerror', lambda err: print(f'[pageerror] {err}'))

    Useful for SPAs that log client-side errors instead of
    surfacing them in the DOM.
```

# When NOT to use

- **The target is a public, production URL.** This skill is
  for local dev/test. Production testing wants a real CI test
  framework, real Playwright config, retry logic, proper
  reporting, and a staging environment with seed data.
- **You want to unit-test a JS component in isolation.** Use
  Vitest, Jest, or Storybook. Playwright is for full-page
  flows, not component snapshots.
- **The target requires non-Chromium quirks** (legacy IE, old
  Safari). Playwright supports them, but a one-off script is
  not the right tool — use a real cross-browser CI grid.
- **You reach for `page.wait_for_timeout(ms)` for every step.**
  That's a flaky test waiting to fail. Use `wait_for_selector`
  or `wait_for_load_state` instead.
- **You forgot to wait for `networkidle` before inspecting the
  DOM on a SPA.** You'll see pre-render HTML, your selectors
  will be wrong, and the test will pass locally but fail in CI
  when the timing shifts.
- **The script imports the API client and asserts via the
  database instead of the UI.** That's a unit test in disguise.
  Playwright is for testing what the user actually sees.

# Example

**Input:**

```yaml
target_url: http://localhost:5173
servers:
  - command: "npm run dev"
    port: 5173
headless: true
selectors: []
```

**Output:**

```
Script: /tmp/automation_login_flow.py
Screenshots: /tmp/inspect_initial.png, /tmp/inspect_after_submit.png
Result: pass

Sequence:
  1. server: npm run dev (started, port 5173 ready in 4.2s)
  2. navigate http://localhost:5173/login
  3. wait_for_load_state('networkidle')
  4. screenshot /tmp/inspect_initial.png  (full page)
  5. fill input[name=email] = "user@example.com"
  6. fill input[name=password] = "correct-horse-battery-staple"
  7. click button[type=submit]
  8. wait_for_selector('.toast-success')
  9. assert page.url matches /\/dashboard$/
  10. screenshot /tmp/inspect_after_submit.png
  11. close browser
  12. helper: server torn down (exit 0)
```
