---
name: testing
description: Testing patterns and frameworks for Python (pytest, pytest-asyncio), TypeScript (Vitest, Jest), and Angular (Testing Library). Use when the user asks about writing tests, test coverage, mocking, fixtures, test setup, or testing strategy.
---

# Testing Skill

## Python - pytest

### Setup
```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--strict-markers -q"

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "*/migrations/*"]
```

### File Structure
```
tests/
├── conftest.py          # shared fixtures
├── unit/
│   └── test_service.py
├── integration/
│   └── test_api.py
└── test_utils.py
```

### Fixtures and Mocking

```python
# conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_firestore():
    db = AsyncMock()
    db.collection.return_value.document.return_value.get.return_value.exists = True
    return db

@pytest.fixture
def mock_current_user():
    return {"uid": "user-123", "email": "test@example.com", "roles": ["viewer"]}
```

```python
# Patching at import point (not where it is defined)
@patch("app.services.user_service.send_email")
async def test_register_sends_email(mock_send, client):
    response = await client.post("/api/users", json={"email": "a@b.com"})
    assert response.status_code == 201
    mock_send.assert_called_once_with(to="a@b.com", template="welcome")
```

### Parametrize

```python
@pytest.mark.parametrize("status,expected_code", [
    ("draft", 200),
    ("submitted", 403),
    ("archived", 404),
])
async def test_report_access_by_status(status, expected_code, client, mock_report):
    mock_report.status = status
    response = await client.get(f"/api/reports/{mock_report.id}")
    assert response.status_code == expected_code
```

### FastAPI Test Client

```python
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client(mock_firestore):
    app.dependency_overrides[get_db] = lambda: mock_firestore
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
```

---

## TypeScript - Vitest

### Setup
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    environment: 'node',       // or 'jsdom' for DOM
    globals: true,
    coverage: { provider: 'v8', reporter: ['text', 'lcov'] },
  },
});
```

### Mocking

```typescript
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Module mock
vi.mock('../api/client', () => ({
  apiClient: { get: vi.fn(), post: vi.fn() }
}));

// Spy on method without replacing
const spy = vi.spyOn(service, 'calculateTax').mockReturnValue(100);

// Restore after test
afterEach(() => vi.restoreAllMocks());

// Mock timers
vi.useFakeTimers();
vi.advanceTimersByTime(5000);
vi.useRealTimers();
```

---

## Angular - Testing Library + Vitest

### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/angular';
import { LoginComponent } from './login.component';
import { ReactiveFormsModule } from '@angular/forms';

describe('LoginComponent', () => {
  it('disables submit button while loading', async () => {
    const { fixture } = await render(LoginComponent, {
      imports: [ReactiveFormsModule],
    });

    const button = screen.getByRole('button', { name: /login/i });
    fireEvent.click(button);
    expect(button).toBeDisabled();
  });
});
```

### Service with HttpClient

```typescript
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

describe('ReportService', () => {
  let service: ReportService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ReportService],
    });
    service = TestBed.inject(ReportService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('fetches reports by year', () => {
    service.getReports(2024).subscribe(reports => {
      expect(reports).toHaveLength(3);
    });
    const req = httpMock.expectOne('/api/reports?year=2024');
    req.flush([{}, {}, {}]);
  });
});
```

---

## Coverage Guidelines

| Priority | What to test |
|----------|-------------|
| High | Business logic with branching, auth checks, input validation |
| Medium | API endpoints (happy path + error cases), DB queries |
| Low | Simple utilities, pure transformations, trivial getters |
| Skip | Third-party library wrappers, generated code, config files |

Target: 80%+ on business logic files. Do not chase 100% at the cost of test quality.
