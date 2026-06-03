# ADR 010 — Pre-commit 钩子 + Conventional Commits

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

我们想要一致的代码风格与可解析的提交历史，同时不让每位贡献者手动安装五个工具。

## 决策

- **Pre-commit** 在每次提交时运行 lint 与格式化。
- **Conventional Commits** 在 `commit-msg` 钩子中强制，从而后续发布可以
  自动生成 CHANGELOG。
- `Makefile` 暴露同一组命令（`make lint`、`make typecheck`、`make test`、
  `make secrets-scan`），以供 pre-commit 场景之外使用。

## 后果

- 提供 `make first-run` 目标，一次性安装所有依赖。
- CI 工作流仍会重跑 lint 作为兜底。
- 后续通过 release-please（或机器人）可以从提交日志直接生成 CHANGELOG diff。
