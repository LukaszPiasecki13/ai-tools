---
name: api-design
description: REST API design patterns, schema validation, versioning, error handling, and documentation. Use when the user asks about API endpoints, request/response schemas, HTTP conventions, or API architecture.
user-invocable: false
---

# API Design Skill

## REST Conventions

### URL Structure
```
GET    /api/v1/resources          # List
GET    /api/v1/resources/:id      # Get one
POST   /api/v1/resources          # Create
PUT    /api/v1/resources/:id      # Full update
PATCH  /api/v1/resources/:id      # Partial update
DELETE /api/v1/resources/:id      # Delete
```

### Naming Rules
- Use plural nouns for collections: `/users`, `/reports`
- Use kebab-case for multi-word: `/data-points`, `/report-statuses`
- Nest for relationships: `/users/:id/reports`
- Use query params for filtering: `/reports?status=draft&year=2024`

### HTTP Status Codes
| Code | Meaning | Use when |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed input |
| 401 | Unauthorized | Missing or invalid auth |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate, version conflict |
| 422 | Unprocessable | Semantically invalid input |
| 500 | Internal Error | Unexpected server failure |

## Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      {"field": "email", "issue": "Invalid email format"}
    ]
  }
}
```

## Schema Design (Pydantic/FastAPI)

### Request vs Response schemas
```python
# Base - shared fields
class ResourceBase(BaseModel):
    name: str
    description: str | None = None

# Create - what client sends
class ResourceCreate(ResourceBase):
    pass

# Response - what server returns
class ResourceResponse(ResourceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Validation Patterns
```python
from pydantic import BaseModel, Field, field_validator

class CreateReport(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=2020, le=2030)
    
    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()
```

## Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 142,
    "total_pages": 8
  }
}
```

Query params: `?page=1&page_size=20&sort_by=created_at&order=desc`

## Versioning Strategy

- URL path versioning: `/api/v1/`, `/api/v2/`
- Only increment major version for breaking changes
- Support previous version for deprecation period
- Document breaking changes in changelog

## Authentication Patterns

### Bearer Token
```
Authorization: Bearer <jwt-token>
```

### API Key (service-to-service)
```
X-API-Key: <key>
```

## Rate Limiting Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

## Documentation

- Use OpenAPI/Swagger for auto-generated docs
- Include request/response examples for each endpoint
- Document all error codes and their meaning
- Specify required vs optional fields clearly
