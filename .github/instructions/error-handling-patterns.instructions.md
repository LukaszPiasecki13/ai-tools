---
name: error-handling-patterns
description: Error handling patterns for Python backend and TypeScript frontend - exception hierarchy, HTTP error contract, logging strategy. Framework-neutral; the exact response shape is a per-project decision. Auto-loaded for Python and TypeScript files.
applyTo: **/*.py,**/*.{ts,tsx,js,jsx}
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: rules/error-handling-patterns.md
     Regenerate: python scripts/sync_copilot.py -->

# Error Handling Patterns

Rules: validate at entry points, catch only known exceptions, log once, never expose internal details in responses.

**The exact class names and response shape are a project decision** — record it in a project ADR
and follow it. If the project already has an error contract, extend it; do not introduce a second
one. This rule fixes only the invariants below, plus a default for projects that have none.

## Invariants (every project)

1. **One base exception** for domain errors, carrying a human-readable message, a stable
   machine-readable `code`, and the HTTP status it maps to (directly or via a lookup).
2. **`code` on every domain error.** `UPPER_SNAKE`, naming the entity and condition
   (`DEVICE_NOT_FOUND`). The `code` is the contract with clients; the message is not — clients
   translate `code` and use the message only as a fallback.
3. **The message language is fixed per API** (one language, not a mix). Localisation is the
   client's job.
4. **Services raise domain exceptions, never `HTTPException`.** The API layer maps them. FastAPI
   dependencies count as API layer, but should still raise the domain exceptions, so the response
   carries `code` like every other error.
5. **Log once**, in the layer that catches. `logger.exception()` for unexpected errors.
6. **Never expose internals** (stack traces, SQL, paths) in a response.
7. **Validation errors follow the same envelope** as domain errors, with per-field detail in a
   dedicated array, not smuggled into the message field.

## Default contract (when the project has none)

Compatible with RFC 9457 (Problem Details, `application/problem+json`):

```json
{
  "type": "urn:<app>:error:device-not-found",
  "title": "Device not found",
  "status": 404,
  "detail": "Device 42 does not exist in this organization",
  "code": "DEVICE_NOT_FOUND",
  "errors": [{"field": "email", "issue": "..."}]
}
```

`detail` is always a string; `errors` appears only for validation failures; `code` is the
extension member clients switch on. A project that shipped `{"detail", "code"}` already uses the
core of this shape — migrate additively (add fields, migrate clients, then remove old behaviour).

| Status | Code (generic fallback) | When |
|--------|-------------------------|------|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing/invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Duplicate or version conflict |
| 422 | VALIDATION_ERROR | Semantically invalid input |
| 500 | INTERNAL_ERROR | Never expose internal details |

Prefer a specific code (`DEVICE_NOT_FOUND`) over the generic fallback.

## Python Backend

### Exception hierarchy

Default names for a project without its own: `AppError(Exception)` base with `message`,
`code`, and status; subclasses `NotFoundError`, `AuthorizationError`, `ConflictError`,
`DomainValidationError`. Use `DomainValidationError`, not `ValidationError`, to avoid the
Pydantic clash. A dedicated subclass is worth it only when a caller must catch it by type;
otherwise raise the shared class with a specific `code`.

### FastAPI exception handler

- Register the base class once: `app.add_exception_handler(AppError, app_error_handler)`.
- Add a handler for Pydantic/request validation errors (invariant 7) and a catch-all that logs
  with `logger.exception()` and returns a fixed generic message.

### Logging

- Structured logging: `logger.info("...", extra={"key": value})`.
- 4xx at `info`, 5xx at `error`, unhandled at `exception`.

## TypeScript Frontend

Framework-neutral rules; framework specifics live in the `react-patterns` / `angular-patterns`
skills.

- Handle errors in one place (HTTP client interceptor or query client), not in every component.
- 401 → end the session and route to login; 403 → permission message; network error →
  connection message; everything else → surface to the component.
- Map `code` to a user-facing message in one table. Fall back to the server `detail` only when
  `code` is missing or unknown, then to a generic message.
