# 测试

测试套件分为三层。每一层有不同的作用范围，并在 CI 流水线的不同
阶段运行。

## 第一层 —— 单元测试

纯函数，无 I/O。快速、隔离，在每个 PR 上运行。

```bash
cd backend && poetry run pytest tests/unit
cd frontend && npm test
cd sdk/python && poetry run pytest
cd sdk/typescript && npm test
```

**后端约定**：文件名 `test_<module>.py`，放在 `tests/unit/` 下。
`async def` 测试使用 `pytest-asyncio`。

**前端约定**：文件名 `<Component>.test.tsx`，与组件同目录。

**SDK 约定**：文件名 `test_<module>.py` / `.test.ts`，放在 SDK
自身的 `tests/` 目录。

## 第二层 —— 集成测试

通过真实服务验证系统片段。较慢，需要 Postgres + Redis + Qdrant。

```bash
cd backend && poetry run pytest tests/integration
```

**环境准备**：CI 工作流会启动 Postgres、Redis、Qdrant 作为服务
容器。本地你可以：

- 用 `docker compose up -d postgres redis qdrant` 启动服务后
  运行 `pytest tests/integration`
- 或使用 `tests/docker-compose.yml` 助手限定端口

**Fixture**：共享 fixture 放在 `tests/conftest.py`。它会为每个
测试通过 Alembic 创建一个干净的 schema、事务性 session 与
测试 client。

## 第三层 —— 端到端测试

验证整条链路。最慢，仅在 main 分支和发布 tag 上运行。

目前 E2E 套件是一组冒烟测试：

```bash
# CI 中：拉起整套服务、跑冒烟测试、拆除
make health-check
make test-e2e
```

## 覆盖率

按层生成覆盖率：

```bash
make test-coverage
```

输出：

- `backend/coverage.xml` —— Cobertura XML，上传 Codecov
- `frontend/coverage/` —— HTML 报告

覆盖率是**信号**，不是**目标**。CI 工作流会在 PR 中覆盖率下降
超过 1% 时让构建失败。

## 约定

### 后端

- 每个测试只测一个断言点
- `async def` 测试加 `pytest.mark.asyncio`
- 错误路径使用 `pytest.raises(ExpectedException)`
- 避免 `time.sleep`；时间穿越用 `freezegun`，HTTP mock 用
  `httpx.MockTransport`
- 模型构造使用工厂（`factory_boy`），不要手写字典

### 前端

- 使用 `@testing-library/react`（不要用 `enzyme`）
- 测试行为而非实现细节
- 用 `msw` mock 网络请求
- 每个测试只渲染一次
- 异步用 `findBy*`，同步用 `getBy*`

### SDK

- mock HTTP 传输（Python 用 `httpx.MockTransport`，TS 用 `msw`）
- 覆盖正常路径与每一个错误码

## 运行单个测试

```bash
# 后端
cd backend && poetry run pytest tests/unit/test_skill.py::test_create

# 前端
cd frontend && npm test -- SkillCard

# Python SDK
cd sdk/python && poetry run pytest skill_sdk/test_client.py

# TypeScript SDK
cd sdk/typescript && npm test -- SkillClient
```

## 接下来去哪里

- [新增一个 API 端点](adding-endpoint.md) —— 含示例测试
- [新增一个前端页面](adding-page.md) —— 含示例测试
- [发布流程](release.md) —— 发布前必须通过的测试
