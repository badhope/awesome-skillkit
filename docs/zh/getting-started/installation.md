# 安装

AI-SKILL 是一个可自托管的 monorepo。选择适合你场景的安装方式。

## 准备

| 工具         | 版本    | 用途                                      |
|--------------|------------|------------------------------------------|
| Python       | 3.12+      | 后端运行时                                 |
| Poetry       | 1.8+       | 后端依赖管理                               |
| Node.js      | 20+        | 前端与 TypeScript SDK 构建                |
| npm          | 10+        | 前端与 TypeScript SDK 安装                |
| Docker       | 24+        | 容器运行时                                 |
| Docker Compose | 2.x      | 多容器编排                                 |
| Git          | 2.40+      | 源码管理                                   |
| OpenSSL      | 1.1+       | 生成密钥                                   |

后端默认还会使用以下系统服务（默认通过 Docker Compose 提供）：

| 服务        | 版本 |
|------------|---------|
| PostgreSQL | 16      |
| Redis      | 7       |
| Qdrant     | 1.9+    |

## 通过 Docker 安装（推荐）

这是最快的路径。一条命令即可启动整个技术栈，既适合开发，也适合单 VPS 生产环境。

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

cp .env.example .env
echo "JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""      >> .env
echo "ADMIN_PASSWORD=\"$(openssl rand -base64 18)\""   >> .env
echo "POSTGRES_PASSWORD=\"$(openssl rand -base64 18)\"" >> .env

docker compose up -d --build

# 跟踪日志
docker compose logs -f
```

在浏览器中打开 <http://localhost:3000>。

## 不用 Docker 安装

当你无法运行 Docker 时使用此方式（例如严格受限的企业环境）。

### 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env —— 设置真实的 DATABASE_URL、JWT_SECRET_KEY、ADMIN_PASSWORD
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
# 暴露到浏览器的环境变量必须以 NEXT_PUBLIC_ 开头。
# 该值为后端根地址（不带 /api/v1 后缀），因为 next.config.ts 中的
# Next.js rewrite 会为你拼接 /api/*。
cp .env.example .env.local
echo 'NEXT_PUBLIC_API_URL="http://localhost:8000"' >> .env.local
echo 'NEXT_PUBLIC_APP_NAME="AI-SKILL"'                >> .env.local
npm install
npm run build
npm start
```

### 状态服务

你需要自行提供 PostgreSQL、Redis 与 Qdrant。简单的免费方案：

- **PostgreSQL** — `brew install postgresql@16`（macOS）/
  `apt install postgresql-16`（Ubuntu）
- **Redis** — `brew install redis` / `apt install redis`
- **Qdrant** — `docker run -p 6333:6333 qdrant/qdrant:v1.9.0`

## 验证安装

```bash
# 后端健康检查
curl -sf http://localhost:8000/health

# 前端能渲染
curl -sfI http://localhost:3000

# API 文档（仅当后端 DEBUG=true 时可用）
open http://localhost:8000/docs
```

## 创建第一个管理员

```bash
docker compose exec backend python -m app.scripts.create_admin
```

按提示输入。脚本结束后，使用刚创建的账号登录前端。

## 后续步骤

- [快速开始](quickstart.md) — 5 分钟创建你的第一个技能
- [配置](configuration.md) — 文档化所有环境变量（英文原版）
- [部署](../deployment.md) — 生产环境拓扑（英文原版）
