---
name: database-design
description: Database modeling patterns for SQL, NoSQL (Firestore), BigQuery. Schema design, indexing, queries, and data migration. Use when the user asks about data models, database queries, schema changes, or data architecture.
---

# Database Design Skill

## Data Modeling Principles

1. **Start from access patterns** - design schema based on how data is read, not just written
2. **Normalize for writes, denormalize for reads** - balance based on workload
3. **Plan for evolution** - schemas will change, design for migration
4. **Index intentionally** - every index has a write cost

## SQL Schema Patterns

### Table Naming
- Plural nouns: `users`, `reports`, `data_points`
- Junction tables: `user_roles`, `report_indicators`
- Snake_case for all identifiers

### Common Column Patterns
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- soft delete
);
```

### Indexing Strategy
```sql
-- Index columns used in WHERE, JOIN, ORDER BY
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_by ON reports(created_by);

-- Composite index for common query patterns
CREATE INDEX idx_reports_status_year ON reports(status, year);

-- Partial index for active records only
CREATE INDEX idx_reports_active ON reports(status) WHERE deleted_at IS NULL;
```

## Firestore/NoSQL Patterns

### Document Structure
```
/companies/{companyId}
  - name: string
  - settings: map
  
/companies/{companyId}/reports/{reportId}
  - title: string
  - status: string
  - year: number
  - indicators: subcollection or array (depends on size)
```

### When to use subcollections vs arrays
| Use subcollection | Use array/map |
|-------------------|---------------|
| Items > 20 | Items < 20 |
| Need independent queries | Always loaded together |
| Items grow unbounded | Fixed/bounded size |
| Need pagination | Small payload |

### Firestore Query Patterns
```python
# Simple query
docs = db.collection("reports").where("status", "==", "published").stream()

# Composite query (requires composite index)
docs = (db.collection("reports")
    .where("company_id", "==", company_id)
    .where("year", "==", 2024)
    .order_by("created_at", direction=firestore.Query.DESCENDING)
    .limit(20)
    .stream())
```

### Firestore Limitations
- Max document size: 1 MB
- Max write rate per document: 1/second
- No joins - denormalize or do client-side joins
- Composite queries need composite indexes
- `!=` and `not-in` have index requirements

## BigQuery Patterns

### Table Design
- Partition by date/timestamp for cost and performance
- Cluster by commonly filtered columns
- Use nested/repeated fields for denormalized data

```sql
CREATE TABLE dataset.reports
PARTITION BY DATE(created_at)
CLUSTER BY company_id, status
AS SELECT ...
```

### Query Cost Optimization
- Always filter on partition column
- Select only needed columns (columnar storage)
- Use `LIMIT` for exploratory queries
- Avoid `SELECT *` in production

## Migration Patterns

### Schema Evolution Rules
1. Adding columns: always nullable or with default
2. Removing columns: deprecate first, remove in next release
3. Renaming: add new, migrate data, remove old
4. Type changes: create new column, backfill, swap

### Migration Script Template
```sql
-- Migration: 001_add_status_column
-- Date: YYYY-MM-DD
-- Description: Add status tracking to reports

ALTER TABLE reports ADD COLUMN status VARCHAR(50) DEFAULT 'draft';
UPDATE reports SET status = 'published' WHERE published_at IS NOT NULL;
ALTER TABLE reports ALTER COLUMN status SET NOT NULL;
```

## Anti-Patterns to Avoid
- Storing JSON blobs in SQL without schema
- Using string IDs without indexing
- Unbounded arrays in NoSQL documents
- Missing created_at/updated_at timestamps
- Hard deletes without audit trail
