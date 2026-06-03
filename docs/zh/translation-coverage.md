# 翻译覆盖率

本文档追踪文档站的简体中文翻译进度。CI 会在每次 PR 时校验"已翻译"页面的
`mkdocs build` 通过；缺页或构建失败会让 CI 变红。

> 想帮助翻译？参见 [`CONTRIBUTING.md → 翻译贡献`](community/contributing.md#i18n-contributing) 维护的中英术语表。

## 已翻译（22 / 22 = 100%）

### 入门（4/4）

- [x] [首页](index.md)
- [x] [安装](getting-started/installation.md)
- [x] [快速开始](getting-started/quickstart.md)
- [x] [配置](getting-started/configuration.md)

### 核心文档（3/3）

- [x] [架构](architecture.md)
- [x] [部署](deployment.md)
- [x] [故障排查](troubleshooting.md)

### 社区（5/5）

- [x] [常见问题](community/faq.md)
- [x] [路线图](community/roadmap.md)
- [x] [贡献指南](community/contributing.md)
- [x] [行为准则](community/code-of-conduct.md)
- [x] [更新日志](community/changelog.md)

### 架构决策记录（10/10）

- [x] ADR 001 — Pydantic v2 + ClassVar Depends
- [x] ADR 002 — Qdrant 向量检索
- [x] ADR 003 — 选用 HS256 JWT
- [x] ADR 004 — `skills.content` 与 `compositions.items` 的存储形式
- [x] ADR 005 — 后端用 Poetry、前端用 npm
- [x] ADR 006 — Next.js 15 App Router
- [x] ADR 007 — v1 单租户，v1.2 多租户
- [x] ADR 008 — 启动期密钥校验（fail-fast）
- [x] ADR 009 — OWASP 安全头中间件
- [x] ADR 010 — Pre-commit 钩子 + Conventional Commits

### 运维（4/4）

- [x] [运维总览](operations/index.md)
- [x] [安全](operations/security.md)
- [x] [备份与恢复](operations/backup.md)
- [x] [可观测性](operations/observability.md)

### 开发（6/6）

- [x] [开发总览](development.md)
- [x] [新增 API 端点](development/adding-endpoint.md)
- [x] [新增前端页面](development/adding-page.md)
- [x] [数据库迁移](development/migrations.md)
- [x] [测试](development/testing.md)
- [x] [发布流程](development/release.md)

### 参考（4/4）

- [x] [配置参考](reference/configuration.md)
- [x] [命令行](reference/cli.md)
- [x] [环境变量](reference/environment.md)
- [x] [HTTP 状态码](reference/http-status-codes.md)

### SDK（3/3）

- [x] [SDK 总览](sdks/README.md)
- [x] [Python SDK](sdks/python.md)
- [x] [TypeScript SDK](sdks/typescript.md)

### 示例（5/5）

- [x] [示例总览](examples/index.md)
- [x] [REST（curl + .http）](examples/rest.md)
- [x] [Python 示例](examples/python.md)
- [x] [TypeScript 示例](examples/typescript.md)
- [x] [Postman 集合](examples/postman.md)

### 架构资产（2/2）

- [x] [数据模型](assets/data-model.md)
- [x] [搜索流水线](search.md)

## 待翻译（0 / 22 = 0%）

无。

## 跨语言链接策略

- 已翻译页面在中文站点中**互相链接**（`docs/zh/foo` 链到 `docs/zh/bar`）。
- 中文页面链接到未翻译页面时，**直接链英文版本**（例如 `../contributing.md`），
  以避免双站点互引产生"内容跳回英文"的怪现象。
- mkdocs 链接检查中保留 `validation.links.not_found: warn`，让链接警告
  显式可见但不阻塞构建。

## 翻译工作流

参见 [`CONTRIBUTING.md → 翻译贡献`](community/contributing.md#i18n-contributing) 维护的
中英术语表与完整流程。CI 工作流 `.github/workflows/i18n.yml` 会在 PR 时跑：

1. `make i18n-compile && make i18n-check` — 后端 gettext 完整性
2. `mkdocs build -f docs/mkdocs.yml` — 多语言 docs 构建
3. 断言 `site/index.html`（英文）和 `site/zh/index.html`（中文）都存在，且
   中文版**不**含 `open-source universal`（防止 i18n 插件配置错把英文源镜像到 `/zh/`）
