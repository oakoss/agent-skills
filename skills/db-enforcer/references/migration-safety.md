---
title: Migration Safety
description: Zero-downtime migration protocols, destructive change handling, lock management, idempotent migrations, backfill patterns, CI/CD integration, and rollback strategies
tags:
  [
    migrations,
    zero-downtime,
    rollback,
    prisma-migrate,
    lock-management,
    backfill,
    idempotent,
    ci-cd,
  ]
---

# Migration Safety

## The Migration Lifecycle

1. **Generate**: Use `prisma migrate dev --create-only` to review the SQL first
2. **Audit**: Check for destructive changes (DROP COLUMN, RENAME COLUMN)
3. **Test**: Apply to a staging/preview database before production
4. **Execute**: Run `prisma migrate deploy` in the CI/CD pipeline

## Zero-Downtime Column Rename

Never rename a column in a single deployment. Use the expand-and-contract pattern across multiple deployments:

**Phase 1 — Expand: add new column**

```sql
ALTER TABLE users ADD COLUMN display_name TEXT;
```

**Phase 2 — Dual-write in application code**

Update the application to write to both `name` and `display_name` simultaneously. Deploy this before any data migration.

```ts
await prisma.user.update({
  where: { id },
  data: { name: value, displayName: value },
});
```

**Phase 3 — Backfill existing rows**

Run as a separate migration after dual-write is deployed and stable:

```sql
UPDATE users
SET display_name = name
WHERE display_name IS NULL;
```

For large tables, use the batched backfill pattern described in the Backfill Patterns section.

**Phase 4 — Migrate reads to new column**

Deploy application code that reads exclusively from `display_name`. Keep dual-write active during this phase.

**Phase 5 — Wait for rollback window**

Allow at least 48 hours before proceeding. If rollback is needed, the old column still has current data.

**Phase 6 — Contract: drop old column**

Deploy a separate migration to remove the old column only after the rollback window has passed:

```sql
ALTER TABLE users DROP COLUMN name;
```

## Idempotent Migrations

Migrations that can safely re-run prevent failures in pipelines where migrations may execute multiple times (e.g., due to retries or multi-region deploys).

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_users_verified_at ON users (verified_at);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name = 'users_email_verified_check'
      AND table_name = 'users'
  ) THEN
    ALTER TABLE users ADD CONSTRAINT users_email_verified_check
      CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$');
  END IF;
END $$;
```

For enum types, check existence before creating:

```sql
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status') THEN
    CREATE TYPE user_status AS ENUM ('active', 'suspended', 'deleted');
  END IF;
END $$;
```

## Lock Management

### Set a Lock Timeout

Always set a lock timeout before DDL statements to prevent indefinite blocking:

```sql
SET lock_timeout = '2s';
ALTER TABLE users ADD COLUMN last_seen_at TIMESTAMPTZ;
```

If the lock cannot be acquired within the timeout, the statement fails immediately rather than blocking all queries on that table.

### Avoid Long-Running Transactions During DDL

DDL inside a long transaction holds locks for the entire transaction duration. Keep DDL statements in short, isolated transactions:

```sql
BEGIN;
SET lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS fulfilled_at TIMESTAMPTZ;
COMMIT;
```

Never combine DDL with bulk DML in the same transaction on high-traffic tables.

### CREATE INDEX CONCURRENTLY

`CREATE INDEX CONCURRENTLY` builds the index without holding a lock on the table, allowing reads and writes to continue. It cannot run inside a transaction block.

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id
  ON orders (user_id);
```

In Prisma raw migrations, wrap concurrent index creation outside transactions:

```sql
-- This file must not be wrapped in BEGIN/COMMIT by the migration runner
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
  ON orders (status)
  WHERE status != 'completed';
```

If a concurrent index build fails partway through, it leaves an invalid index. Clean it up before retrying:

```sql
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_status;
```

### NOT NULL Addition on Large Tables

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

## Backfill Patterns

### Batched UPDATE with LIMIT

Backfilling millions of rows in a single UPDATE locks the table and risks transaction log exhaustion. Use cursor-based batching instead:

```sql
DO $$
DECLARE
  batch_size INT := 1000;
  last_id UUID := '00000000-0000-0000-0000-000000000000';
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET display_name = name
    WHERE id > last_id
      AND display_name IS NULL
      AND id IN (
        SELECT id FROM users
        WHERE id > last_id
          AND display_name IS NULL
        ORDER BY id
        LIMIT batch_size
      )
    RETURNING id INTO last_id;

    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;

    PERFORM pg_sleep(0.05);
  END LOOP;
END $$;
```

### Monitoring Backfill Progress

Track progress without interrupting the backfill:

```sql
SELECT
  COUNT(*) FILTER (WHERE display_name IS NOT NULL) AS backfilled,
  COUNT(*) FILTER (WHERE display_name IS NULL)     AS remaining,
  COUNT(*)                                         AS total,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE display_name IS NOT NULL) / COUNT(*),
    2
  ) AS pct_complete
FROM users;
```

### Avoiding Table Locks During Backfill

- Use small batch sizes (500–2000 rows) with short sleeps between batches
- Target rows by primary key range, not offset, to avoid full scans
- Run backfill during low-traffic windows when possible
- Never wrap the entire backfill in a single transaction

## CI/CD Integration

### Pre-Deploy vs Post-Deploy Migrations

Classify each migration before running it in the pipeline:

| Migration type                 | When to run | Why                                               |
| ------------------------------ | ----------- | ------------------------------------------------- |
| Add nullable column            | Pre-deploy  | Safe to apply before new code reads it            |
| Add index (`CONCURRENTLY`)     | Pre-deploy  | No lock; new code benefits immediately            |
| Add NOT NULL constraint        | Post-deploy | Requires backfill to complete first               |
| Drop column                    | Post-deploy | Old code must be retired before column is removed |
| Rename column (expand phase)   | Pre-deploy  | Add new column before code writes to it           |
| Rename column (contract phase) | Post-deploy | Remove old column after all reads have switched   |

### Running Migrations in the Pipeline

```bash
# Verify schema is in sync before deploying
npx prisma validate

# Apply pending migrations (non-interactive, safe for CI)
npx prisma migrate deploy

# Run post-deploy migrations separately after smoke tests pass
npx prisma migrate deploy --schema=prisma/post-deploy.prisma
```

For raw SQL migrations outside Prisma:

```bash
psql "$DATABASE_URL" \
  --set ON_ERROR_STOP=1 \
  --single-transaction \
  -f db/migrations/042_add_fulfilled_at.sql
```

Use `--single-transaction` for DDL-only migrations where atomicity is safe. Omit it when the migration contains `CREATE INDEX CONCURRENTLY` (which cannot run inside a transaction).

### Deployment Rollback

Every migration must have a documented rollback. Store rollback scripts alongside forward migrations:

```text
db/migrations/042_add_fulfilled_at.sql
db/migrations/042_add_fulfilled_at.rollback.sql
```

For irreversible changes (data deletion, column removal), verify a point-in-time backup exists before running the migration.

## Numbered Migration Standard

Use 3-digit numbered sequences for clarity and ordering:

```text
db/migrations/001_initial_schema.sql
db/migrations/002_add_roles.sql
db/migrations/003_add_team_permissions.sql
```

## Rollback Strategy

Every migration must have a corresponding rollback plan documented, even if not automated. For irreversible changes (data deletion, column removal), ensure data is backed up before execution.
