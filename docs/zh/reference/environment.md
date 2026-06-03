# 环境变量

本文档列出了 AI-SKILL 后端的**全部**环境变量，按逻辑分组。

> 启动顺序 / 校验参见 [配置参考](configuration.md)。
> 运维向快速摘要参见 [入门 → 配置](../getting-started/configuration.md)。

---

## 约定

- **大小写敏感** —— 字段名就是环境变量名（`JWT_SECRET_KEY` 不是
  `jwt_secret_key`）
- **大写蛇形** —— `DB_POOL_SIZE` 而非 `dbPoolSize`
- **列表** —— 在 Python 中是 `list[str]`；在 `.env` 中是逗号分隔字符串
- **布尔** —— `"true"`、`"1"`、`"yes"` 为真；其余为假
- **空字符串** —— 通常**意味着未设置**（例：`DATABASE_URL=""` 触发
  回退逻辑）

---

## Application

| 变量          | 类型      | 默认值                 | 说明                                       |
|---------------|-----------|-----------------------|-------------------------------------------|
| `APP_NAME`    | `str`     | `"AI-SKILL"`          | 在 OpenAPI 元信息、CLI 横幅中出现            |
| `APP_VERSION` | `str`     | `"0.1.0"`             | 出现在 `/health` 响应中                      |
| `DEBUG`       | `bool`    | `false`               | `true` 时启用 OpenAPI 文档、`/docs`、宽松认证 |
| `API_PREFIX`  | `str`     | `"/api/v1"`           | 所有路由的前缀                              |

## Database

| 变量                       | 类型     | 默认值              | 说明                       |
|---------------------------|--------|--------------------|---------------------------|
| `DATABASE_URL`            | `str`  | *(无)*             | asyncpg DSN，必填           |
| `DATABASE_POOL_SIZE`      | `int`  | `10`               | asyncpg 连接池大小          |
| `DATABASE_MAX_OVERFLOW`   | `int`  | `20`               | 超出池大小后允许的临时连接     |
| `DATABASE_POOL_TIMEOUT`   | `int`  | `30`               | 等待池中连接的秒数            |
| `DATABASE_POOL_RECYCLE`   | `int`  | `1800`             | 连接回收的秒数                |

## Redis

| 变量               | 类型    | 默认值         | 说明                  |
|-------------------|--------|--------------|----------------------|
| `REDIS_URL`       | `str`  | *(无)*        | redis-py 连接串，必填  |
| `REDIS_POOL_SIZE` | `int`  | `10`          | 连接池大小            |

## Qdrant

| 变量             | 类型    | 默认值     | 说明                          |
|-----------------|--------|----------|------------------------------|
| `QDRANT_URL`    | `str`  | *(无)*   | Qdrant HTTP 端点。设为空字符串回退到 Postgres 纯词法检索 |
| `QDRANT_API_KEY`| `str`  | `None`    | Qdrant Cloud 必填             |

## Auth

| 变量                            | 类型    | 默认值      | 说明                                |
|--------------------------------|--------|------------|------------------------------------|
| `JWT_SECRET_KEY`               | `str`  | *(无)*     | HS256 签名密钥；生产模式 32+ 字符必填 |
| `JWT_ALGORITHM`                | `str`  | `"HS256"`  |                                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | `int`  | `30`       | 访问令牌生命周期                    |
| `REFRESH_TOKEN_EXPIRE_DAYS`    | `int`  | `7`        | 刷新令牌生命周期                    |

## CORS

| 变量                    | 类型             | 默认值              | 说明                              |
|------------------------|------------------|---------------------|----------------------------------|
| `BACKEND_CORS_ORIGINS` | `list[str]`      | `[]`                | 允许的来源列表（逗号分隔或 JSON 列表） |

## Storage

| 变量              | 类型    | 默认值       | 说明                  |
|------------------|--------|------------|----------------------|
| `STORAGE_TYPE`   | `str`  | `"local"`  | `local` 或 `s3`        |
| `S3_BUCKET`      | `str`  | `None`     |                      |
| `S3_ACCESS_KEY`  | `str`  | `None`     |                      |
| `S3_SECRET_KEY`  | `str`  | `None`     |                      |
| `S3_REGION`      | `str`  | `None`     |                      |
| `S3_ENDPOINT_URL`| `str`  | `None`     | MinIO/R2 兼容接入点   |

## Embedding

| 变量                 | 类型    | 默认值                                      | 说明                          |
|---------------------|--------|--------------------------------------------|------------------------------|
| `EMBEDDING_MODEL`   | `str`  | `"sentence-transformers/all-mpnet-base-v2"` | HuggingFace 模型 id           |
| `EMBEDDING_DIMENSION`| `int` | `768`                                       | 与所选模型一致                  |

## Logging

| 变量          | 类型    | 默认值      | 说明                              |
|--------------|--------|------------|----------------------------------|
| `LOG_LEVEL`  | `str`  | `"INFO"`   | `DEBUG`、`INFO`、`WARNING`、`ERROR` |
| `LOG_FORMAT` | `str`  | `"json"`   | `json`（生产）或 `console`（开发） |

## Rate limit

| 变量                  | 类型    | 默认值      | 说明                          |
|----------------------|--------|------------|------------------------------|
| `RATE_LIMIT_DEFAULT` | `int`  | `100`      | 每个 IP 在每个时间窗内允许的请求数 |
| `RATE_LIMIT_WINDOW`  | `int`  | `60`       | 时间窗长度（秒）               |

## Sentry

| 变量                            | 类型    | 默认值   | 说明                          |
|--------------------------------|--------|----------|------------------------------|
| `SENTRY_DSN`                   | `str`  | `None`   | 留空则关闭 Sentry            |
| `SENTRY_TRACES_SAMPLE_RATE`    | `float`| `0.1`    |                              |
| `SENTRY_PROFILES_SAMPLE_RATE`  | `float`| `0.1`    |                              |

## Admin

| 变量              | 类型    | 默认值          | 说明                          |
|------------------|--------|----------------|------------------------------|
| `ADMIN_EMAIL`    | `str`  | *(无)*         | 首次启动时种子管理员邮箱        |
| `ADMIN_USERNAME` | `str`  | *(无)*         | 首次启动时种子管理员用户名      |
| `ADMIN_PASSWORD` | `str`  | *(无)*         | 首次启动时种子管理员密码；缺失时跳过 seed |
| `ADMIN_FULL_NAME`| `str`  | `"Admin"`      |                              |

## Locale

| 变量               | 类型        | 默认值     | 说明                          |
|-------------------|------------|------------|------------------------------|
| `DEFAULT_LOCALE`  | `str`      | `"en"`     | 客户端无 `?lang=` / `Accept-Language` 时的回退 |
| `SUPPORTED_LOCALES`| `list[str]`| `["en", "zh"]` | 启用 `compile_catalogs` 的语言列表    |

> 跨多语言键完整性由 `make i18n-check` 强制。CI 会在 PR 时跑这条命令。

---

## 下一步

- [配置参考](configuration.md) —— 底层的 `Settings` 类与 `@model_validator`
- [配置（入门）](../getting-started/configuration.md) —— 一份 .env 文件怎么写
- [.env.example](https://github.com/badhope/AI-SKILL/blob/main/backend/.env.example) —— 完整可用的模板
