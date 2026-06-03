# 可观测性

AI-SKILL 以可对接任意 OpenTelemetry 兼容后端的方式，输出
日志、指标与追踪。

## 日志

通过 [`structlog`](https://www.structlog.org/) 输出结构化 JSON。
每一行日志都具备相同形态：

```json
{
  "event": "skill.created",
  "level": "info",
  "timestamp": "2026-06-01T12:00:00.000Z",
  "logger": "app.services.skill",
  "skill_id": "f3a4…",
  "user_id": "8d2e…"
}
```

常用环境变量：

| 变量          | 默认值  | 说明                                       |
|---------------|---------|--------------------------------------------|
| `LOG_LEVEL`   | `INFO`  | `DEBUG` / `INFO` / `WARNING` / `ERROR`    |
| `LOG_FORMAT`  | `json`  | 生产用 `json`，开发用 `console`            |

### 本地查看

```bash
make logs                              # 所有服务
docker compose logs -f backend         # 仅后端
docker compose logs --since=1h backend # 最近一小时
```

### 采集至集中存储

让日志采集器（Fluent Bit、Vector、Promtail）指向 docker socket
即可。每行都是一个 JSON 文档，无需解析。

Fluent Bit 输入示例：

```ini
[INPUT]
    Name              tail
    Path              /var/lib/docker/containers/*/*.log
    Parser            docker
    Tag               docker.*
[FILTER]
    Name              parser
    Match             docker.*
    Key_Name          log
    Parser            json
```

## 指标

通过 OTLP 导出 OpenTelemetry。设置标准 OTel 环境变量即可：

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer%20<token>
OTEL_SERVICE_NAME=skill-backend
```

后端会自动埋点以下内容：

- FastAPI 请求处理器（耗时、状态码、路由）
- SQLAlchemy 查询（耗时、SQL、影响行数）
- Redis 调用（耗时、命令）
- Qdrant 调用（耗时、集合、top-k）

前端不会自动埋点；如需真实用户监控（RUM），请添加一个
OTel 兼容的浏览器 SDK，并采集到同一个 collector。

### 推荐仪表盘

- **按路由的请求量** —— 5xx 比率、p50/p95/p99 延时
- **数据库** —— 活跃连接、慢查询、dead tuples
- **向量搜索** —— Qdrant 查询延时、recall@10（通过离线任务周期计算）
- **业务** —— 每日新建技能数、搜索点击比

## 追踪

同一份 OTLP 导出器也会承载追踪。每个请求都会获得一个 trace，
其下展开成对 DB、Redis、Qdrant 调用的 span。当引入 worker
（Celery）时，分布式追踪会很有用 —— 它的任务会变成源请求的
子 span。

## 错误

Sentry 是可选的，但生产环境推荐。设置 `SENTRY_DSN` 后，后端会：

- 捕获未处理异常，并附带请求上下文
- 按可配置比例采样事务（默认 10%）

```bash
SENTRY_DSN=https://…@o0.ingest.sentry.io/0
SENTRY_TRACES_SAMPLE_RATE=0.1   # 10% 的事务
SENTRY_PROFILES_SAMPLE_RATE=0.1 # 10% 的 profile
```

## 健康检查端点

| 端点             | 检查内容                                                                  |
|------------------|---------------------------------------------------------------------------|
| `GET /health`    | 应用存活（只要进程在就返回 200，body 为 `{status, app_name, version}`）   |
| `GET /`          | 与 `/health` 相同的 JSON，并附加 `api_prefix` 与 `docs` 链接             |

深度就绪检查（Alembic head、Qdrant 集合等）目前**尚未**通过 HTTP
暴露。它们由
[`scripts/health_check.py`](https://github.com/badhope/AI-SKILL/blob/main/scripts/health_check.py)
针对运行中的后端执行：

```bash
make health-check          # 等价于: poetry run python scripts/health_check.py
```

将 `/health` 同时接入负载均衡器的 liveness 与 readiness 探针。
`/health` 失败时，pod 会从负载均衡中摘除并重启。

## 接下来去哪里

- [配置](../getting-started/configuration.md) —— 日志与 OTel 环境变量
- [部署](../deployment.md) —— 生产环境拓扑
- [故障排查](../troubleshooting.md) —— 读日志的常用套路
