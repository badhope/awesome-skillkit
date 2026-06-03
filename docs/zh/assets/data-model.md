# 数据模型

数据模型刻意保持精简，核心围绕 **skill** 展开。大多数「附属」字段
（标签、依赖、版本）都是关联表或 JSONB 列，以便在不频繁迁移的
前提下让 schema 平滑演进。

![数据模型图](../assets/data-model.svg)

## 表

### `users`

系统的「行动者」。

| 字段               | 类型          | 说明                                |
|--------------------|---------------|-------------------------------------|
| `id`               | `uuid`        | 主键                                |
| `email`            | `varchar`     | 唯一                                |
| `username`         | `varchar`     | 唯一                                |
| `hashed_password`  | `varchar`     | bcrypt，工作因子 12                 |
| `full_name`        | `varchar`     | 可选                                |
| `is_active`        | `bool`        | 默认 `true`                         |
| `is_superuser`     | `bool`        | 默认 `false`                        |
| `created_at`       | `timestamptz` | 服务端时间                          |

### `skills`

核心实体。

| 字段              | 类型          | 说明                                          |
|-------------------|---------------|-----------------------------------------------|
| `id`              | `uuid`        | 主键                                          |
| `slug`            | `varchar`     | 唯一，用于 URL                                |
| `name`            | `varchar`     | 展示名                                        |
| `description`     | `text`        | 简短描述，用于卡片                            |
| `content`         | `jsonb`       | 完整内容（Markdown + 元数据）                 |
| `category_id`     | `uuid`        | FK → `categories.id`                          |
| `author_id`       | `uuid`        | FK → `users.id`（可空）                       |
| `version`         | `varchar`     | SemVer                                        |
| `license`         | `varchar`     | SPDX 标识                                     |
| `is_public`       | `bool`        | 未登录是否可见                                |
| `is_featured`     | `bool`        | 是否在首页推荐                                |
| `rating_avg`      | `numeric`     | 0–5                                           |
| `rating_count`    | `int`         |                                               |
| `download_count`  | `int`         |                                               |
| `view_count`      | `int`         |                                               |
| `usage_count`     | `int`         |                                               |
| `created_at`      | `timestamptz` | 服务端时间                                    |
| `updated_at`      | `timestamptz` | 服务端时间，自动更新                          |

### `skill_versions`

每个发布版本的 append-only 历史。用户编辑技能并升级版本时，
会插入一行。

| 字段         | 类型          | 说明                                |
|--------------|---------------|-------------------------------------|
| `id`         | `uuid`        | 主键                                |
| `skill_id`   | `uuid`        | FK → `skills.id`                    |
| `version`    | `varchar`     | SemVer，按技能唯一                  |
| `changelog`  | `text`        | Markdown                            |
| `content`    | `jsonb`       | 内容的快照                          |
| `created_at` | `timestamptz` |                                     |
| `created_by` | `uuid`        | FK → `users.id`                     |

### `categories`

两层分类（顶层 + 子分类）。

| 字段         | 类型          | 说明                                |
|--------------|---------------|-------------------------------------|
| `id`         | `uuid`        | 主键                                |
| `slug`       | `varchar`     | 唯一                                |
| `name`       | `varchar`     |                                     |
| `parent_id`  | `uuid`        | FK → `categories.id`（可空）        |
| `sort_order` | `int`         |                                     |
| `icon`       | `varchar`     | 图标名（Lucide）                    |
| `is_active`  | `bool`        |                                     |

### `tags`

技能的自由标签。

| 字段          | 类型      | 说明                                |
|---------------|-----------|-------------------------------------|
| `id`          | `uuid`    | 主键                                |
| `name`        | `varchar` | 唯一                                |
| `color`       | `varchar` | Hex 颜色                            |
| `description` | `text`    |                                     |

### `skill_tag_association`

多对多关联表。使用独立表（而非 SQLAlchemy 自动管理）以强制
复合主键。

| 字段       | 类型   | 说明                                |
|------------|--------|-------------------------------------|
| `skill_id` | `uuid` | FK → `skills.id`                    |
| `tag_id`   | `uuid` | FK → `tags.id`                      |

### `skill_dependencies`

「技能 A 依赖技能 B（且版本 ≥ N）」的有向图。

| 字段                    | 类型       | 说明                                       |
|-------------------------|------------|--------------------------------------------|
| `id`                    | `uuid`     | 主键                                       |
| `skill_id`              | `uuid`     | FK → `skills.id`                           |
| `depends_on_skill_id`   | `uuid`     | FK → `skills.id`                           |
| `version_constraint`    | `varchar`  | SemVer 约束，例如 `>=1.2.0,<2.0.0`         |
| `is_required`           | `bool`     | `false` 表示软依赖（推荐但非必需）          |
| `created_at`            | `timestamptz` |                                        |

### `skill_ratings`

每个 (user, skill) 一行。用户重复评分时，原地更新。

| 字段         | 类型          | 说明                                |
|--------------|---------------|-------------------------------------|
| `id`         | `uuid`        | 主键                                |
| `skill_id`   | `uuid`        | FK → `skills.id`                    |
| `user_id`    | `uuid`        | FK → `users.id`                     |
| `rating`     | `int`         | 1–5                                 |
| `comment`    | `text`        | 可选，最多 2 000 字符               |
| `created_at` | `timestamptz` |                                     |
| `updated_at` | `timestamptz` |                                     |

### `skill_usage_logs`

「用户 X 对技能 Z 做了 Y」事件的 append-only 日志。为分析
仪表盘提供数据。它**不是**早期草稿中提到的 `analytics_events`
表的替代 —— 那张表最终没有落地；当前唯一的事件入口是
`app.core.audit.log_event` 的审计日志。

| 字段         | 类型          | 说明                                          |
|--------------|---------------|-----------------------------------------------|
| `id`         | `uuid`        | 主键                                          |
| `skill_id`   | `uuid`        | FK → `skills.id`                              |
| `user_id`    | `uuid`        | FK → `users.id`（匿名事件可为 NULL）          |
| `action`     | `varchar`     | `view` · `download` · `use` · `rate` · `share` |
| `ip_address` | `varchar`     | 入库前做哈希                                  |
| `user_agent` | `varchar`     |                                               |
| `created_at` | `timestamptz` |                                               |

### `skill_compositions`

组合本身 —— 一个具名、带版本的技能集合。

| 字段          | 类型          | 说明                                |
|---------------|---------------|-------------------------------------|
| `id`          | `uuid`        | 主键                                |
| `slug`        | `varchar`     | 唯一                                |
| `name`        | `varchar`     |                                     |
| `description` | `text`        |                                     |
| `is_public`   | `bool`        |                                     |
| `owner_id`    | `uuid`        | FK → `users.id`                     |
| `created_at`  | `timestamptz` |                                     |
| `updated_at`  | `timestamptz` |                                     |

### `skill_composition_items`

组合内部的有序技能列表。这些 item 存为关系行（而非父表的
JSONB 列），以便重排、索引和外键校验。

| 字段            | 类型     | 说明                                |
|-----------------|----------|-------------------------------------|
| `id`            | `uuid`   | 主键                                |
| `composition_id`| `uuid`   | FK → `skill_compositions.id`        |
| `skill_id`      | `uuid`   | FK → `skills.id`                    |
| `sort_order`    | `int`    | 在组合中的展示顺序                  |
| `notes`         | `text`   | 针对该 item 的自由评论              |

## 索引

每张表都有 `created_at` 索引；外键都已建索引。`skills` 表还为
最常见的查询补充了几个复合索引：

- `(category_id, is_public, is_featured)` —— 首页
- `GIN(to_tsvector('english', name || ' ' || description))` ——
  词法搜索的兜底
- `(author_id)` —— 「某用户的技能」页面

## 为什么要把 `content` 和 `items` 存为 JSONB？

技能和组合都是**用户创作**的，并且形态在不断演进。如果强行套入
关系列，每次 schema 变化都要写迁移。把它们存为 JSONB，并在
读写时用 Pydantic 校验，能换来：

- Schema 灵活性
- 「JSON 中包含 X」类查询的 GIN 索引
- 形态的唯一真相源（Pydantic）

完整讨论见 [ADR 004](../adr/004-jsonb-flexible-content.md)。

## 接下来去哪里

- [搜索流水线](../search.md) —— 索引的构建方式
- [Schema 源码](https://github.com/badhope/AI-SKILL/blob/main/backend/app/models/skill.py) ——
  SQLAlchemy 模型
- [迁移](../development/migrations.md) —— schema 的演进方式
