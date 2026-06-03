# AI-SKILL — 故障排查

> 想看完整版故障排查？请见
> [docs/troubleshooting.md](docs/troubleshooting.md)。本页是
> README 引用的短版。

## 整套栈启动不起来

| 症状 | 解法 |
|---|---|
| `port already allocated` | 释放端口：`sudo lsof -i :8000` 并 kill，或在 `docker-compose.yml` 中改映射 |
| `JWT_SECRET_KEY environment variable is required in production` | 在 `.env` 中设置 `JWT_SECRET_KEY="$(openssl rand -hex 32)"` |
| `ADMIN_PASSWORD environment variable is not set` | 在 `.env` 中设置 `ADMIN_PASSWORD="$(openssl rand -base64 18)"`，或运行 `make create-admin` |
| `relation "users" does not exist` | 缺迁移：`docker compose exec backend poetry run alembic upgrade head` |

## 前端空白

- 打开浏览器 dev-tools → Network 标签 → 找失败的请求
- 确认 `VITE_API_BASE_URL` 指向后端
- 确认 CORS：`.env` 中 `BACKEND_CORS_ORIGINS` 包含前端来源

## 搜索无结果

- 检查 Qdrant：`curl http://localhost:6333/collections`
- 确认 embedding 模型维度与索引维度一致
- 查后端日志中是否出现 `QdrantException`

## 忘记管理员密码

通过 SQL 重置——见 [docs/zh/troubleshooting.md](docs/zh/troubleshooting.md#forgot-the-admin-password)。

## 日志

```bash
make logs                          # 全部服务
docker compose logs -f backend     # 只看后端
```

## 还没解决？

1. 查阅 [docs/zh/troubleshooting.md](docs/zh/troubleshooting.md)
2. 搜索 [已有 issue](https://github.com/badhope/AI-SKILL/issues)
3. 开 [新 bug 报告](https://github.com/badhope/AI-SKILL/issues/new?template=bug_report.md)，
   附上 `make health-check` 与 `docker compose logs` 的输出
