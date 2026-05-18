---
applyTo: ['**/*.py', '**/*.ts', '**/*.tsx']
description: "Error handling patterns for Python backend and TypeScript frontend: exception hierarchy, HTTP contract, logging strategy. Applied to Python and TypeScript files."
---

# Error Handling Patterns

Rules: validate at entry points, catch only known exceptions, log once, never expose internal details in responses.

## Python Backend

### Custom Exception Hierarchy (`app/exceptions.py`)
```python
class AppError(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} '{identifier}' not found", "NOT_FOUND")

class AuthorizationError(AppError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN")

# NOTE: If Pydantic is in scope, name this DomainValidationError to avoid conflicts
class DomainValidationError(AppError):
    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")
```

### Centralized FastAPI Exception Handler (`app/error_handlers.py`)
```python
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_map = {"NOT_FOUND": 404, "VALIDATION_ERROR": 422, "FORBIDDEN": 403, "CONFLICT": 409}
    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={"error": {"code": exc.code, "message": exc.message}},
    )

# Register in main.py:
app.add_exception_handler(AppError, app_error_handler)
```

### Service Layer Rule
Services raise domain exceptions, never HTTP exceptions directly.

```python
class ReportService:
    async def get(self, report_id: str) -> Report:
        report = await self.repository.find(report_id)
        if not report:
            raise NotFoundError("Report", report_id)
        return report

    async def publish(self, report_id: str, user: User) -> Report:
        report = await self.get(report_id)
        if report.company_id != user.company_id:
            raise AuthorizationError("Cannot publish reports from other companies")
        if report.status != "draft":
            raise DomainValidationError(f"Cannot publish report in '{report.status}' status")
        report.status = "published"
        return await self.repository.save(report)
```

### Logging Pattern
```python
logger = logging.getLogger(__name__)

async def process_file(file_path: str) -> ProcessResult:
    logger.info("Processing file", extra={"file_path": file_path})
    try:
        result = transform(await read_file(file_path))
        logger.info("File processed", extra={"file_path": file_path, "records": len(result)})
        return result
    except FileNotFoundError:
        logger.warning("File not found", extra={"file_path": file_path})
        raise NotFoundError("File", file_path)
    except Exception:
        logger.exception("Unexpected error processing file", extra={"file_path": file_path})
        raise
```

---

## TypeScript Frontend

### HTTP Error Interceptor (Angular)
```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          inject(AuthService).logout();
          inject(Router).navigate(['/login']);
          break;
        case 403:
          inject(NotificationService).error('You do not have permission for this action.');
          break;
        case 0:
          inject(NotificationService).error('Network connection lost.');
          break;
      }
      return throwError(() => error);
    }),
  );
};
```

### Component Error State (Angular Signals)
```typescript
// Define LoadState<T> in core/models/load-state.ts
type LoadState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string };

protected state = signal<LoadState<Report[]>>({ status: 'idle' });

loadReports(): void {
  this.state.set({ status: 'loading' });
  this.reportService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
    next: (data) => this.state.set({ status: 'success', data }),
    error: (err) => this.state.set({
      status: 'error',
      message: err.error?.error?.message ?? 'An unexpected error occurred',
    }),
  });
}
```

---

## API Error Response Contract

All errors return this shape:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [{ "field": "email", "issue": "Invalid email format" }]
  }
}
```

| HTTP Status | Code | When |
|-------------|------|------|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing/invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Duplicate or version conflict |
| 422 | VALIDATION_ERROR | Semantically invalid input |
| 500 | INTERNAL_ERROR | Unexpected server error (never expose details) |
