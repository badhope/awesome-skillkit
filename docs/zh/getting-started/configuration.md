# 配置

AI-SKILL 完全通过环境变量进行配置。**没有** `config.yaml`，**没有** 管理员全局设置 UI。

## 配置加载顺序

Pydantic v2 按以下优先级加载设置：

1. 真实环境变量（最高优先级）
2. 工作目录下的 `.env` 文件
3. 代码内置的合理默认值（最低优先级 —— 对安全敏感值**不采用**）

## 如何加载配置文件

```bash
# 1. 复制示例
cp .env.example .env

# 2. 生成三个应用拒绝以默认值出发的密钥
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

## 启动期密钥校验（fail-fast）

在生产环境（`DEBUG=false`）下，如果以下条件不满足，后端**拒绝启动**：

- `JWT_SECRET_KEY` 缺失、短于 32 字符，或与已知的弱默认值匹配
- `ADMIN_PASSWORD` 缺失（seed 模块会跳过管理员创建）
- `POSTGRES_PASSWORD` 缺失（docker-compose 服务使用 `${VAR:?...}`，容器会直接启动失败）

在 debug 模式（`DEBUG=true`）下，后端会为**每个进程**生成一个**临时随机**的 `JWT_SECRET_KEY` 并打印警告。这让本地开发零摩擦，同时不削弱生产环境。

## 环境变量参考

完整参考见 [环境变量](../reference/environment.md)。下面是速览：

| 变量 | 用途 | 生产必填？ |
|-------------------|----------------------------------------|-------------------|
| `JWT_SECRET_KEY`  | HS256 签名密钥                      | 是               |
| `ADMIN_PASSWORD`  | 第一个超级用户密码               | 是（seed 需要）   |
| `POSTGRES_PASSWORD` | Postgres 超级用户密码           | 是               |
| `DATABASE_URL`    | asyncpg DSN                            | 是               |
| `REDIS_URL`       | redis-py 连接串                     | 是               |
| `QDRANT_URL`      | Qdrant HTTP 端点                   | 是               |
| `BACKEND_CORS_ORIGINS` | 逗号分隔的允许来源列表         | 是               |
| `DEBUG`           | true = 宽松 / false = 严格     | 否（默认 false）|
| `SENTRY_DSN`      | Sentry 错误监控                | 否                |
| `STORAGE_TYPE`    | `local` 或 `s3`                        | 否（默认 local）|
| `EMBEDDING_MODEL` | HuggingFace 模型 id                   | 否（默认 `sentence-transformers/all-mpnet-base-v2`） |
| `EMBEDDING_DIMENSION` | 向量维度                  | 否（默认 768）  |
| `LOG_LEVEL`       | `DEBUG` / `INFO` / `WARNING` / …       | 否（默认 INFO） |
| `LOG_FORMAT`      | `json` / `console`                     | 否（默认 json） |
| `RATE_LIMIT_DEFAULT` | 每个 IP 在每个时间窗内允许的请求数          | 否（默认 100）  |
| `RATE_LIMIT_WINDOW`  | 时间窗长度，单位秒              | 否（默认 60）   |

## 多环境工作流

推荐的做法是每个环境一个 `.env` 文件，且不入版本控制：

```bash
# 本地开发
.env

# 预发
.env.staging

# 生产
.env.production
```

启动前把对应文件复制到 `.env`：

```bash
cp .env.production .env
docker compose up -d
```

生产环境建议接入 Vault / AWS Secrets Manager / Doppler / Infisical 等密钥管理服务，在容器启动时注入。

## 密钥生成片段

```bash
# JWT 密钥（256 位）
openssl rand -hex 32

# 强随机密码
openssl rand -base64 18

# UUID（用于 category_id 等）
python3 -c "import uuid; print(uuid.uuid4())"
```

## 接下来读什么

- [环境变量参考](../reference/environment.md) — 每个变量、每个默认值、每个约束
- [配置参考](../reference/configuration.md) — 底层的 `Settings` 类
