---
name: db-enforcer
description: 'Enforces database integrity for PostgreSQL and Prisma systems. Use when designing schemas, writing migrations, or configuring Row-Level Security. Use for type-safe SQL, naming alignment, constraint validation, zero-trust RLS policies, UUIDv7 primary keys, and zero-downtime deployments.'
---

# DB Enforcer

## Overview

Enforces data integrity and architectural consistency between the TypeScript application layer and the PostgreSQL persistence layer. Prevents type drift by ensuring CHECK constraints mirror TypeScript types, migrations are generated before applying changes, and Row-Level Security protects every table.

**When to use:** Schema design, migration planning, RLS policy authoring, Prisma model mapping, constraint auditing, zero-downtime deployments.

**When NOT to use:** Application-level business logic, frontend state management, non-PostgreSQL databases.

## Quick Reference

| Pattern               | API/Tool                            | Key Points                                 |
| --------------------- | ----------------------------------- | ------------------------------------------ |
| Type-to-DB sync       | `prisma migrate dev --create-only`  | Generate SQL before applying changes       |
| Naming alignment      | `@map` / `@@map`                    | snake_case in SQL, camelCase in TS         |
| Primary keys          | `DEFAULT uuidv7()`                  | Sequential, globally unique, fast indexing |
| Virtual columns       | `GENERATED ALWAYS AS (...) VIRTUAL` | Zero disk cost, computed on read           |
| Temporal uniqueness   | `EXCLUDE USING gist`                | Prevent overlapping ranges natively        |
| NOT VALID constraints | `ADD CONSTRAINT ... NOT VALID`      | Add constraints without table locks        |
| TypedSQL              | `prisma.$queryRawTyped()`           | Type-safe raw SQL via `.sql` files         |
| Relation emulation    | `relationMode = "prisma"`           | Integrity in FK-less environments          |
| Soft deletes          | Prisma Extensions `$extends`        | Cross-cutting concern via middleware       |
| RLS standard          | `auth.uid() = user_id`              | Default own-data access policy             |
| Team RLS              | `EXISTS` subquery                   | Permission checks via join tables          |
| Column-level security | PostgreSQL Views                    | Hide sensitive columns from public APIs    |

## Synchronization Protocol

Every schema modification MUST follow these steps:

1. **Type-to-DB Verification**: When adding an enum or union in TS, verify the equivalent CHECK constraint in SQL
2. **Migration-First Generation**: Generate SQL migrations using `prisma migrate dev --create-only` BEFORE applying
3. **Naming Alignment**: Enforce snake_case in SQL and camelCase in TS via explicit mappings
4. **Integrity Audit**: Run `prisma validate` and check for missing indices on relation scalars

## Common Mistakes

| Mistake                                                  | Correct Pattern                                                                       |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Running SQL changes manually without migrations          | Generate numbered migrations with `prisma migrate dev --create-only` before applying  |
| Using auto-increment or raw IDs exposed in URLs          | Use native UUIDv7 for globally unique, non-enumerable identifiers                     |
| Skipping CHECK constraints on enums or unions            | Add database-level CHECK constraints that mirror TypeScript types                     |
| Mixing snake_case and camelCase without explicit mapping | Use `@map` and `@@map` to enforce snake_case in SQL and camelCase in TypeScript       |
| Tables without Row-Level Security policies               | Apply RLS policies to every table, defaulting to `auth.uid() = user_id`               |
| DROP or RENAME column in a single deployment             | Use expand-and-contract: add new column, dual-write, backfill, switch reads, drop old |
| Adding NOT NULL to large tables with full lock           | Add column as NULL first, backfill, then add NOT NULL with NOT VALID                  |
| Creating indices without CONCURRENTLY                    | Use `CREATE INDEX CONCURRENTLY` in raw SQL migrations to avoid table locks            |

## Delegation

- **Audit existing schema for missing constraints or indices**: Use `Explore` agent
- **Plan a zero-downtime migration strategy for production databases**: Use `Plan` agent
- **Execute a full schema refactor with type alignment and RLS setup**: Use `Task` agent

## References

- [PostgreSQL integrity patterns, UUIDv7, virtual columns, and temporal constraints](references/postgres-integrity.md)
- [Prisma architecture, TypedSQL, extensions, and edge-first patterns](references/prisma-architecture.md)
- [Migration safety protocols, destructive changes, and rollback strategies](references/migration-safety.md)
- [Row-Level Security, column-level security, and audit logging](references/rls-security.md)
