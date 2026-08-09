---
paths: ["**/*.py"]
description: Python 3.12+ coding standards - Ruff, mypy strict, FastAPI patterns, pytest. Auto-loaded for Python files.
---

# Python Coding Standards

Python 3.12+ with FastAPI or Django REST. Toolchain: `uv`, Ruff, mypy strict, pytest.

## Package Management

Use `uv` exclusively - not pip or poetry. Always commit `uv.lock`. Do not commit `.venv/`.

## Formatting Rules (Ruff)

- Line length: 88 characters
- Indent: 4 spaces
- Quotes: double (`"`)
- Imports: stdlib, then third-party, then local (isort-compatible)

## Type Safety (mypy strict)

All functions must have full type annotations.

```python
# Use | for unions (Python 3.10+)
def get_user(user_id: str) -> User | None: ...

# Type aliases
from typing import TypeAlias
ReportMap: TypeAlias = dict[str, list[ReportResponse]]

# Protocol for structural typing
from typing import Protocol
class Repository(Protocol):
    async def get(self, id: str) -> dict | None: ...
    async def save(self, data: dict) -> str: ...
```

## FastAPI Patterns

### Router structure
```python
from fastapi import APIRouter, Depends, status
from app.schemas.report import ReportCreate, ReportResponse
from app.services.report_service import ReportService
from app.dependencies import get_current_user, get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return await service.create(data, current_user.id)
```

### Pydantic schemas
```python
from pydantic import BaseModel, Field, ConfigDict

class ReportBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=2020, le=2030)

class ReportCreate(ReportBase):
    """What the client sends."""

class ReportResponse(ReportBase):
    """What the server returns."""
    id: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### Configuration (pydantic-settings)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    allowed_origins: list[str] = []
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

### Dependencies
```python
from collections.abc import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

## Code Quality Rules

| Rule | Limit |
|------|-------|
| Cyclomatic complexity | max 10 |
| Function length | ~50 lines |
| File length | ~300 lines |

### Prefer
- f-strings over `.format()`
- `pathlib.Path` over `os.path`
- Structural pattern matching (`match`/`case`) for multi-branch logic
- Dependency injection over global mutable state

### Avoid
```python
# Mutable default arguments - BUG
def bad(items: list = []):  ...
def good(items: list | None = None):
    items = items or []

# Bare except - NEVER
try: ...
except:  ...
# Instead:
except (ValueError, KeyError) as e:
    logger.error(f"Processing failed: {e}")
```

## Testing (pytest)

Configure in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # no @pytest.mark.asyncio needed per test
```

```python
@pytest.fixture
def mock_service() -> AsyncMock:
    service = AsyncMock(spec=ReportService)
    service.get.return_value = ReportResponse(id="1", title="Test", ...)
    return service

async def test_create_report_success(client: AsyncClient, mock_service: AsyncMock):
    response = await client.post("/api/v1/reports", json={"title": "New", "year": 2024})
    assert response.status_code == 201

@pytest.mark.parametrize("invalid_year", [-1, 2019, 2031])
async def test_create_report_invalid_year(client: AsyncClient, invalid_year: int):
    response = await client.post("/api/v1/reports", json={"title": "X", "year": invalid_year})
    assert response.status_code == 422
```

## Docstrings

Add only to: public API functions, complex business logic, non-obvious algorithms.
Skip for: private helpers, simple CRUD, test functions.
Format: Google style with `Args`/`Returns`/`Raises` sections.

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|----------|
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

- Boolean variables/params: `is_`, `has_`, `can_` prefix (`is_active`, `has_permission`)
- Async functions: no special naming (`async` keyword is sufficient)
- Abbreviations allowed: `db`, `id`, `url`, `api` - avoid all others

## API and Database Naming

| Element | Convention | Example |
|---------|-----------|----------|
| URL path | kebab-case, plural | `/api/v1/data-points` |
| Query param | snake_case | `?company_id=abc&page_size=20` |
| JSON field | snake_case | `created_at`, `company_id` |
| DB table | snake_case, plural | `reports`, `data_points` |
| DB column | snake_case | `created_at`, `company_id` |
| DB index | `idx_` + table + columns | `idx_reports_company_status` |
