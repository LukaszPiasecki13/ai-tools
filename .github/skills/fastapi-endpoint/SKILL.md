---
name: fastapi-endpoint
description: "Scaffold a FastAPI endpoint end to end - schema, route, service, test - following the project's existing layering."
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/fastapi-endpoint/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# FastAPI Endpoint

Requested: **$ARGUMENTS**

## 1. Copy the project, not the template

Before writing a line, read one existing endpoint in the same app and match it: router
location, dependency names, service boundaries, error mapping, test fixtures. The
`python-coding-standards` rule is already in context; this step is about the conventions
that rule does not cover because they are specific to this codebase.

If the project has no endpoint yet, say so and propose the layering before generating it.

## 2. Write the pieces in this order

**Schemas** (`schemas/<resource>.py`) — request and response are separate types. Never return
an ORM model directly. Every field carries its constraint (`min_length`, `ge`, `Literal`),
because that constraint is the validation.

```python
class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=2020, le=2030)

class ReportResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

Query parameters go in their own `BaseModel` used with `Depends()` — even a single one.

**Service** (`services/<resource>_service.py`) — the business logic and the database work.
The route must stay thin enough that it has nothing to unit-test on its own.

**Route** (`api/<resource>.py`) — wiring only:

```python
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return await service.create(data, current_user.id)
```

**Authorization is not optional.** Every route states who may call it. If this endpoint is
genuinely public, write that as a comment saying why — an unauthenticated route with no
explanation reads as an oversight, and usually is one.

**Errors** — raise the project's domain exceptions from the service; map them to HTTP at one
place per app, not per route. Never leak an internal message into the response body.

## 3. Tests, in the same task

Cover, at minimum:

- success path with the status code asserted
- each validation boundary (`422`), parametrized rather than copy-pasted
- unauthorized (`401`) and forbidden (`403`) where authorization applies
- the not-found path

```python
@pytest.mark.parametrize("invalid_year", [2019, 2031])
async def test_create_report_rejects_year_outside_range(client, invalid_year):
    response = await client.post("/api/v1/reports", json={"title": "X", "year": invalid_year})
    assert response.status_code == 422
```

## 4. Migrations

If the endpoint needs a schema change, generate the migration with the project's tooling
(`alembic revision --autogenerate -m "..."`) and review the generated file before running it.
Never hand-write a migration.

## 5. Finish

Run the new tests and the linter. Report the commands and their output. Then state the
endpoint's contract in two lines — method, path, auth requirement, status codes — so it can
go straight into the API documentation or the PR body.
