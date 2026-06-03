# AI-SKILL — 架构

本文档描述 AI-SKILL 的运行时架构、数据流与部署拓扑，面向在扩展系统前需要先理解其运作方式的运维与贡献者。

如需高层概览，请参阅 [首页中的图示](index.md#architecture)。
关于部署的细节，请参阅 [deployment.md](../en/deployment.md)。

> **翻译状态**：本文档为官方架构的中文译本。链接到的部分页面
> （如 deployment.md、reference/environment.md、ADR 系列）暂未翻译，
> 链接保持指向英文原文。

---

## 1. 分层视图

AI-SKILL 划分为五个清晰的层次。每一层职责单一，通过类型化契约与下一层通信。

```
┌──────────────────────────────────────────────────────────────────┐
│  L1  客户端                                                      │
│      浏览器（PWA）· 移动浏览器 · Python SDK · TS SDK              │
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTPS · JSON / form-data
┌──────────────────────────────▼───────────────────────────────────┐
│  L2  边缘层                                                      │
│      Nginx / Caddy / Traefik （TLS 终止、限流、gzip）              │
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTP
┌──────────────────────────────▼───────────────────────────────────┐
│  L3  应用层                                                      │
│      前端 ── Next.js 15 （App Router、SSR + RSC）                 │
│      后端 ── FastAPI 0.115  （async，自动生成 OpenAPI）            │
└──────────────────────────────┬───────────────────────────────────┘
                               │  asyncpg / qdrant-client / redis-py
┌──────────────────────────────▼───────────────────────────────────┐
│  L4  有状态服务层                                                │
│      PostgreSQL 16  · Redis 7  · Qdrant 1.9+  · 对象存储          │
└──────────────────────────────┬───────────────────────────────────┘
                               │  Alembic 迁移
┌──────────────────────────────▼───────────────────────────────────┐
│  L5  运维层                                                      │
│      Docker Compose  · GitHub Actions  · Sentry  · OTel          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. 后端模块结构

```
backend/app/
├── main.py                # FastAPI 入口、中间件链、生命周期
├── api/                   # 路由（v1）
│   └── v1/
│       ├── auth.py        #  /api/v1/auth/{register,login,refresh,logout,me}
│       ├── skills.py      #  /api/v1/skills, /api/v1/skills/{slug}
│       ├── categories.py  #  /api/v1/categories, /api/v1/categories/{slug}
│       ├── tags.py        #  /api/v1/tags, /api/v1/tags/{name}
│       ├── compositions.py#  /api/v1/compositions, /api/v1/compositions/{slug}
│       ├── analytics.py   #  /api/v1/analytics/{overview,skills,usage}
│       └── users.py       #  /api/v1/users
├── core/                  # 横切关注点
│   ├── config.py          # Pydantic-Settings，加载 .env
│   ├── security.py        # JWT 签发 / 校验，密码哈希
│   ├── deps.py            # FastAPI 依赖：get_current_user、get_request_locale
│   ├── i18n.py            # gettext 翻译 + locale 探测
│   ├── content_i18n.py    # Skill.content 按 locale 切片
│   ├── pagination.py      # 通用 ?page=&page_size= 校验
│   ├── audit.py           # 结构化审计日志
│   ├── logging.py         # JSON formatter
│   └── seed.py            # 初始化种子数据（分类、标签）
├── middleware/            # 中间件
│   ├── locale.py          # 请求 locale 探测 + Content-Language 响应头
│   ├── error_handler.py   # 统一 5xx 处理 + request_id
│   ├── rate_limit.py      # 基于 Redis 的滑动窗口限流
│   └── security_headers.py# OWASP 推荐头
├── models/                # SQLAlchemy ORM
├── schemas/               # Pydantic 请求/响应模型
├── services/              # 业务逻辑（独立于 FastAPI，可独立测试）
│   ├── vector_search.py   # Qdrant 客户端封装
│   ├── analytics.py       # 仪表盘聚合
│   ├── cache.py           # Redis 缓存抽象
│   ├── import_export.py   # 技能导入/导出
│   ├── notification.py    # 通知通道（邮件、Webhook）
│   ├── skill_composer.py  # 技能组合（多技能编排）
│   └── skill_validator.py # 技能内容校验
├── db/                    # 异步 SQLAlchemy 会话管理
├── locales/               # 后端 gettext 翻译（en/zh）
│   ├── en/LC_MESSAGES/messages.{po,mo}
│   └── zh/LC_MESSAGES/messages.{po,mo}
├── cli/                   # Typer CLI（make 命令的薄封装）
└── scripts/               # 一次性运维脚本
```

每一层依赖都向下流动，且只通过显式导入关系。

---

## 3. 请求生命周期

一次典型的 `GET /api/v1/skills/{slug}` 请求经过这些步骤：

1. **TLS 终止**（边缘 / 反向代理）
2. **LocaleMiddleware** 解析 `?lang=`、`X-Locale`、`Accept-Language`，按顺序
   回退到 `DEFAULT_LOCALE`，把结果写入 `request.state.locale`，并在响应中
   设置 `Content-Language` 与 `Vary: Accept-Language, X-Locale`。
3. **SecurityHeadersMiddleware** 注入 OWASP 头（`X-Content-Type-Options`、`Strict-Transport-Security` 等）。
4. **RateLimitMiddleware** 基于 Redis 滑动窗口检查（参见 `ENDPOINT_RATE_LIMITS`），命中时返回带 `Retry-After` 的 429。
5. **ErrorHandlerMiddleware** 包裹下游，捕获未处理异常并以本地化消息返回 5xx。
6. **FastAPI 路由解析** + 依赖注入（`get_db`、`get_current_user`、`get_request_locale`）。
7. **业务服务** 通过 SQLAlchemy 异步会话查询 Postgres，必要时通过 Qdrant 客户端
   做向量搜索。
8. **响应模型校验** —— Pydantic schema 把 ORM 对象转成 JSON；`content_i18n.pick_translation`
   按 `?locale=` 切片 `Skill.content`。
9. **响应体** 反向穿过中间件链；每个中间件都可以追加或修改响应头。
10. **审计日志** —— 状态变更类（POST/PUT/DELETE）写入 `audit_logs` 表。

---

## 4. 数据模型

主要实体（详见 `docs/assets/data-model.md`）：

| 实体 | 表 | 关键字段 |
|------|-----|----------|
| User | `users` | email、username、hashed_password、is_superuser |
| Skill | `skills` | name、slug、description、content (JSONB)、extra_metadata (JSONB) |
| SkillVersion | `skill_versions` | skill_id、version、content (JSONB) |
| SkillDependency | `skill_dependencies` | skill_id、depends_on_skill_id、version_constraint |
| SkillRating | `skill_ratings` | skill_id、user_id、rating、comment |
| SkillUsageLog | `skill_usage_logs` | skill_id、user_id、action、created_at |
| Category | `categories` | name、slug、parent_id、sort_order |
| Tag | `tags` | name、color、usage_count |
| SkillComposition | `skill_compositions` | name、slug、is_public、metadata (JSONB) |
| SkillCompositionItem | `skill_composition_items` | composition_id、skill_id、sort_order、notes |

### `Skill.content` 约定

`Skill.content` 是 JSONB 列；它接受两种形态：

1. **扁平（兼容旧数据）** —— 一个普通字典，对所有 locale 一致返回：

   ```json
   {"summary": "...", "body": "..."}
   ```

2. **本地化** —— 包含 `default_locale` 与 `translations` 字典：

   ```json
   {
     "default_locale": "en",
     "translations": {
       "en": {"summary": "...", "body": "..."},
       "zh": {"summary": "...", "body": "..."}
     }
   }
   ```

`GET /api/v1/skills/{slug}?locale=zh` 把 `content` 切片为请求的 locale；
`?locale=all` 返回完整翻译字典（用于编辑界面）。详见 [配置参考](../en/reference/configuration.md) 与 `app.core.content_i18n`。

---

## 5. 搜索流水线

```
                      用户查询（自然语言）
                              │
                              ▼
                    ┌────────────────────┐
                    │  EmbeddingService   │  ← Sentence-BERT（多语言）
                    │  (Qdrant 客户端)    │
                    └────────┬───────────┘
                             │ vector(1024-d)
                             ▼
                    ┌────────────────────┐
                    │   Qdrant collection │  ← 余弦相似度 top-K
                    │   "skills"         │
                    └────────┬───────────┘
                             │ (skill_id, score)
                             ▼
                    ┌────────────────────┐
                    │  Postgres join      │  ← SELECT * FROM skills WHERE id IN (...)
                    │  + 业务过滤         │     业务侧再按 category / status / is_public 过滤
                    └────────┬───────────┘
                             │ SkillResponse[]
                             ▼
                          JSON
```

- 索引流程在 `services/vector_search.py::index_skill()` 中实现，技能 POST/PUT 后由 Celery 任务异步触发。
- 删除技能会同步从 Qdrant 中移除（参见 `delete_skill()`）。

---

## 6. 部署拓扑

参见 [deployment.md](deployment.md) 了解：

- 单 VPS、Docker Compose
- Kubernetes（Kustomize + Helm chart 见 `deploy/k8s/`）
- 托管 PaaS（Render、Fly.io、Railway）

各拓扑都使用相同的环境变量约定（参见 [reference/environment.md](reference/environment.md)）。

---

## 7. 进一步阅读

- [ADR 002 — Qdrant for vector search](../en/adr/002-qdrant-vector-search.md) （英文）
- [ADR 004 — JSONB for skills.content](../en/adr/004-jsonb-flexible-content.md) （英文）
- [ADR 006 — Next.js 15 App Router](../en/adr/006-nextjs-app-router.md) （英文）
- [ADR 007 — Single-tenant v1, multi-tenant v1.2](../en/adr/007-tenancy-model.md) （英文）
