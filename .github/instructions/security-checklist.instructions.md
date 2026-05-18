---
applyTo: ['**/*.py', '**/*.ts', '**/*.tsx', '**/*.ps1']
description: "Security checklist: JWT auth, input validation, SQL injection, XSS, CSRF, rate limiting, secrets management. Applied to all code files."
---

# Security Checklist

OWASP Top 10. Apply to all code handling auth, user input, database access, or secrets.

## Authentication (JWT)

Use `PyJWT` (actively maintained). Do NOT use `python-jose` - unmaintained since 2022.

```python
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, PUBLIC_KEY, algorithms=["RS256"],
            audience="your-app", issuer="your-auth-server",
        )
        return TokenPayload(**payload)
    except ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {e}")
```

### Token Rules
- Access tokens: 15-30 min lifetime
- Refresh tokens: 7-30 days, rotate on use
- Store refresh tokens in `httpOnly`, `Secure`, `SameSite=Strict` cookies
- Never store tokens in `localStorage` (XSS risk)

---

## Input Validation

All validation at the system boundary (API routes). Never trust input from URL params, request bodies, or query strings.

```python
# Backend: Pydantic at API boundary
class UserInput(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100, pattern=r"^[\w\s\-]+$")
    role: Literal["viewer", "editor", "admin"]  # whitelist, not blacklist

# Validate UUIDs before DB queries
UUID_PATTERN = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
def validate_uuid(value: str) -> str:
    if not UUID_PATTERN.match(value):
        raise DomainValidationError("Invalid ID format")
    return value
```

```typescript
// Frontend: validate before sending, never trust URL params
const reportId = route.params['id'];
if (!isValidUuid(reportId)) {
  router.navigate(['/not-found']);
  return;
}
```

---

## SQL Injection Prevention

Always use parameterized queries. Never interpolate user input into SQL.

```python
# BigQuery
query = "SELECT * FROM `dataset.table` WHERE id = @id AND status = @status"
job_config = bigquery.QueryJobConfig(query_parameters=[
    bigquery.ScalarQueryParameter("id", "STRING", user_id),
    bigquery.ScalarQueryParameter("status", "STRING", status),
])

# SQLAlchemy ORM - safe by default
stmt = select(Report).where(Report.id == report_id)

# NEVER do:
query = f"SELECT * FROM reports WHERE id = '{user_input}'"  # SQL INJECTION
```

---

## Secrets Management

- Never commit secrets to git
- Never hardcode API keys, passwords, or connection strings in code
- Load from environment variables or secret managers at runtime
- Add `.env`, `*.pem`, `*.key`, `service-account*.json` to `.gitignore`

```python
DATABASE_URL = os.environ["DATABASE_URL"]  # fails fast if missing
API_KEY = os.environ.get("EXTERNAL_API_KEY")
if not API_KEY:
    raise RuntimeError("EXTERNAL_API_KEY environment variable required")
```

---

## XSS Prevention

```typescript
// Angular: interpolation {{ }} is safe (auto-escaped)
// NEVER bypass sanitization:
// BAD: [innerHTML]="userContent"
// GOOD: {{ userContent }}

// If raw HTML is required:
import { DomSanitizer, SecurityContext } from '@angular/platform-browser';
const safe = sanitizer.sanitize(SecurityContext.HTML, rawContent);
```

```tsx
// React: JSX expressions are safe by default
// NEVER use dangerouslySetInnerHTML with user content
// If required, sanitize first:
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userHtml);
```

---

## CSRF Protection

- If using JWT in `Authorization` header: CSRF protection is NOT needed
- If using cookies: CSRF middleware is required

```typescript
// Angular: enable XSRF protection in app.config.ts
provideHttpClient(
  withXsrfConfiguration({ cookieName: 'XSRF-TOKEN', headerName: 'X-XSRF-TOKEN' }),
)
```

---

## Rate Limiting

Apply to all authentication and sensitive endpoints.

```python
# FastAPI with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest) -> TokenResponse: ...
```
