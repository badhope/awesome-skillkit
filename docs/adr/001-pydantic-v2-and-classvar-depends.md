# ADR 001 — Pydantic v2 + ClassVar Depends

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

FastAPI dependency functions need to be invocable by the framework.
When we expose a dependency as a class attribute, FastAPI may try to
call the attribute itself (not the underlying function), which fails
with `TypeError: 'X' object is not callable`.

## Decision

1. **Use Pydantic v2** for all settings, schemas, and request/response
   models.
2. When a dependency function must be exposed as a class attribute
   (e.g. on a `PaginationParams` dataclass), declare it as a
   `ClassVar[Callable[..., T]]` so Pydantic does not try to treat it
   as a field.
3. Use the modern `Depends(get_pagination)` pattern instead of
   `Depends(PaginationParams)`.

```python
class PaginationParams:
    page: int = 1
    size: int = 20

    # ClassVar so pydantic-settings / pydantic v2 does not pick it up
    get_pagination: ClassVar[Callable[..., "PaginationParams"]] = None
```

## Consequences

- Pydantic v2 strict mode rejects invalid input early.
- `ClassVar` declarations avoid the "not callable" surprise.
- The pagination dependency stays a function — clearer to test and
  to mock.
