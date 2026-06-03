# 数据库迁移

AI-SKILL 使用 [Alembic](https://alembic.sqlalchemy.org/) 进行 schema
迁移。所有 schema 变更 **必须** 通过迁移完成 —— 生产环境不要手工
执行 `CREATE TABLE`。

## 工作流

1. 修改 `backend/app/models/skill.py`（或同目录下其他模型）。
2. 自动生成迁移：
   ```bash
   cd backend
   poetry run alembic revision --autogenerate -m "add skill_versions table"
   ```
3. **检视** `backend/alembic/versions/` 中生成的文件。Alembic
   较为保守，列重命名、枚举值变更等场景它会漏报。
4. 在本地应用并测试：
   ```bash
   poetry run alembic upgrade head
   poetry run pytest
   poetry run alembic downgrade -1    # 冒烟测试 downgrade
   poetry run alembic upgrade head
   ```
5. 提交并推送。
6. CI 工作流会在全新数据库上执行 `alembic upgrade head`，以校验
   迁移可重复。

## 命名

迁移位于 `backend/alembic/versions/`，遵循如下模式：

```
<sequence>_<short_slug>_<description>.py
```

序号是全局递增的 —— `0001`、`0002`、`0003`，以此类推。

示例：

- `0001_initial.py`
- `0002_add_skill_versions.py`
- `0003_add_analytics_events.py`

自动生成的文件名通常符合规范，多数情况下无需重命名。

## autogenerate 能识别的变更

| 变更                                       | autogenerate？ |
|--------------------------------------------|----------------|
| 新增 / 删除列                              | 是             |
| 新增 / 删除表                              | 是             |
| 新增 / 删除索引                            | 是             |
| 修改列类型                                 | 有时           |
| 列重命名                                   | **否**（按 删+增 处理） |
| 表重命名                                   | **否**（按 删+增 处理） |
| 修改 `ForeignKey` 约束                     | 有时           |
| 新增 / 删除 check 约束                     | 是             |
| 新增 / 删除 `UniqueConstraint`             | 是             |
| 修改默认值                                 | 有时           |

若有疑问，**请手写迁移**。Alembic 只是 SQL 的薄包装，你可以把任何
SQLAlchemy DDL 放进 `op.execute()`。

## 危险迁移

### 删除列

Alembic 在 `upgrade` 时会直接 drop 列；`downgrade` 时数据已不可恢复。
对于破坏性变更：

1. 停掉后端。
2. 备份数据库。
3. 应用迁移。
4. 冒烟测试。
5. 保留备份至少 7 天再清理。

### 新增 NOT NULL 列（无默认值）

若表里已有数据，这一步会失败。可选方案：

- 先以 nullable 新增列，用脚本回填数据，再用一次迁移设为 NOT NULL
- 或新增列时使用服务端 `DEFAULT`

### 列重命名

Alembic 会把重命名视为 drop + add，**数据会丢失**。正确做法：

```python
def upgrade() -> None:
    op.alter_column("skills", "old_name", new_column_name="new_name")

def downgrade() -> None:
    op.alter_column("skills", "new_name", new_column_name="old_name")
```

### 新增 CHECK 约束

自动生成器会直接添加约束，不会校验既有数据。对于大表，请在
数据回填后用单独事务 `postgresql_using="VALIDATE CONSTRAINT"` 验证。

## 生产部署

迁移在启动时由后端（通过 FastAPI 的 `lifespan` 钩子）**自动应用**。
发布流水线：

1. 构建新的后端镜像。
2. 启动新容器。
3. 容器在 entrypoint 内执行 `alembic upgrade head`。
4. 待迁移完成后再启动 Gunicorn / uvicorn 进程。

若迁移失败，新容器退出，滚动更新暂停。旧版本仍在线提供服务。
请修复迁移并推送新镜像。

## 回滚迁移

应急场景下：

```bash
# 连接到正在运行的后端
docker compose exec backend poetry run alembic downgrade -1
```

这**不能**替代「向前修复」。回滚后，请新增一个迁移执行相反操作，
使 schema 与模型重新一致。

## 种子数据

迁移用于 **schema**，而不是数据。`app.core.seed` 模块会植入
分类、标签与首位管理员。该模块是**幂等**的 —— 每次启动都安全。

若测试需要植入特定夹具，请放在 `tests/conftest.py`，而不是
某个迁移中。

## 接下来去哪里

- [Schema 源码](https://github.com/badhope/AI-SKILL/blob/main/backend/app/models/skill.py)
- [种子模块](https://github.com/badhope/AI-SKILL/blob/main/backend/app/core/seed.py)
- [新增一个 API 端点](adding-endpoint.md) —— 通常与迁移一起出现
