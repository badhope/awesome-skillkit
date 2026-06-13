---
name: agent-setup-maintenance
name_zh: Agent 设置与维护
description: Shared workflow for editing Langfuse''s repo-owned agent setup 
  under
description_zh: 设置和维护 AI agent 的配置、环境变量和依赖项。
category: dev-tools
tags:
  - ai
  - database
  - docker
  - documentation
  - frontend
source:
license: UNKNOWN
author: unknown
version: 0.1.0
needs_review: false
slug: agent-setup-maintenance
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

Use this skill when you need guidance on agent setup maintenance.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Agent Setup Maintenance

Use this skill when changing the shared agent setup for the repository.

## Start Here

- Read [`../../README.md`](../../README.md) for the shared config and shim model.
- Read root [`../../AGENTS.md`](../../AGENTS.md) for repo-level expectations.
- When adding or editing shared skills, use
  [`../skill-creator/SKILL.md`](../skill-creator/SKILL.md), then apply the
  repo-specific checks in this skill.
- Inspect [`../../../scripts/agents/sync-agent-shims.mjs`](../../../scripts/agents/sync-agent-shims.mjs)
  before changing generated outputs or provider discovery behavior.
- Inspect [`../../../scripts/postinstall.sh`](../../../scripts/postinstall.sh)
  and [`../../../package.json`](../../../package.json) when changing install-time
  sync behavior.

## Workflow

1. Edit the canonical files under `.agents/`, not generated provider outputs.
2. Keep root `AGENTS.md` and `CLAUDE.md` as discovery symlinks; do not turn
   them back into manually maintained copies.
3. Treat tool-specific directories such as `.claude/`, `.cursor/`, `.codex/`,
   `.vscode/`, and `.mcp.json` as generated discovery surfaces unless the tool
   requires a truly tool-specific feature.
4. Keep root `AGENTS.md` concise. Move detailed or conditional workflows into
   shared skills or package `AGENTS.md` files.
5. Treat developer feedback as a learning loop: when a task reveals a durable
   repo convention, recurring pitfall, reusable workflow, or verification
   pattern, update the smallest relevant `AGENTS.md` or shared skill.
6. When adding or changing a shared skill, keep `SKILL.md` as the entrypoint; do
   not add skill-by-skill links to root `AGENTS.md`.
7. When shared setup behavior changes materially, update `README.md` and
   contributor-facing docs in the same PR.

## Docker / Install-Time Constraint

- `pnpm install` runs in environments that may not contain the full repo source
  tree.
- In Docker builds, Turbo's pruned install stage can run root `postinstall`
  before `scripts/` and `.agents/` are available in the image.
- Keep install-time agent setup logic robust in those pruned contexts: skip
  cleanly when the required repo-owned files are not present.

## Required Verification

Run after changing shared agent setup:

- `pnpm run agents:sync`
- `pnpm run agents:check`

Run additional verification when relevant:

- `pnpm run postinstall` when install-time behavior changes
- targeted tests for any scripts you changed

## Design Rules

- Prefer one repo-owned source of truth over duplicated provider-specific files.
- Keep shared setup tool-neutral where possible.
- Only keep provider-specific files in source control when the provider requires
  a fixed discovery path or feature that cannot be expressed through the shared
  setup model.

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.


```bash
# 使用 agent-setup-maintenance 技能
python scripts/use-skill.py agent-setup-maintenance

# 查看技能详情
python scripts/inspect-skill.py agent-setup-maintenance

# 验证技能
python scripts/validate-skill.py agent-setup-maintenance
```
