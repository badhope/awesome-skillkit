本项目的所有重要变更都记录在此文件中。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目同时遵守 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

---

## [1.0.0] - 2026-06-01

### 新增

- AI-SKILL 首次发布 —— 一个可自托管的通用智能体技能库平台
- 全栈 monorepo：FastAPI 后端、Next.js 15 前端、Python 与 TypeScript 双 SDK
- 移动优先的响应式设计，支持 PWA
- 中英文国际化（i18n），支持运行时切换语言
- 基于 Sentence-BERT 嵌入的 Qdrant 向量搜索
- BM25 + 稠密向量的混合检索，最大化相关性
- 语义化版本管理，包含完整的技能变更历史
- 技能依赖管理，支持版本约束与环依赖检测
- 用户评分与评论系统（1-5 星）
- 分析仪表盘，提供实时使用统计与趋势
- REST API，自动生成 OpenAPI 文档（Swagger / ReDoc）
- 基于 JWT 的认证，支持 access / refresh 双令牌轮换
- 基于角色的访问控制（RBAC）
- 速率限制与 API 防滥用
- OWASP 安全响应头（HSTS、CSP、X-Frame-Options、Referrer-Policy、Permissions-Policy）
- 结构化 JSON 日志，日志级别可配置
- OpenTelemetry 集成，支持分布式追踪
- Sentry 错误监控与性能追踪
- Python SDK：原生异步、类型注解
- TypeScript SDK：完整类型定义
- Docker Compose 一键部署
- GitHub Actions CI/CD 流水线（lint、test、build、publish）
- 基于 Alembic 的数据库迁移
- Redis 缓存层，LRU 淘汰策略
- PostgreSQL 16 + asyncpg 驱动，高性能查询
- Celery 任务队列，后台异步处理
- S3 兼容对象存储后端
- CLI 管理工具，基于 Rich 的终端 UI
- 完善的单元测试与集成测试套件
- 代码质量工具：ruff、mypy、ESLint、Prettier、pre-commit 钩子
- Issue 模板、PR 模板、CODEOWNERS、Dependabot 配置
- 完整开源文档：LICENSE、CONTRIBUTING、SECURITY、CODE_OF_CONDUCT、CHANGELOG

### 备注

本次发布附带一个**完全可用的空库**。每个运维方需自行填充
技能数据，或从外部注册中心导入。平台本身已具备生产可用性，
数据集刻意不打包。

---

[1.0.0]: https://github.com/badhope/AI-SKILL/releases/tag/v1.0.0
