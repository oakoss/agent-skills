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

## Native UUIDv7 Support

PostgreSQL 18 introduces native `uuidv7()` generation. This is the preferred primary key format, combining global uniqueness with sequential ordering for significantly improved B-tree index performance and reduced page splits.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  email TEXT UNIQUE NOT NULL
);
```

## Virtual Generated Columns

Generated columns that default to VIRTUAL occupy zero disk space and are calculated on the fly during SELECT.

```sql
CREATE TABLE products (
  price_cents INTEGER NOT NULL,
  tax_rate DECIMAL NOT NULL,
  total_price_cents INTEGER GENERATED ALWAYS AS (price_cents * (1 + tax_rate)) VIRTUAL
);
```

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
