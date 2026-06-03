# AI-SKILL — 架构决策记录

本目录包含架构决策记录（ADR）。

每条 ADR 是一篇短小、不可变的文档，记录**一个**重要的技术决策：上下文、备选方案、决定、后果。

## 索引

| #   | 标题                                | 状态     |
|-----|--------------------------------------|------------|
| 001 | [Pydantic v2 + ClassVar Depends](001-pydantic-v2-and-classvar-depends.md) | 已采纳 |
| 002 | [Qdrant 向量检索](002-qdrant-vector-search.md)                 | 已采纳 |
| 003 | [JWT (HS256) 而非 RS256](003-jwt-hs256.md)                              | 已采纳 |
| 004 | [JSONB 存储 skills.content 与 compositions.items](004-jsonb-flexible-content.md) | 已采纳 |
| 005 | [后端用 Poetry、前端用 npm](005-polyglob-packaging.md)      | 已采纳 |
| 006 | [Next.js 15 App Router](006-nextjs-app-router.md)                      | 已采纳 |
| 007 | [v1 单租户，v1.2 多租户](007-tenancy-model.md)            | 已采纳 |
| 008 | [启动期密钥校验（fail-fast）](008-fail-fast-secrets.md)            | 已采纳 |
| 009 | [OWASP 安全头中间件](009-owasp-headers.md)              | 已采纳 |
| 010 | [Pre-commit 钩子 + Conventional Commits](010-pre-commit-and-commits.md) | 已采纳 |

## 格式

我们使用 [MADR](https://adr.github.io/madr/) 模板并做了轻量改造。每条 ADR 是
本目录中带顺序编号前缀的 Markdown 文件。**ADR 只能追加** —— 一旦采纳，
文件永远不再被编辑。如果某项决策后来被推翻，请写一条新 ADR 替代它。

## 价值

ADR 帮助我们：

- 更快地 onboarding 新贡献者
- 在两年后依然记得当初为什么这样选
- 在 PR 中避免重新讨论已定案的决策
