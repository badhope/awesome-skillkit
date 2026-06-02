# HTTP status codes

The API follows the [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
conventions for HTTP status codes. A few opinionated choices are
called out below.

## Success

| Code | When |
|------|------|
| 200  | Standard success for `GET`, `PUT`, `PATCH`, `DELETE` |
| 201  | Resource created (`POST` that returns the new entity) |
| 204  | No body (rare; we prefer to return the empty object) |

## Client errors

| Code | When |
|------|------|
| 400  | Malformed request (invalid JSON, missing required field) |
| 401  | Missing or invalid authentication |
| 403  | Authenticated but not allowed (e.g. trying to edit someone else's skill) |
| 404  | Resource not found |
| 409  | Conflict (duplicate email, duplicate slug) |
| 422  | Request is well-formed but semantically wrong (e.g. invalid enum value) |
| 429  | Rate-limited |

## Server errors

| Code | When |
|------|------|
| 500  | Unhandled exception (a bug; report it) |
| 502  | Upstream is down (e.g. Qdrant is unreachable from the API) |
| 503  | Service is starting up, migrating, or in maintenance |
| 504  | Upstream timed out |

## Error response shape

All error responses share the same shape:

```json
{
  "detail": "Skill not found: react-usememo-deep-dive",
  "error_code": "skill_not_found",
  "request_id": "f3a4…"
}
```

| Field        | Type   | Notes |
|--------------|--------|-------|
| `detail`     | `str`  | Human-readable message |
| `error_code` | `str`  | Machine-readable code (stable across releases) |
| `request_id` | `str`  | UUID of the request — quote it when reporting bugs |

## Validation errors (422)

Pydantic v2 validation errors return a richer shape:

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

| Field  | Notes |
|--------|-------|
| `type` | Pydantic error type (stable) |
| `loc`  | Path to the offending field |
| `msg`  | Human-readable message |
| `input`| The value that failed validation |
| `ctx`  | Type-specific context (min length, allowed values, etc.) |

## Pagination

Paginated endpoints return 200 with a `Page[T]` body:

```json
{
  "items": [ … ],
  "total": 1234,
  "page": 1,
  "size": 20,
  "total_pages": 62
}
```

`total_pages` is calculated as `ceil(total / size)`. A request for
a page that is out of range returns 200 with an empty `items`
array (not 404).

## Idempotency

`PUT` and `DELETE` are idempotent. `POST` is not, except for the
explicit `Idempotency-Key` header, which when present makes the
request safely retryable within a 24-hour window.

## Where to go from here

- [OpenAPI schema](https://github.com/badhope/AI-SKILL/blob/main/backend/app/api/openapi.py) — full contract
- [Swagger UI](http://localhost:8000/docs) — interactive playground
- [Examples](../examples/rest.md) — sample requests and responses
