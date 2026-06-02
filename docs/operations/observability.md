# Observability

AI-SKILL emits logs, metrics, and traces in a way that drops into
any OpenTelemetry-compatible backend.

## Logs

Structured JSON via [`structlog`](https://www.structlog.org/).
Every log line has the same shape:

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

Useful env knobs:

| Variable     | Default | Notes                                  |
|--------------|---------|----------------------------------------|
| `LOG_LEVEL`  | `INFO`  | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_FORMAT` | `json`  | `json` for production, `console` for dev |

### Local tailing

```bash
make logs                              # all services
docker compose logs -f backend         # backend only
docker compose logs --since=1h backend # last hour
```

### Shipping to a centralized store

Point your log shipper (Fluent Bit, Vector, Promtail) at the docker
socket. Each line is one JSON document; no parsing required.

Example Fluent Bit input:

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

## Metrics

OpenTelemetry is exported via OTLP. Set the standard OTel env vars:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer%20<token>
OTEL_SERVICE_NAME=skill-backend
```

The backend auto-instruments:

- FastAPI request handlers (latency, status code, route)
- SQLAlchemy queries (latency, statement, rows affected)
- Redis calls (latency, command)
- Qdrant calls (latency, collection, top-k)

The frontend is not auto-instrumented; if you need Real User
Monitoring, add an OTel-compatible browser SDK and ship to the
same collector.

### Suggested dashboards

- **Request rate by route** — 5xx rate, p50/p95/p99 latency
- **Database** — active connections, slow queries, dead tuples
- **Vector search** — Qdrant query latency, recall@10 (computed in
  a periodic offline job)
- **Business** — skills created per day, search-to-click ratio

## Traces

The same OTLP exporter carries traces. Each request gets a trace
that fans out into spans for DB, Redis, and Qdrant calls. Distributed
tracing is useful when you add a worker (Celery) — its tasks become
child spans of the originating request.

## Errors

Sentry is optional but recommended for production. Set
`SENTRY_DSN` and the backend will:

- Capture uncaught exceptions with the request context
- Sample a configurable percentage of transactions (default 10%)

```bash
SENTRY_DSN=https://…@o0.ingest.sentry.io/0
SENTRY_TRACES_SAMPLE_RATE=0.1   # 10% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.1 # 10% of profiles
```

## Health endpoints

| Endpoint             | What it checks                              |
|----------------------|---------------------------------------------|
| `GET /health`        | App is alive (always 200 if the process is up) |
| `GET /health/ready`  | Postgres + Redis + Qdrant are all reachable |
| `GET /health/live`   | Liveness probe (always 200)                 |

Wire `/health/ready` to your load balancer's readiness check and
`/health/live` to the liveness check. A failing `/health/ready`
removes the pod from rotation; a failing `/health/live` restarts it.

## Where to go from here

- [Configuration](../getting-started/configuration.md) — log and
  OTel env vars
- [Deployment](../deployment.md) — production topology
- [Troubleshooting](../troubleshooting.md) — common log-reading
  recipes
