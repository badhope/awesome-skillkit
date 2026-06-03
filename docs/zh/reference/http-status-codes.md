# HTTP 状态码

API 遵循 [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) 的 HTTP 状态码约定。
下面列出我们做出的一些有意见的选择。

## 成功

| 状态码 | 何时使用 |
|------|------|
| 200  | `GET`、`PUT`、`PATCH`、`DELETE` 的标准成功 |
| 201  | 资源已创建（`POST` 返回新实体时） |
| 204  | 无 body（少见；我们倾向返回空对象） |

## 客户端错误

| 状态码 | 何时使用 |
|------|------|
| 400  | 请求格式错误（JSON 非法、缺少必填字段） |
| 401  | 缺少或无效的鉴权 |
| 403  | 已鉴权但不被允许（例如尝试编辑他人的技能） |
| 404  | 资源未找到 |
| 409  | 冲突（重复邮箱、重复 slug） |
| 422  | 请求格式合法但语义错误（例如非法枚举值） |
| 429  | 被限流 |

## 服务端错误

| 状态码 | 何时使用 |
|------|------|
| 500  | 未处理异常（是 bug；请上报） |
| 502  | 上游服务宕机（例如 API 访问不到 Qdrant） |
| 503  | 服务正在启动、迁移或维护中 |
| 504  | 上游超时 |

## 错误响应格式

错误来自哪里不同，响应的格式也不同：

**未捕获的异常（500）** —— 由 `ErrorHandlerMiddleware` 产生：

```json
{
  "detail": "An internal server error occurred.",
  "request_id": "f3a4…",
  "error_type": "ValueError"
}
```

| 字段          | 类型   | 备注 |
|--------------|--------|-------|
| `detail`     | `str`  | 人类可读消息 |
| `request_id` | `str`  | 请求的 UUID —— 上报 bug 时请附上 |
| `error_type` | `str`  | Python 异常类名（不带模块前缀） |

**已处理的错误（4xx，来自 FastAPI 的 `HTTPException`）** —— 标准
`{"detail": "..."}` body。`request_id` 总是在 `X-Request-ID` 响应头中返回，
便于把客户端反馈与服务端日志关联起来。

> 计划加入统一的 `error_code` 字段，但**尚未实现**。跟踪进度见 issue tracker。

## 校验错误（422）

Pydantic v2 的校验错误返回更丰富的格式：

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 12 characters",
      "input": "hunter2",
      "ctx": { "min_length": 12 }
    }
  ]
}
```

| 字段      | 备注 |
|--------|------|
| `type`   | Pydantic 错误类型（稳定） |
| `loc`    | 出错字段的路径 |
| `msg`    | 人类可读消息 |
| `input`  | 触发校验失败的值 |
| `ctx`    | 类型相关的上下文（最小长度、允许值等） |

## 分页

分页端点以 200 + `Page[T]` body 返回：

```json
{
  "items": [ … ],
  "total": 1234,
  "page": 1,
  "size": 20,
  "total_pages": 62
}
```

`total_pages` 按 `ceil(total / size)` 计算。请求越界页时返回 200 + 空 `items`
数组（不是 404）。

## 幂等性

`PUT` 与 `DELETE` 是幂等的。`POST` **通常不**幂等 —— 重试 `POST /skills`
会创建第二个具有新 id 的技能。显式 `Idempotency-Key` 头**计划中**但**尚未实现**；
暂不要依赖它。要让写操作可安全重试，请使用确定性的 `slug`（对 `skills` 是 UQ）
或检查第一次尝试的响应。

## 下一步

- [OpenAPI schema](https://badhope.github.io/AI-SKILL/api/v1/openapi.json) —— 完整契约（实时）
- [Swagger UI](http://localhost:8000/docs) —— 交互式演练场（仅当后端以 `DEBUG=true` 启动时可用）
- [示例](../examples/rest.md) —— 请求与响应样例
