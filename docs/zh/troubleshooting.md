# AI-SKILL — 故障排查

如果你卡住了，先扫一遍本页。如果还没解决，请开 [Q&A 讨论](https://github.com/badhope/AI-SKILL/discussions) 或 [bug 报告](https://github.com/badhope/AI-SKILL/issues/new?template=bug_report.md)。

---

## 整套栈启动不起来

### `docker compose up` 退出提示 "port is already allocated"

你的主机上 3000、5432、6379、6333 或 8000 端口被别的进程占用了。找出并停止它：

```bash
sudo lsof -i :5432
sudo lsof -i :8000
```

或者改 `docker-compose.yml` 里的端口映射：

```yaml
ports:
  - "5433:5432"   # 把 Postgres 暴露在 5433
```

### `JWT_SECRET_KEY environment variable is required in production`

`DEBUG=false` 但 `JWT_SECRET_KEY` 为空或短于 32 字符。生成一个：

```bash
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\"" >> .env
```

然后重启：`docker compose up -d`。

### `ADMIN_PASSWORD environment variable is not set`

同类问题，另一个变量。生产环境应用拒绝创建默认管理员。二选一：

```bash
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

或运行专用 CLI 来引导超级用户：

```bash
ADMIN_PASSWORD="$(openssl rand -base64 18)" \
ADMIN_EMAIL="ops@your-domain.com" \
ADMIN_USERNAME="ops" \
docker compose exec backend python -m app.scripts.create_admin
```

### `alembic.util.exc.CommandError: Can't locate revision identified by '...'`

`alembic_version` 表行指向了 migrations 目录里没有的版本号。这通常意味着
一次不完整的 `git pull` 或自定义 migration 被删除。恢复方式：

```bash
docker compose exec backend poetry run alembic stamp head
```

---

## 数据库错误

### `asyncpg.exceptions.UniqueViolationError`

你试图创建重复项（比如邮箱已存在）。API 返回 `409 Conflict`。如果这是非预期的，
看看是不是种子数据有残留：

```bash
docker compose exec -T postgres psql -U skill_user skill_db \
  -c "SELECT email FROM users;"
```

### `psycopg2.OperationalError: could not connect to server`

后端连不上 Postgres。检查：

```bash
docker compose ps postgres
docker compose logs postgres
```

如果数据库是 up 状态但后端还是连不上，核对 `DATABASE_URL` 中的 host。
在 Compose 网络里它必须是 `postgres`，而不是 `localhost`。

### `relation "users" does not exist`

迁移还没跑。执行：

```bash
docker compose exec backend poetry run alembic upgrade head
```

---

## 前端问题

### 浏览器控制台出现 `Failed to fetch`

浏览器连不上 API。在另一个标签里打开 <http://localhost:8000/health> —— 如果
能加载，后端是好的，问题出在 CORS 或 `NEXT_PUBLIC_API_URL`。

确认 `frontend/.env.local` 里的环境变量与后端实际监听位置一致：

```bash
# 打印运行中的前端容器实际使用的值
docker compose exec frontend printenv NEXT_PUBLIC_API_URL
# 在 dev 模式下应该是 http://localhost:8000（不带 /api/v1 后缀；
# Next.js 的 rewrite 会自动补 /api/*）
```

### `npm run build` 后页面是空白

多半是 SSR 阶段出错。查看构建日志和运行时日志：

```bash
npm run build 2>&1 | tee build.log
docker compose logs frontend
```

### `Module not found: Can't resolve '@ai-skill/sdk'`

本地的 TypeScript SDK 包没有 link。在 SDK 目录里执行：

```bash
cd sdk/typescript
npm run build
npm link
cd ../../frontend
npm link @ai-skill/sdk
```

或者直接装发布版：

```bash
npm install @ai-skill/sdk
```

---

## 向量搜索无结果

### 显而易见的查询返回空

Qdrant collection 可能还没建，或者 embedding 模型维度不对。检查：

```bash
curl http://localhost:6333/collections/skills
```

如果 collection 不存在，重启后端 —— 它会在启动时创建 collection。如果维度不对，
说明模型不匹配。两种解法：

- 把 `EMBEDDING_MODEL` 设回索引时用的同一个模型
- 换模型后重新建索引

### `QdrantException: Not found: Collection skills doesn't exist`

collection 丢了。最简单的修法是重启后端 —— `VectorSearchService` 在 `__init__`
里若发现 collection 不存在就会重建。如果是自定义部署且禁用了自动创建，
可以手动重建：

```bash
docker compose exec backend python -c "
import asyncio
from app.core.config import get_settings
from qdrant_client import QdrantClient

async def main():
    s = get_settings()
    q = QdrantClient(url=s.QDRANT_URL, api_key=s.QDRANT_API_KEY)
    if not q.collection_exists('skills'):
        q.create_collection(
            collection_name='skills',
            vectors_config={'size': s.EMBEDDING_DIMENSION, 'distance': 'Cosine'},
        )
        print('Created collection: skills')
    else:
        print('Collection already exists')

asyncio.run(main())
"
```

---

## 性能

### 搜索慢

1. 确认 HNSW 索引已建好（Qdrant dashboard 中 `status: green`）
2. 换用更小的模型时同步减小 `EMBEDDING_DIMENSION`
3. 在最热查询前面加 Redis 缓存
4. 给后端做 profile：

```bash
docker compose exec backend py-spy dump --pid 1
```

### 后端内存占用高

embedding 模型是惰性加载的。释放内存：

```bash
docker compose restart backend
```

要做永久修复，把 `EMBEDDING_MODEL=` 设成空串，然后把 embedding 服务
跑在独立的 worker 里。

### Postgres 慢

检查索引：

```sql
\d skills
```

定期跑 `VACUUM ANALYZE`：

```sql
VACUUM ANALYZE skills;
```

---

## 鉴权

### 刚登录就报 "Invalid token"

多半是后端或客户端的系统时钟不准。JWT 校验对时间敏感。

```bash
docker compose exec backend date
date
```

### "User is not active"

账户被停用了。用 SQL 重新激活：

```sql
UPDATE users SET is_active = true WHERE email = 'you@example.com';
```

### 忘记管理员密码

重置：

```bash
docker compose exec backend python -c "
import asyncio
from app.db.session import async_session_factory
from app.models.skill import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def reset():
    async with async_session_factory() as db:
        u = (await db.execute(select(User).where(User.email == 'admin@ai-skill.local'))).scalar_one()
        u.hashed_password = get_password_hash('NEW_PASSWORD_HERE')
        await db.commit()
        print('Password reset for', u.email)

asyncio.run(reset())
"
```

---

## CI 红了

### 首次运行 `ruff` 报了一堆错

跑自动修复：

```bash
cd backend && poetry run ruff check --fix app/
cd sdk/python && poetry run ruff check --fix skill_sdk/
```

### `mypy` 抱怨缺导入

把包加到 `pyproject.toml` 的 `[tool.mypy]` overrides，或者在导入处
加 `# type: ignore[import-untyped]`。

### `npm test` 超时

前端测试共用一个数据库。确保测试数据库是隔离的：

```bash
docker compose exec -T postgres \
  psql -U skill_user -c "CREATE DATABASE skill_test_db;"
```

---

## 日志

### 日志在哪？

```bash
docker compose logs backend   | tail -200
docker compose logs frontend  | tail -200
docker compose logs postgres  | tail -200
docker compose logs qdrant    | tail -200
```

### 打开 debug 日志

```bash
# .env
LOG_LEVEL=DEBUG
```

然后 `docker compose restart backend`。

---

## 还是没解决？

1. 搜 [现有 issue](https://github.com/badhope/AI-SKILL/issues)
2. 搜 [Discussions / Q&A](https://github.com/badhope/AI-SKILL/discussions/categories/q-a)
3. 开 [新 issue](https://github.com/badhope/AI-SKILL/issues/new?template=bug_report.md)，
   附上 `make health-check` 与 `docker compose logs backend` 的输出
