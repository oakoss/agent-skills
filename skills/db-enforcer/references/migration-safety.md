---
title: Migration Safety
description: Zero-downtime migration protocols, destructive change handling, lock management, numbered migration standards, and rollback strategies
tags: [migrations, zero-downtime, rollback, prisma-migrate, lock-management]
---

# Migration Safety

## The Migration Lifecycle

1. **Generate**: Use `prisma migrate dev --create-only` to review the SQL first
2. **Audit**: Check for destructive changes (DROP COLUMN, RENAME COLUMN)
3. **Test**: Apply to a staging/preview database before production
4. **Execute**: Run `prisma migrate deploy` in the CI/CD pipeline

## Handling Destructive Changes

Never DROP or RENAME in a single deployment. Use the expand-and-contract pattern:

1. Add the new column (keep the old one)
2. Write to both columns in application code
3. Backfill data from old to new
4. Switch reads to the new column
5. Wait 48 hours for rollback safety
6. Drop the old column in a separate migration

## Lock Management

Avoid long-running migrations that lock tables:

- **Index Creation**: Always use `CREATE INDEX CONCURRENTLY` in raw SQL migrations
- **NOT NULL Addition**: Add columns as NULL first, backfill data, then add NOT NULL constraint (use NOT VALID for large tables as described in the PostgreSQL integrity reference)

```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 2: Backfill (run as a batch job)
UPDATE users SET display_name = name WHERE display_name IS NULL;

-- Step 3: Add constraint without full lock
ALTER TABLE users ADD CONSTRAINT users_display_name_not_null
CHECK (display_name IS NOT NULL) NOT VALID;

-- Step 4: Validate separately
ALTER TABLE users VALIDATE CONSTRAINT users_display_name_not_null;
```

## Numbered Migration Standard

Use 3-digit numbered sequences for clarity and ordering:

```text
db/migrations/001_initial_schema.sql
db/migrations/002_add_roles.sql
db/migrations/003_add_team_permissions.sql
```

## Rollback Strategy

Every migration must have a corresponding rollback plan documented, even if not automated. For irreversible changes (data deletion, column removal), ensure data is backed up before execution.
