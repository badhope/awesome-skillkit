# ADR 005 — 后端用 Poetry、前端用 npm

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

我们需要一套包管理 + 依赖锁策略。后端是 Python，前端与 TypeScript SDK 是 JavaScript。

## 决策

- **Python（后端 + Python SDK）** → Poetry 1.8+
- **JavaScript / TypeScript（前端 + TypeScript SDK）** → npm 10+
  并提交 `package-lock.json`

## 依据

- Poetry：确定的 lockfile（`poetry.lock`）、清晰的 `pyproject.toml`、单条命令即可安装与运行。
- npm：Node 20+ 自带，CI 中无门槛，lockfile 通用，无需额外工具。

## 候选方案

| 方案                | 原因未选                                     |
|---------------------|---------------------------------------------|
| pip + requirements.txt | 缺乏确定的传递依赖解析 |
| uv                  | 优秀但 2026 年仍在演进；我们可能会回头评估 |
| pnpm / yarn         | 都可用；为最小摩擦选了 npm                  |

## 后果

- CI 使用 `poetry install --no-interaction` 与 `npm ci`。
- 贡献者需要安装 Poetry 与 npm；两者均记录于 [贡献指南](../community/contributing.md)。
- `pyproject.toml` 内置 `[tool.ruff]` 与 `[tool.mypy]` 配置，lint、类型检查、打包共用同一份文件。
