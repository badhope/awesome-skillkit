# AI-SKILL — 路线图

本文档追踪项目方向。它是一份动态清单 —— 各项会在各阶段间迁移。

最近更新：2026-06-02

---

## 已发布

- [x] 可自托管的 FastAPI 后端，附 OpenAPI 自动文档
- [x] Next.js 15 移动优先前端，中英文 i18n
- [x] JWT 鉴权、RBAC、限流、审计日志、安全头
- [x] Qdrant 混合向量检索（BM25 + 稠密向量 + 重排）
- [x] Alembic 迁移，幂等的 category / tag 种子
- [x] Python 与 TypeScript SDK
- [x] Docker Compose 一键部署
- [x] CI/CD：lint、test、build、推送 Docker 镜像
- [x] 完整开源文档集：LICENSE、CONTRIBUTING、SECURITY、CODE_OF_CONDUCT、CHANGELOG、architecture、deployment、troubleshooting、development

## 进行中 — 1.1（目标 2026 Q3）

- [ ] **公共技能注册表** —— 社区共建的技能目录，任何人都可拉取。与平台本体解耦。
- [ ] 与 REST 并行的 **GraphQL 端点**
- [ ] **按租户的 API key**（在用户 JWT 之外）
- [ ] 实时分析的 **WebSocket** 推送
- [ ] 前端的 **Composition 可视化编辑器**
- [ ] **技能评分细分**（清晰度、性能、可移植性）
- [ ] 面向技能作者的 **CLI 工具** —— `ai-skill init` / `validate` / `publish`

## 计划中 — 1.2（目标 2026 Q4）

- [ ] 多语言 i18n（西班牙语、法语、日语、韩语）
- [ ] 技能包（下载/上传 `.zip` 形式的技能 + 元数据）
- [ ] 版本对比 UI
- [ ] OAuth 提供方（Google、GitHub）补充邮箱/密码
- [ ] 可插拔的存储后端（S3、R2、GCS、MinIO）
- [ ] 可插拔的向量后端（pgvector、Milvus、Weaviate）
- [ ] 按组织计费（Stripe）
- [ ] 审计日志保留 + GDPR 抹除工具

## 评估中 — 2.0+

- [ ] 技能执行沙箱（用 WASM 运行不可信技能）
- [ ] 市场 / 付费技能
- [ ] 技能推荐引擎（协同过滤）
- [ ] 原生移动 App（iOS、Android）
- [ ] Slack / Discord / Teams bot
- [ ] VSCode 插件

## 非目标

以下是**明确不做**的事：

- **通用 CMS** —— 已有更好的工具（Strapi、Directus、Sanity）。
- **通用 LLM 聊天产品** —— AI-SKILL 是技能编目，不是聊天 UI。
- **工作流引擎** —— Composition 描述依赖关系，不描述执行语义。执行请用现有生态（Temporal、Prefect、Airflow）。
- **网络爬虫** —— 技能是手写的，不是抓的。

## 如何影响路线图

1. 提一个 [Feature Request](https://github.com/badhope/AI-SKILL/issues/new?template=feature_request.md)。
2. 或在 [Discussions / Ideas](https://github.com/badhope/AI-SKILL/discussions/categories/ideas) 发起讨论。
3. 或直接发 PR —— 参见 [CONTRIBUTING.md](CONTRIBUTING.md)。
