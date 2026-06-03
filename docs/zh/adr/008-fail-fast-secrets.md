# ADR 008 — 启动期密钥校验（fail-fast）

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

过去我们提供的 `.env.example` 含有占位值，例如
`JWT_SECRET_KEY=change-this-in-production`。运维人员经常直接复制该文件
并用占位值启动整套系统 —— 服务能起来，但整个认证层都可被轻易伪造。

## 决策

在生产模式下，如果以下任一变量缺失、过短或落在已知弱值黑名单中，
应用**拒绝启动**：

- `JWT_SECRET_KEY`（至少 32 字符）
- `ADMIN_PASSWORD`（供 seed 模块使用，至少 12 字符）
- `POSTGRES_PASSWORD`（供 docker-compose 使用；没有默认回退）

校验通过 `Settings` 类上的 `@model_validator` 实现。Compose 文件使用
`${VAR:?...}`，所以容器在启动期就会因变量缺失而失败。

## 后果

- 新的运维人员首次启动会撞上清晰的错误提示和 `openssl rand` 提示。
  这正是我们想要的"摩擦"。
- 测试通过 `DEBUG=true` 走宽松模式（随机临时 JWT 密钥），让测试集保持隔离。
- 提供一个 `secrets-scan` Make 目标，防止意外再次引入硬编码凭据。
