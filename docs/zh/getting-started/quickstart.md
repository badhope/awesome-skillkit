# 快速开始

本页将带你在 5 分钟内从全新安装到在目录中成功创建一条技能。

## 1. 确认技术栈已运行

```bash
docker compose ps
# backend 与 frontend 都应处于 "running" 状态
```

如有任何服务未运行：

```bash
docker compose up -d
docker compose logs -f backend
```

## 2. 登录

在浏览器中打开 <http://localhost:3000>。点击 **登录** →
**注册** 创建一个账号。（如果你跳过了 [安装](installation.md) 的第 1 步，
也可以通过 `docker compose exec backend python -m app.scripts.create_admin`
引导出一个超级用户，然后使用该账号登录。）

## 3. 找到你的前端分类 slug

你即将创建的技能需要一个 `category_slug`。最简单的方式是通过 API 查询（按 `sort_order` 排序，返回扁平 JSON 数组）：

```bash
curl -s http://localhost:8000/api/v1/categories | jq
```

你会看到类似：

```json
[
  { "id": "8d2e…", "slug": "frontend", "name": "Frontend", … },
  { "id": "f3a4…", "slug": "backend",  "name": "Backend",  … },
  …
]
```

复制 **Frontend** 这一项的 `slug`。

## 4. 通过 API 创建一条技能

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"you","password":"hunter2"}' | jq -r .access_token)

curl -s -X POST http://localhost:8000/api/v1/skills \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "React useMemo deep-dive",
    "slug": "react-usememo-deep-dive",
    "description": "A practical guide to React useMemo with examples",
    "category_slug": "frontend",
    "tags": ["react", "performance"],
    "version": "1.0.0",
    "is_public": true,
    "content": {
      "summary": "useMemo lets you cache the result of an expensive calculation between renders…",
      "examples": []
    }
  }' | jq
```

返回 201 表示技能创建成功。平台会异步将其索引到 Qdrant 以提供语义搜索。

## 5. 在 UI 中查看

刷新 <http://localhost:3000>。你新建的技能应出现在 **Frontend** 分类页顶部，搜索 "useMemo" 时应排名靠前。

## 6. 语义搜索它

搜索端点为 `GET`，将查询作为 URL 参数（`q`）传入，按 score 排序返回扁平 JSON 数组：

```bash
curl -s "http://localhost:8000/api/v1/skills/search?q=cache+expensive+react&limit=5" | jq
```

即使你的技能文本里不包含字面词 "cache" 或 "expensive"，它也应位于顶部且分数很高。

## 下一步

- [示例](../examples/) — REST、Python、TypeScript SDK 配方
- [架构](../architecture.md) — 理解各组件
- [部署](../deployment.md) — 升级到生产环境
