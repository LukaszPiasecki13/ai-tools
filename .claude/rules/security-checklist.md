---
paths: ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.ps1"]
description: OWASP Top 10 security checklist - JWT auth, input validation, SQL injection, XSS, CSRF, rate limiting, secrets management. Auto-loaded for Python, TypeScript, and PowerShell files.
---

# Security Checklist

OWASP Top 10. Apply to all code handling auth, user input, database access, or secrets.

## Authentication (JWT)

- Use `PyJWT`. Do NOT use `python-jose` - unmaintained since 2022.
- Algorithms: `RS256` with `audience` and `issuer` validation.
- Access tokens: 15-30 min lifetime. Refresh tokens: 7-30 days, rotate on use.
- Store refresh tokens in `httpOnly`, `Secure`, `SameSite=Strict` cookies. Never in `localStorage`.

## Input Validation

- Validate at system boundary only (API routes). Never trust URL params, request bodies, or query strings.
- Backend: Pydantic with strict field constraints (`min_length`, `max_length`, `pattern`, `Literal` whitelist).
- Frontend: validate UUIDs/IDs before routing or API calls. Never trust route params directly.

## SQL Injection Prevention

- Always use parameterized queries. Never interpolate user input into SQL strings.
- BigQuery: use `QueryJobConfig` with `ScalarQueryParameter`. SQLAlchemy ORM is safe by default.

## Secrets Management

- Never commit secrets, API keys, passwords, or connection strings to git.
- Load from environment variables (`os.environ["KEY"]` - fails fast if missing) or secret managers.
- Add `.env`, `*.pem`, `*.key`, `service-account*.json` to `.gitignore` (already covered by `.claudeignore` for Claude's own file access).

## XSS Prevention

- Angular: `{{ }}` interpolation is safe. Never use `[innerHTML]` with user content. Use `DomSanitizer` if raw HTML is required.
- React: JSX expressions are safe. Never use `dangerouslySetInnerHTML` with user content. Use `DOMPurify` if required.

## CSRF Protection

- JWT in `Authorization` header: CSRF protection not needed.
- Cookie-based auth: CSRF middleware required. Angular: configure `withXsrfConfiguration()` in `provideHttpClient()`.

## Rate Limiting

- Apply to all auth and sensitive endpoints. FastAPI: use `slowapi`. Login endpoints: max 5/minute.
