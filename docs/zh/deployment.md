# AI-SKILL — 部署指南

本指南带你从 `git clone` 走到生产 URL。请按你的场景选择对应路径：

1. [本地开发](#local-dev-docker-compose)
2. [手动 / 裸金属](#bare-metal)
3. [单 VPS 生产](#single-vps-nginx)
4. [托管 / 云](#managed-cloud)
5. [升级与回滚](#upgrade-rollback)
6. [备份](#backup)
7. [加固清单](#hardening)

---

## 1. 本地开发（Docker Compose） {#local-dev-docker-compose}

这是跑整套栈最快的方式。假设已安装 Docker Engine 24+ 与 Compose v2。

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

# 1. 复制并编辑环境文件
cp .env.example .env
# 生成三个必需密钥
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env

# 2. 构建并启动
docker compose up -d --build

# 3. 跟踪日志
docker compose logs -f

# 4. 打开应用
open http://localhost:3000
```

默认端口：

| 服务    | 端口  | URL                         |
|------------|-------|-----------------------------|
| 前端   | 3000  | <http://localhost:3000>     |
| 后端    | 8000  | <http://localhost:8000>     |
| Swagger UI | 8000  | <http://localhost:8000/docs>|
| ReDoc      | 8000  | <http://localhost:8000/redoc> |
| Postgres   | 5432  | `localhost:5432`            |
| Redis      | 6379  | `localhost:6379`            |
| Qdrant     | 6333  | <http://localhost:6333/dashboard> |

后端首次启动时会运行 Alembic 迁移并注入初始分类。用以下命令创建第一个超级用户：

```bash
docker compose exec backend python -m app.scripts.create_admin
```

然后重启后端让新管理员能登录：

```bash
docker compose restart backend
```

---

## 2. 手动安装（裸金属） {#bare-metal}

当你无法运行 Docker 时使用此方式（例如受限环境）。

### 2.1 准备

| 工具         | 版本    |
|--------------|------------|
| Python       | 3.12+      |
| Poetry       | 1.8+       |
| Node.js      | 20+        |
| PostgreSQL   | 16+        |
| Redis        | 7+         |
| Qdrant       | 1.9+       |
| Caddy / Nginx| latest     |

### 2.2 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入真实值
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2.3 前端

```bash
cd frontend
# 暴露到浏览器的环境变量必须以 NEXT_PUBLIC_ 开头。
# 前端把 /api/* 反向代理到 ${NEXT_PUBLIC_API_URL}/api/*（见
# frontend/next.config.ts），所以这里的值是后端根地址（不带 /api/v1 后缀）。
cp .env.example ../.env.local  # 或手动创建 .env.local
echo 'NEXT_PUBLIC_API_URL="http://localhost:8000"' >> .env.local
echo 'NEXT_PUBLIC_APP_NAME="AI-SKILL"'                >> .env.local
npm install
npm run build
npm start
```

---

## 3. 单 VPS 生产（Nginx 反向代理） {#single-vps-nginx}

这是最小可用的"真正"生产方案：一份 $5/月的 VPS，把整套栈放在带自动 TLS 的反向代理后面。

### 3.1 初始化主机

```bash
# 推荐 Ubuntu 22.04+
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin ufw
sudo usermod -aG docker $USER
# 注销后重新登录
```

开启防火墙：

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3.2 克隆与配置

```bash
sudo mkdir -p /opt/skill-system && sudo chown $USER:$USER /opt/skill-system
cd /opt/skill-system
git clone https://github.com/badhope/AI-SKILL.git .
cp .env.example .env
$EDITOR .env   # 见下方"生成密钥"
```

### 3.3 生成密钥

```bash
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env
```

### 3.4 用 Nginx 顶在最前面

`/etc/nginx/sites-available/skill-system`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### 3.5 用 Caddy 自动 TLS（替代方案）

如果你想免运维 TLS，把 Nginx 换成 Caddy：

```caddy
your-domain.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /*    frontend:3000
}
```

### 3.6 启动整套栈

```bash
docker compose up -d
docker compose exec backend python -m app.scripts.create_admin
```

### 3.7 验证

```bash
curl -fI https://your-domain.com/health
```

---

## 4. 托管云部署 {#managed-cloud}

### 4.1 Vercel（前端）

```bash
cd frontend
vercel link
vercel env add NEXT_PUBLIC_API_URL production
# 粘贴：https://api.your-domain.com（不带 /api/v1 后缀 —— Next.js
# 会自动把 /api/* 重写到 ${NEXT_PUBLIC_API_URL}/api/*）
vercel --prod
```

### 4.2 Fly.io（后端）

```bash
cd backend
fly launch --no-deploy
fly secrets set \
  JWT_SECRET_KEY=$(openssl rand -hex 32) \
  ADMIN_PASSWORD=$(openssl rand -base64 18) \
  DATABASE_URL=postgres://... \
  REDIS_URL=redis://... \
  QDRANT_URL=https://...
fly deploy
```

### 4.3 Render

使用 `render.yaml` 蓝图：

```yaml
services:
  - type: web
    name: skill-backend
    env: docker
    rootDir: backend
    envVars:
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ADMIN_PASSWORD
        generateValue: true
```

### 4.4 参考架构（AWS / GCP / Azure）

```
                    ┌─────────────────────┐
                    │  CloudFront / CDN   │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
   │  前端    │         │   后端      │        │  异步 worker │
   │  (S3 /   │         │  (ECS /     │        │  (ECS /     │
   │ CloudFront)        │  Cloud Run) │        │  Cloud Run) │
   └──────────┘         └──────┬──────┘        └──────┬──────┘
                               │                      │
        ┌──────────────────────┼──────────────────────┤
        │                      │                      │
   ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
   │ Postgres │         │   Redis     │        │   Qdrant    │
   │ (RDS)    │         │ (ElastiCache)        │  (managed)  │
   └──────────┘         └─────────────┘        └─────────────┘
```

---

## 5. 升级与回滚 {#upgrade-rollback}

### 5.1 例行升级

```bash
cd /opt/skill-system
git pull --ff-only
docker compose pull
docker compose up -d --remove-orphans
docker compose exec backend poetry run alembic upgrade head
# 在主机上探测新版本（scripts/health_check.py 位于仓库根，不在 backend 容器内）
make health-check
```

### 5.2 回滚到上一版本

```bash
git log --oneline -n 5   # 找到上一个正常 commit
git checkout <good-sha>
docker compose up -d --build
docker compose exec backend poetry run alembic downgrade -1
```

### 5.3 仅回滚数据库

```bash
docker compose exec backend poetry run alembic downgrade -1
```

> ⚠️ 某些迁移是破坏性的。生产环境回滚前务必先做数据库快照。

---

## 6. 备份 {#backup}

### 6.1 Postgres

```bash
# 快照
docker compose exec -T postgres pg_dump -U skill_user skill_db | \
    gzip > "backup-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"

# 恢复
gunzip -c backup-20260601T000000Z.sql.gz | \
    docker compose exec -T postgres psql -U skill_user skill_db
```

用 cron 自动化。备份脚本本身有意**不入库**（各运维的备份目标、保留窗口、
S3 bucket 各不相同），最小化示例如下：

```bash
# /etc/cron.d/skill-system-backup
0 3 * * * cd /opt/skill-system && \
  /opt/skill-system/scripts/backup.sh >> /var/log/skill-backup.log 2>&1
```

参考性的 `scripts/backup.sh` 放在运维 runbook 中（不在本仓库），通常把上面的
`pg_dump` 和 `qdrant snapshots` 调用包起来，加上轮转与 S3 同步。

### 6.2 Qdrant

Qdrant 自带 snapshot API：

```bash
curl -X POST 'http://localhost:6333/collections/skills/snapshots'
# 快照出现在 qdrant 容器的 /qdrant/snapshots 目录
```

### 6.3 对象存储

如果使用 S3，请开启桶版本管理与生命周期策略。你的备份脚本（见 §6.1）
也应当把 `*.sql.gz` 与 Qdrant 快照通过 `aws s3 sync` 同步到带版本控制的桶。

---

## 7. 生产加固清单 {#hardening}

把这份清单走完，再向公网开放。

- [ ] `.env` 中所有环境变量已设置；生产环境**没有默认值**
- [ ] `JWT_SECRET_KEY` 长度 ≥ 32 字符且**不在**弱值黑名单中
- [ ] `ADMIN_PASSWORD` 长度 ≥ 12 字符，且唯一
- [ ] `POSTGRES_PASSWORD` 强且不是示例值
- [ ] TLS 已配置；观察到 HSTS 响应头（`curl -I https://…`）
- [ ] `BACKEND_CORS_ORIGINS` 只列出真实的前端来源
- [ ] 数据库**没有**对公网开放
- [ ] Qdrant **没有**对公网开放
- [ ] Redis **没有**对公网开放
- [ ] `DEBUG=false`
- [ ] 已配置 Sentry DSN
- [ ] 备份在跑且经过恢复演练
- [ ] 本机已安装 `pre-commit`；CI 绿灯
- [ ] `main` 分支已开启分支保护（需 PR + 至少 1 名 reviewer + CI 绿）
- [ ] 已开启 Dependabot alerts
- [ ] `git log --oneline` 中无硬编码密钥

完整策略与漏洞披露流程请见 [安全策略](operations/security.md)。
