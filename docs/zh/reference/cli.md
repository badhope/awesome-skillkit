# CLI

后端带有一组小型的命令行工具。它们位于 `backend/app/scripts/`，以 Python
模块形式运行。

## `python -m app.scripts.create_admin`

引导首个超级用户（交互式）。

```bash
ADMIN_PASSWORD='<strong>' \
ADMIN_EMAIL='ops@example.com' \
ADMIN_USERNAME='ops' \
python -m app.scripts.create_admin
```

如果未设置 `ADMIN_PASSWORD`，脚本会交互式提示输入（并要求确认）。它会拒绝：

- 短于 12 字符的密码
- 常见弱密码（`password`、`admin`、`changeme` 等）
- 覆盖已存在的同邮箱或同用户名的用户

## `skill-cli index rebuild`

重新索引 Qdrant collection 中的每个公开技能。**当** 切换 `EMBEDDING_MODEL`
**或** 数据库手动修复后**运行**此命令。

```bash
cd backend
poetry run python -m app.cli index rebuild --yes
```

| 标志        | 默认值 | 用途                          |
|-------------|---------|-------------------------------|
| `--yes`     | false   | 跳过交互式确认                |

该命令是**幂等**的 —— 再次运行会就地重建 collection；现有 points 在新 points
写入前被清除。

## `python -m app.core.seed`

幂等的 category、tag 种子（可选地含首个管理员）。在后端启动时自动调用；很少
手动运行。

```bash
python -m app.core.seed
```

在生产中，除非设置了 `ADMIN_PASSWORD`，否则跳过 admin seed 步骤。

## `python scripts/health_check.py`

向运行中的后端及其依赖发出请求并打印状态报告。在部署流水线和事后分析中
很有用。

```bash
python scripts/health_check.py
# 或，使用 Makefile：
make health-check
```

| 检查         | 作用                                |
|--------------|-------------------------------------|
| PostgreSQL   | 连接 `DATABASE_URL` 并执行 `SELECT version()` |
| Redis        | 连接 `REDIS_URL` 并执行 `PING`       |
| Qdrant       | 调用 `GET ${QDRANT_URL}/health`（或在不可用时回退到 `/collections`） |
| API          | 调用 `GET ${API_URL}/health` 并读取 `app_name` / `version` |

退出码：

- `0` —— 全部检查通过
- `1` —— 至少一个检查失败

## `skill-cli`（进程内 Typer 应用）

`backend/app/cli/main.py` 暴露了一个 `skill-cli` 用于不需要 HTTP 的常规
运维任务。它是本项目**规范的 CLI**；上面的脚本仅为一次性引导与外部探针保留。

```bash
cd backend
poetry run python -m app.cli --help
```

当前注册的子命令：

| 命令                    | 用途                                            |
|-------------------------|------------------------------------------------|
| `version`               | 打印 `APP_NAME` 与 `APP_VERSION`                |
| `skills`                | 技能 CRUD / 列表 / 重新索引                      |
| `categories`            | 分类管理                                         |
| `tags`                  | 标签管理                                         |
| `search`                | 对 Qdrant 的一次性语义搜索                        |
| `import` / `export`     | 技能包导入导出                                    |
| `index`                 | 重建 / 检查 Qdrant 索引                           |
| `cache`                 | 刷新 / 检查 Redis 缓存                            |

## `make` 命令

最常用的工作流也以 Make 目标的形式暴露。运行 `make help` 查看完整列表。

```bash
make help               # 列出所有目标
make dev                # 启动整套栈
make test               # 运行所有测试
make db-upgrade         # 应用迁移
make db-revision msg=…  # 创建新迁移
make secrets-scan       # 扫硬编码凭据
make i18n-compile       # 编译后端 .po → .mo
make i18n-check         # 校验 i18n 键完整
```

## 下一步

- [Makefile](https://github.com/badhope/AI-SKILL/blob/main/Makefile) —— 完整的目标列表
- [备份与恢复](../operations/backup.md)
