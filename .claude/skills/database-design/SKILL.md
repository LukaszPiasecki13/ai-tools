---
name: database-design
description: Database modeling patterns for SQL, NoSQL (Firestore), BigQuery. Schema design, indexing, queries, and data migration. Use when the user asks about data models, database queries, schema changes, or data architecture.
user-invocable: false
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
