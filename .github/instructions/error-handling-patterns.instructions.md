---
applyTo: "**/*.py,**/*.ts,**/*.tsx"
description: "Error handling patterns for Python backend and TypeScript frontend: exception hierarchy, HTTP contract, logging strategy. Applied to Python and TypeScript files."
---

# Error Handling Patterns

Rules: validate at entry points, catch only known exceptions, log once, never expose internal details in responses.

## Python Backend

### Exception Hierarchy (`app/exceptions.py`)

- `AppError(Exception)` - base: `message: str`, `code: str = "INTERNAL_ERROR"`
- `NotFoundError(AppError)` - code: `NOT_FOUND`
- `AuthorizationError(AppError)` - code: `FORBIDDEN`
- `DomainValidationError(AppError)` - code: `VALIDATION_ERROR`, optional `field: str | None`
- **Note**: Use `DomainValidationError` (not `ValidationError`) to avoid conflict with Pydantic.

### FastAPI Exception Handler (`app/error_handlers.py`)

- Map codes to HTTP: `NOT_FOUND` → 404, `VALIDATION_ERROR` → 422, `FORBIDDEN` → 403, `CONFLICT` → 409, default → 500.
- Response shape: `{"error": {"code": "...", "message": "..."}}`.
- Register: `app.add_exception_handler(AppError, app_error_handler)`.

### Service Layer Rule

Services raise domain exceptions (`NotFoundError`, `AuthorizationError`, `DomainValidationError`) - never `HTTPException` directly. Router layer catches and maps.

### Logging

- Log at the layer where exception is caught. Log once, then re-raise or return.
- Use structured logging: `logger.info("...", extra={"key": value})`.
- `logger.exception()` for unexpected errors (includes stack trace automatically).

---

## TypeScript Frontend (Angular)

### HTTP Error Interceptor

- 401: call `AuthService.logout()` + navigate to `/login`
- 403: show permission denied notification
- 0 (network error): show connection error notification
- All others: `throwError(() => error)` - handled at component level

### Component Error State

Use `LoadState<T>` discriminated union: `idle | loading | success | error`. Store in `signal<LoadState<T>>()`. Extract error message from `err.error?.error?.message ?? 'An unexpected error occurred'`.

---

## API Error Response Contract

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [{"field": "email", "issue": "..."}] } }
```

| Status | Code | When |
|--------|------|------|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing/invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Duplicate or version conflict |
| 422 | VALIDATION_ERROR | Semantically invalid input |
| 500 | INTERNAL_ERROR | Never expose internal details |
