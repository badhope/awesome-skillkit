# ADR 009 — OWASP 安全头中间件

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

FastAPI 默认不设置 HTTP 安全头。OWASP Secure Headers 项目推荐的基线包括
HSTS、`X-Content-Type-Options`、`X-Frame-Options`、`Referrer-Policy`、
`Permissions-Policy`、严格的 `Content-Security-Policy`，以及
`Cross-Origin-*` 隔离头。

## 决策

添加一个 `SecurityHeadersMiddleware`，对每个响应附加 OWASP 基线头，
剥离 `X-Powered-By`，并规范化 `Server` 头。仅在 `DEBUG=false` 时附加 HSTS。

## 后果

- 单文件约 50 行，零运行时开销。
- 该中间件位于错误处理器与限流器之间，因此错误响应也带上了安全头。
- 未来加入 CSP nonce（用于未来的 SSR 界面）有明确的归属位置。
