---
applyTo: ['**/*.py', '**/*.ts', '**/*.tsx', '**/*.ps1', '**/*.html', '**/*.scss']
description: "Naming conventions for Python, TypeScript, Angular, React, PowerShell, API, database, and Git. Applied to all code and config files."
---

# Naming Conventions

## Python

| Element | Convention | Example |
|---------|-----------|---------|
| Module/file | snake_case | `report_service.py` |
| Class | PascalCase | `ReportService` |
| Function/method | snake_case | `get_by_company()` |
| Variable | snake_case | `report_count` |
| Constant (module-level) | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| Private | leading underscore | `_validate_input()` |
| Type alias | PascalCase | `ReportMap` |
| Pydantic schema | PascalCase + suffix | `ReportCreate`, `ReportResponse` |
| FastAPI router | snake_case | `report_router` |
| Test function | `test_` + descriptive | `test_create_report_with_invalid_year()` |
| Fixture | snake_case, noun | `mock_service`, `db_session` |

### Python Rules
- Boolean variables/params: use `is_`, `has_`, `can_` prefix: `is_active`, `has_permission`
- Async functions: no special naming (`async` keyword is sufficient)
- Abbreviations allowed: `db`, `id`, `url`, `api` - avoid all others

---

## TypeScript (shared Angular + React)

| Element | Convention | Example |
|---------|-----------|---------|
| File | kebab-case | `report-list.component.ts` |
| Class | PascalCase | `ReportListComponent` |
| Interface | PascalCase (no `I` prefix) | `Report`, `UserProfile` |
| Type alias | PascalCase | `LoadState<T>` |
| Enum | PascalCase | `ReportStatus` |
| Enum values | PascalCase | `ReportStatus.Draft` |
| Function | camelCase | `getReportById()` |
| Variable | camelCase | `reportCount` |
| Constant (module-level) | UPPER_SNAKE | `MAX_RETRIES` |
| Constant (local/function) | camelCase | `defaultConfig` |
| Observable | camelCase + `$` suffix | `reports$`, `loading$` |
| Signal | camelCase (no suffix) | `reports`, `loading` |
| Private member | no underscore (use `private`) | `private readonly service` |

### Angular-Specific

| Element | Convention | Example |
|---------|-----------|---------|
| Component | PascalCase + `Component` | `ReportListComponent` |
| Service | PascalCase + `Service` | `ReportService` |
| Directive | PascalCase + `Directive` | `HighlightDirective` |
| Pipe | PascalCase + `Pipe` | `DateFormatPipe` |
| Guard | PascalCase + `Guard` | `AuthGuard` |
| Interceptor | camelCase + `Interceptor` | `errorInterceptor` (fn) |
| Selector (element) | `app-` + kebab-case | `app-report-card` |
| Selector (directive) | `app` + camelCase | `appTooltip` |

### React-Specific

| Element | Convention | Example |
|---------|-----------|---------|
| Component | PascalCase | `ReportList` |
| Hook | camelCase + `use` prefix | `useReports()` |
| Context | PascalCase + `Context` | `AuthContext` |
| Props interface | PascalCase + `Props` | `ReportListProps` |
| Event handler | `handle` + Event | `handleClick`, `handleSubmit` |
| Event handler prop | `on` + Event | `onClick`, `onSubmit` |

---

## Files and Folders

| Type | Convention | Example |
|------|-----------|---------|
| Python module | snake_case | `report_service.py` |
| TS/Angular file | kebab-case + suffix | `report-list.component.ts` |
| React component | PascalCase | `ReportList.tsx` |
| React util | camelCase | `useReports.ts` |
| Test file | same name + `.test`/`.spec` | `report.service.spec.ts` |
| Config file | kebab-case | `eslint.config.mjs` |
| Folder | kebab-case | `report-management/` |
| Docs | kebab-case | `error-handling-patterns.md` |

---

## API and Database

| Element | Convention | Example |
|---------|-----------|---------|
| URL path | kebab-case, plural | `/api/v1/data-points` |
| Query param | snake_case | `?company_id=abc&page_size=20` |
| JSON field (backend) | snake_case | `created_at`, `company_id` |
| JSON field (frontend) | camelCase | `createdAt`, `companyId` |
| DB table | snake_case, plural | `reports`, `data_points` |
| DB column | snake_case | `created_at`, `company_id` |
| DB index | `idx_` + table + columns | `idx_reports_company_status` |

---

## Git

| Element | Convention | Example |
|---------|-----------|---------|
| Branch | type/ticket-description | `feature/ABC-123-user-auth` |
| Commit | type(scope): subject | `feat(api): add report export` |
| Tag | semver | `v1.2.0` |
| PR title | same as commit | `fix(auth): refresh token rotation` |

---

## Anti-Patterns

Never use:
- Generic names: `data`, `info`, `item`, `result` as standalone identifiers
- Vague handlers: `handleData`, `processStuff`
- Hungarian notation: `strName`, `iCount`
- Non-standard abbreviations: `rpt`, `usr`, `mgr` (write full words)
- Inconsistent pluralization
