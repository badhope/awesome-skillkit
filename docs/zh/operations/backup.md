# 备份与恢复

生产部署的可靠性与备份方案直接挂钩。本节介绍三个有状态服务
以及最基本的恢复演练流程。

## 备份对象

| 服务                | 备份内容                            | 频率                  |
|---------------------|--------------------------------------|-----------------------|
| PostgreSQL          | 整库                                 | 每日                  |
| Qdrant              | `skills` 集合快照                    | 每周                  |
| Redis               | 仅缓存 —— 丢失不会致命              | 无需备份              |
| 对象存储（若用 S3） | Bucket 内容                          | 持续（开启版本管理）  |

## PostgreSQL

### 备份

```bash
docker compose exec -T postgres pg_dump \
    -U skill_user \
    -d skill_db \
    --no-owner \
    --no-privileges \
    | gzip > "backup-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
```

### 恢复

```bash
# 1. 停掉后端，避免恢复期间写入
docker compose stop backend worker beat

# 2. 重建数据库
gunzip -c backup-20260601T000000Z.sql.gz | \
    docker compose exec -T postgres psql -U skill_user -d skill_db

# 3. 重启所有服务
docker compose up -d
```

### 定时任务（示例）

```cron
# /etc/cron.d/skill-system-backup
0 3 * * * cd /opt/skill-system && \
  /usr/local/bin/backup-postgres.sh >> /var/log/skill-backup.log 2>&1
```

`backup-postgres.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/skill-system
KEEP=14
BACKUP_FILE="/var/backups/skill/postgres-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
docker compose exec -T postgres pg_dump -U skill_user skill_db \
  | gzip > "$BACKUP_FILE"
# 清理过期备份
find /var/backups/skill -name 'postgres-*.sql.gz' -mtime +$KEEP -delete
```

## Qdrant

Qdrant 内置了快照 API。

### 创建快照

```bash
curl -X POST 'http://localhost:6333/collections/skills/snapshots'
```

快照会写入容器的 `/qdrant/snapshots/` 目录。

### 拷出快照

```bash
docker cp skill-qdrant:/qdrant/snapshots ./qdrant-snapshots
```

### 恢复

```bash
# 1. 停后端
docker compose stop backend worker beat

# 2. 停 Qdrant
docker compose stop qdrant

# 3. 把快照拷回去
docker cp ./qdrant-snapshots/<snapshot-name> skill-qdrant:/qdrant/snapshots/

# 4. 启动 Qdrant 并触发恢复
docker compose start qdrant
curl -X PUT 'http://localhost:6333/collections/skills/snapshots/recover' \
  -H 'Content-Type: application/json' \
  -d "{\"location\": \"/qdrant/snapshots/<snapshot-name>\"}"

# 5. 启动其他服务
docker compose up -d
```

## Redis

丢失 Redis 不会致命 —— 应用会在下一次请求时重建缓存。
Redis 中只有：

- 会话黑名单（已登出 JWT）
- 限流计数器
- 通用缓存项

无需备份。

## 对象存储

如果使用 S3 或兼容服务：

- 启用 **Bucket 版本管理**，以便误删后可恢复
- 设置 **生命周期策略**，将 30 天以上的旧版本转入 Glacier
  或冷存储
- 将 bucket 复制到另一个区域

## 恢复演练

没有演练过的备份是不可信的。**每个季度**做一次恢复演练：

1. 拉起一台全新 VM（或使用预发环境）。
2. 恢复最新的 Postgres 快照。
3. 恢复最新的 Qdrant 快照。
4. 用恢复后的数据启动整套服务。
5. 运行 `make health-check`。
6. 抽查若干搜索查询。
7. 销毁演练环境。

记录耗时与结果。

## 接下来去哪里

- [部署](../deployment.md) —— 生产环境拓扑
- [故障排查](../troubleshooting.md) —— 恢复出错时该做什么
