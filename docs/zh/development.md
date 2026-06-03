# AI-SKILL — 开发指南

本页面向希望扩展 AI-SKILL 的贡献者。内容涵盖本地工作流、约定，
以及在发起 Pull Request 之前如何测试你的改动。

如果你是新加入项目，请一并阅读
[贡献指南](community/contributing.md) 与
[架构文档](architecture.md)。

---

## 1. 本地环境搭建

```bash
git clone https://github.com/badhope/AI-SKILL.git
cd AI-SKILL

# 一键引导（安装依赖、生成密钥、安装钩子）
make first-run

# 启动整套服务
make dev
```

校验：

```bash
curl -sf http://localhost:8000/health
open http://localhost:3000
```

---

## 2. 项目结构

```
AI-SKILL/
├── backend/              FastAPI 后端
├── frontend/             Next.js 15 PWA
├── sdk/
│   ├── python/           Python 客户端
│   └── typescript/       TypeScript 客户端
├── docs/                 架构、部署、故障排查
├── examples/             API + SDK 用法示例
├── scripts/              运维脚本
├── .github/              Issue 模板、PR 模板、CI、CODEOWNERS
└── Makefile              常用命令
```

---

## 3. 约定

### 3.1 提交信息

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

| 类型        | 适用场景                                               |
|-------------|--------------------------------------------------------|
| `feat`      | 新功能                                                 |
| `fix`       | Bug 修复                                               |
| `docs`      | 仅文档                                                 |
| `refactor`  | 不改变行为                                             |
| `perf`      | 性能优化                                               |
| `test`      | 新增或修复测试                                         |
| `build`     | 构建系统、CI、依赖                                     |
| `chore`     | 工具或配置变更，不涉及产品代码                          |
| `security`  | 漏洞修复或安全加固                                     |

示例：

```
feat(skills): add PATCH /skills/{slug}/metadata endpoint

* 将两次 PUT 合并为一次 PATCH，便于增量元数据更新
* 向后兼容 —— 既有 PUT 路径仍然有效
* 在 tests/integration/test_skills_api.py 中补充了集成测试

Closes #142
```

### 3.2 分支命名

`<type>/<short-kebab-case-description>`

示例：
- `feat/composition-graph`
- `fix/auth-refresh-loop`
- `docs/add-architecture-diagram`

### 3.3 Python 风格

- **格式化器**：`ruff format`（100 列）
- **Linter**：`ruff check`（规则集：E、F、I、B、UP、N、SIM、C4、RET、TCH）
- **类型检查器**：`mypy`，使用 `--ignore-missing-imports`

提交前：

```bash
cd backend
poetry run ruff format app/ tests/
poetry run ruff check --fix app/ tests/
poetry run mypy app/ --ignore-missing-imports
poetry run pytest
```

### 3.4 TypeScript 风格

- **格式化器**：`prettier`（100 列、单引号、尾随逗号）
- **Linter**：`eslint`，使用 `eslint-config-next`
- **类型检查器**：`tsc --noEmit`

提交前：

```bash
cd frontend
npm run lint
npm run typecheck
npm test
```

---

## 4. 新增一个 API 端点

下面给出一个完整示例。假设我们要新增
`GET /api/v1/skills/{slug}/history`。

1. **Schema** —— 在
   `backend/app/schemas/skill.py` 中新增 Pydantic 响应模型：

   ```python
   class SkillHistoryEntry(BaseModel):
       version: str
       changelog: str
       created_at: datetime
   ```

2. **Service** —— 在
   `backend/app/services/skill_history.py` 中实现数据访问：

   ```python
   async def get_history(db: AsyncSession, slug: str) -> list[SkillHistoryEntry]:
       ...
   ```

3. **Router** —— 在
   `backend/app/api/v1/skills.py` 中挂载端点：

   ```python
   @router.get("/{slug}/history", response_model=list[SkillHistoryEntry])
   async def get_skill_history(slug: str, db: AsyncSession = Depends(get_db)):
       return await get_history(db, slug)
   ```

4. **Test** —— 在 `tests/unit/` 写单元测试，在
   `tests/integration/` 写集成测试。

5. **Docs** —— OpenAPI Schema 由代码自动生成。记得把
   新端点加入 README 的「API 总览」表格。

---

## 5. 新增一个前端页面

页面位于 `frontend/src/app/<route>/page.tsx`。App Router
采用文件式路由。

```tsx
// frontend/src/app/skills/[slug]/history/page.tsx
import { SkillHistoryList } from '@/components/SkillHistoryList';

export default function Page({ params }: { params: { slug: string } }) {
  return <SkillHistoryList slug={params.slug} />;
}
```

约定：

- 默认使用 Server Component，仅在必要时再标注 `'use client'`
- 客户端数据获取使用 TanStack Query
- 任何面向用户的字符串都通过 i18n hook 取值
- 在 `frontend/src/lib/i18n/translations.ts` 添加翻译键
- 在 `frontend/src/__tests__/` 补充测试

---

## 6. 新增一个 SDK 方法

1. **实现**：在 `sdk/<lang>/skill_sdk/` 中编写方法
2. **类型**：在 `types.py` / `types.ts` 中声明请求与响应
3. **测试**：在本地服务上验证（`make dev`）
4. **文档**：在 `sdk/<lang>/README.md` 中补充使用示例
5. **Bump 版本**：更新 `pyproject.toml` / `package.json`（新增用 patch，
   破坏性变更用 minor）

---

## 7. 数据库变更

所有变更都应通过 Alembic 完成。永远不要手工 `CREATE TABLE`。

```bash
# 修改模型后
cd backend
poetry run alembic revision --autogenerate -m "add skill_history table"
# 检查 alembic/versions/ 下生成的迁移
poetry run alembic upgrade head
poetry run alembic downgrade -1   # 冒烟测试 downgrade
```

对于纯增量变更（新增可空列、新表），自动生成的迁移通常足够。
对于破坏性变更（删列、改类型），请手写迁移并补充显式
`op.execute(...)` 数据回填。

---

## 8. 测试

### 8.1 后端

```bash
cd backend
poetry run pytest -x                # 遇错即停
poetry run pytest --cov=app          # 附带覆盖率
poetry run pytest tests/integration  # 仅集成测试
poetry run pytest tests/unit        # 仅单元测试
```

集成测试需要 Postgres 与 Redis，已在 `tests/conftest.py` 中
配置使用本地服务。

### 8.2 前端

```bash
cd frontend
npm test                  # 一次性执行
npm test -- --watch       # watch 模式
npm run test:coverage     # 附带覆盖率
```

### 8.3 SDK

```bash
# Python
cd sdk/python
poetry run pytest skill_sdk/

# TypeScript
cd sdk/typescript
npm test
```

### 8.4 手工冒烟测试

发起 PR 前，请依次确认：

1. `make dev` 正常启动
2. 前端无控制台报错
3. `POST /api/v1/auth/register` 返回 201
4. `POST /api/v1/auth/login` 返回令牌对
5. `GET /api/v1/skills` 返回种子数据
6. `GET /api/v1/skills/search?q=react` 返回相关结果
7. `GET /health` 返回 200（存活）
8. `make health-check` 报告 4/4 服务健康

---

## 9. Pull Request 检查清单

详见 [`.github/PULL_REQUEST_TEMPLATE.md`](https://github.com/badhope/AI-SKILL/blob/main/.github/PULL_REQUEST_TEMPLATE.md)。
简要版本：

- [ ] 测试已新增或更新
- [ ] Linter 干净（`make lint`）
- [ ] 类型检查器干净（`make typecheck`）
- [ ] 文档已更新（README、docs/、docstring）
- [ ] CHANGELOG 已更新（若有用户可见变更）
- [ ] 没有密钥，没有 `.env` 文件
- [ ] 至少一位审查者（CODEOWNERS 会自动指派）

---

## 10. 发布流程

1. 在 `backend/pyproject.toml`、`frontend/package.json`、
   `sdk/python/pyproject.toml` 和 `sdk/typescript/package.json`
   中更新版本号。
2. 更新 `CHANGELOG.md` —— 把 Unreleased 下的条目移到带日期的标题下。
3. 提交一个标题为 `chore(release): vX.Y.Z` 的 PR。
4. 合并后打 tag 并推送：

   ```bash
   git tag -s -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. `deploy.yml` 工作流会用该 tag 构建并发布 Docker 镜像。
6. 在 GitHub 上基于该 tag 创建 Release（工作流会辅助）。
