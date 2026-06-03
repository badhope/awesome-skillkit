感谢你有意为 AI-SKILL 贡献！本文档阐述了参与本项目的流程与约定。

## 行为准则

本项目遵循 [Contributor Covenant 行为准则](code-of-conduct.md)。参与即代表你承诺维护该准则。请向项目维护者举报任何不可接受的行为。

---

## 如何贡献

### 报告 Bug

1. 在[已有 issue](https://github.com/badhope/AI-SKILL/issues) 中搜索，避免重复
2. 提新 issue 时使用 **Bug Report** 模板
3. 请附上：
   - 清晰、具描述性的标题
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息（操作系统、浏览器、Python 版本、Node 版本）
   - 截图或错误日志（如有）

### 提出功能建议

1. 查阅已有 issue 与 discussion，确认没有重复建议
2. 使用 **Feature Request** 模板
3. 描述功能、使用场景与潜在实现路径
4. 保持开放，乐于接受反馈与迭代

### 提交 Pull Request

1. **Fork** 仓库
2. 按 [分支命名约定](#branch-naming) **创建** 分支
3. 遵循 [代码风格指南](#code-style) **修改**
4. **编写/更新** 你的修改对应的测试
5. 跑通 **完整测试套件** 与 lint
6. 使用 [Conventional Commits](#commit-message-conventions) **提交**
7. **推送** 分支到你的 fork
8. 针对 `main` 分支 **发起** Pull Request

---

## 开发流程

### 准备

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker 与 Docker Compose（推荐）
- Poetry（Python 依赖管理）

### 环境搭建

```bash
# 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/AI-SKILL.git
cd AI-SKILL

# 启动基础设施服务
docker-compose up -d postgres redis qdrant

# 后端环境
cd backend
poetry install
poetry run alembic upgrade head

# 前端环境
cd ../frontend
npm install
```

### 开发模式运行

```bash
# 终端 1：后端
cd backend
poetry run uvicorn app.main:app --reload

# 终端 2：前端
cd frontend
npm run dev
```

### 运行测试

```bash
# 后端测试
cd backend
poetry run pytest

# 附带覆盖率
poetry run pytest --cov=app --cov-report=term-missing

# 前端检查（lint / typecheck）
cd frontend
npm run lint
npm run typecheck
```

### 代码质量检查

```bash
# 后端
cd backend
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app/

# 前端
cd frontend
npm run lint
npm run typecheck
```

---

## 提交信息约定 {#commit-message-conventions}

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[可选 body]

[可选 footer]
```

### 类型

| Type | 含义 |
|------|-------------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档变更 |
| `style` | 代码风格/格式化（无逻辑改动） |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 添加或修改测试 |
| `chore` | 维护性任务，依赖更新 |
| `ci` | CI/CD 配置变更 |
| `build` | 构建系统变更 |

### Scope

常用 scope：`api`、`frontend`、`sdk`、`search`、`auth`、`db`、`docker`、`docs`、`deps`

### 示例

```
feat(search): add hybrid BM25 + vector search
fix(auth): handle expired JWT tokens gracefully
docs(api): document skills search endpoint
test(search): add integration tests for semantic search
chore(deps): update fastapi to 0.115.0
```

---

## 分支命名 {#branch-naming}

| 前缀 | 用途 |
|--------|---------|
| `feat/` | 新功能 |
| `fix/` | 修复 |
| `docs/` | 文档变更 |
| `refactor/` | 重构 |
| `perf/` | 性能优化 |
| `test/` | 测试增改 |
| `chore/` | 维护任务 |

示例：`feat/semantic-search`、`fix/skill-slug-encoding`、`docs/api-reference`

---

## 代码风格 {#code-style}

### Python（后端与 SDK）

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 与 120 字符行宽上限
- 所有函数签名加类型注解
- 用 `ruff format` 格式化
- 用 `ruff check` 做 lint
- 用 `mypy` 做类型检查
- I/O 密集型操作使用 `async/await`
- 用 Pydantic 模型作为请求/响应 schema
- import 排序：标准库 → 第三方 → 本地

### TypeScript / React（前端与 TS SDK）

- 沿用代码库中既有的 Next.js 与 React 模式
- 使用函数组件 + hooks
- 启用 TypeScript strict mode
- 用 `clsx` + `tailwind-merge` 处理条件 class
- 用 Zod 做运行时校验
- 优先命名导出而非默认导出
- 站内导航用 `next/link`
- 用 ESLint 格式化（`eslint-config-next`）

### 通用

- 写自解释的代码；注释只用于复杂逻辑
- 保持单文件聚焦、控制在约 400 行以内
- 沿用代码库中的既有模式
- 代码中不加 emoji，提交信息中可加

---

## 测试要求

- **新功能** 必须包含单元测试
- **API 端点** 必须包含集成测试
- **Bug 修复** 应包含回归测试
- 目标新增代码 **80%+ 测试覆盖率**
- 后端测试：`pytest` + `pytest-asyncio`
- 前端测试（已有）：Jest + React Testing Library

---

## 文档要求

- 新增/修改功能时同步更新相关文档
- API 端点必须有完整 docstring
- 新 SDK 方法必须包含使用示例
- 重大变更应记入 `CHANGELOG.md`
- README 应反映项目当前状态

---

## 翻译贡献 {#i18n-contributing}

我们也欢迎把文档、界面、错误信息翻译成新语言。`docs/zh/` 是简体中文翻译的起步；如要添加其他语言，请：

1. 复制 `docs/zh/` 树为 `docs/<locale>/`。
2. 翻译文件内容，**保留**所有英文代码块、命令、URL、徽章链接、文件名、品牌名。
3. 在 `docs/mkdocs.yml` 的 `plugins.i18n.languages` 里追加新 locale。
4. 提交 PR，标题形如 `docs(<locale>): translate <page>`。

术语约定参见 [贡献指南 → 翻译贡献 → 术语约定](#i18n-contributing) 维护的中英术语表。

---

## Pull Request 流程

1. 跑通所有测试与 lint
2. 按需更新文档
3. 在 `CHANGELOG.md` 的 `[Unreleased]` 节下加一条
4. PR 需至少一位维护者审查并通过
5. 推荐 squash merge，保持主干历史整洁

### PR 标题格式

与 commit 格式相同：

```
feat(search): implement hybrid search with BM25 ranking
```

---

## 寻求帮助

- **问题？** 开 [Discussion](https://github.com/badhope/AI-SKILL/discussions)
- **Bug？** 开 [Issue](https://github.com/badhope/AI-SKILL/issues)
- **聊天？** 加入社区 Discord（链接稍后）

---

感谢你为 AI-SKILL 做贡献！
