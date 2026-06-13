---
name: frontend-browser-review
name_zh: 前端浏览器审查
description: Shared workflow for browser-based review of user-visible frontend 
  changes
description_zh: 审查前端代码的浏览器兼容性、性能和可访问性。
category: dev-tools
tags:
  - ai
  - backend
  - cli
  - documentation
  - frontend
source:
license: UNKNOWN
author: unknown
version: 0.1.0
needs_review: false
slug: frontend-browser-review
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

Use this skill when you need guidance on frontend browser review.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Frontend Browser Review

Use this skill when a change affects what users see or do in the browser.

## Start Here

- Read [`../../../web/AGENTS.md`](../../../web/AGENTS.md) for web-specific
  entry points and test commands.
- Use the workspace `playwright` MCP server configured from the repo-owned
  shared agent setup.

## When To Use It

- UI changes in `web/**`
- Layout, styling, or responsive behavior changes
- Changes to navigation or page flows
- Bug fixes where the failure mode is visible in the browser
- Final signoff for user-visible frontend work

## Prefill Test Data First

Most flows are only reviewable against meaningful data. Before opening the
browser, seed what the flow needs with the seed CLI (see the
`seed-test-data` skill for the need→command table):

- `pnpm run seed -- trace-tree --observations 5000 --v4` — complex
  observation trees (v3 + v4 events)
- `pnpm run seed -- long-session --traces 300` — heavy session views
- `pnpm run seed -- many-traces --count 100000` — list/filter performance
- `pnpm run seed -- doctor` — when the stack misbehaves

Every run prints UI deep links — open those instead of navigating manually.
Do not hand-write seed scripts or raw ClickHouse inserts.

## Review Loop

1. Start the app with `pnpm run dev:web` unless an existing local server is
   already running.
2. Install Chromium with `pnpm run playwright:install` if Playwright has not
   been set up on the machine yet.
3. Open the primary changed flow with the Playwright MCP server, using the
   deep links printed by the seed CLI when the flow needs seeded data.
4. Exercise the main happy path affected by the change.
5. Check for obvious visual regressions:
   - broken layout or spacing
   - banner overlap or viewport anchoring issues
   - missing loading, empty, or error states
   - broken responsive behavior on narrow widths
6. If the page changed materially, inspect the resulting UI state and compare
   it against the intended behavior from the task or existing patterns.
7. If the browser session fails, inspect traces and artifacts under
   `/tmp/playwright-mcp`.

## Output Expectations

Report:

1. What flow you reviewed
2. Whether the primary flow worked
3. Any visible regressions or follow-up risks
4. If review was blocked, exactly what prevented browser verification

## Scope Notes

- This skill complements, not replaces, targeted tests and linting.
- For implementation details, stay in `web/AGENTS.md` and package-local skills.
- Use this as the browser-signoff workflow, not as a generic frontend coding
  guide.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

```bash
# 1. 启动开发服务器
pnpm run dev:web

# 2. 安装 Playwright（首次）
pnpm run playwright:install

# 3. 预填充测试数据
pnpm run seed -- trace-tree --observations 5000 --v4
pnpm run seed -- long-session --traces 300

# 4. 使用 Playwright MCP 打开变更页面
# 在 Playwright MCP 中导航到 seed CLI 输出的深链接
# 检查响应式布局、加载状态、错误状态

# 5. 检查视觉回归
# - 布局/间距是否正确
# - 窄屏下是否正常
# - 加载/空/错误状态是否完整
```

