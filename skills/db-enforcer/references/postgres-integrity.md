---
title: PostgreSQL Integrity
description: Advanced PostgreSQL constraints, UUIDv7 primary keys, virtual columns, temporal uniqueness, and NOT VALID constraint patterns
tags:
  [
    postgresql,
    uuidv7,
    constraints,
    virtual-columns,
    temporal,
    check-constraints,
  ]
---

# PostgreSQL Integrity

## Native UUIDv7 Support (PostgreSQL 18+)

PostgreSQL 18 introduces the native `uuidv7()` function (RFC 9562). This is the preferred primary key format, combining global uniqueness with sequential ordering for significantly improved B-tree index performance and reduced page splits. The implementation includes a 12-bit sub-millisecond timestamp fraction that guarantees monotonicity within a session.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  email TEXT UNIQUE NOT NULL
);
```

For PostgreSQL versions before 18, use the `pgcrypto` extension with `gen_random_uuid()` (UUIDv4) or install a third-party extension for UUIDv7 support.

**Security note:** UUIDv7 embeds a 48-bit timestamp, leaking creation time. Avoid exposing UUIDv7 primary keys in public-facing APIs where creation time is sensitive.

## Virtual Generated Columns (PostgreSQL 18+)

PostgreSQL 18 introduces virtual generated columns that occupy zero disk space and are calculated on the fly during SELECT. Virtual is the default kind in PostgreSQL 18; the `VIRTUAL` keyword is optional.

```sql
CREATE TABLE products (
  price_cents INTEGER NOT NULL,
  tax_rate DECIMAL NOT NULL,
  -- VIRTUAL is default in PG 18, STORED writes to disk
  total_price_cents INTEGER GENERATED ALWAYS AS (price_cents * (1 + tax_rate)) VIRTUAL
);
```

**Limitations of virtual columns:** Cannot be indexed (indexing support planned for PostgreSQL 19), cannot use user-defined types or functions in the generation expression, and cannot be logically replicated.

For PostgreSQL versions before 18, only `STORED` generated columns are available.

## Advanced CHECK Constraints

Enforce business logic at the database level. CHECK constraints mirror TypeScript types to prevent drift.

```sql
ALTER TABLE orders
ADD CONSTRAINT check_discount_logic
CHECK (discount_price < original_price);
```

Conditional constraints for enums ensure data consistency:

```sql
ALTER TABLE tasks
ADD CONSTRAINT check_completion_date
CHECK (
  (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
  (status != 'COMPLETED' AND completed_at IS NULL)
);
```

## Temporal Constraints

Define uniqueness over time ranges to prevent overlapping schedules or double-bookings natively.

```sql
CREATE TABLE bookings (
  room_id INTEGER,
  booking_period TSTZRANGE,
  EXCLUDE USING gist (room_id WITH =, booking_period WITH &&)
);
```

## NOT VALID Constraint Pattern

Add constraints to large tables without locking the database for hours. This is a two-step process:

1. Add as NOT VALID (takes a brief lock, does not scan existing rows):

```sql
ALTER TABLE logs
ADD CONSTRAINT check_level
CHECK (level IN ('INFO', 'WARN', 'ERROR')) NOT VALID;
```

2. Validate later (scans rows but only takes a SHARE UPDATE EXCLUSIVE lock):

```sql
ALTER TABLE logs VALIDATE CONSTRAINT check_level;
```
