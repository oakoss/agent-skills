---
title: RLS Performance
description: Row Level Security policy performance optimization, mandatory indexing, stable functions, cross-schema considerations, and benchmarking with EXPLAIN
tags: [rls, performance, indexing, postgres, supabase, stable-functions]
---

# RLS Performance Optimization

Each RLS policy is essentially a hidden `WHERE` clause added to every query. If not optimized, it can turn an O(1) lookup into an O(N) scan.

## Mandatory Indexing

Any column used in a `USING` or `WITH CHECK` clause MUST be indexed. Without indexes, RLS adds a sequential scan to every query, causing 100x+ slowdowns on large tables.

```sql
-- If policy is (select auth.uid()) = user_id, then user_id needs a B-Tree index
CREATE INDEX idx_sensitive_data_user_id ON sensitive_data(user_id);

-- For team-based access
CREATE INDEX idx_sensitive_data_team_id ON sensitive_data(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
```

## Wrap auth Functions in SELECT

Supabase recommends wrapping `auth.uid()` and `auth.jwt()` in a subselect. This triggers an `initPlan` optimization that caches the result instead of calling the function per row.

```sql
-- BAD: auth.uid() called per row
CREATE POLICY user_access ON documents
FOR SELECT USING (auth.uid() = user_id);

-- GOOD: Wrapped in select, result cached via initPlan
CREATE POLICY user_access ON documents
FOR SELECT USING ((select auth.uid()) = user_id);
```

This optimization only works when the function result does not depend on row data.

## Wrapping in Stable Functions

Postgres can cache the results of `STABLE` functions. Wrap complex subqueries in a function to avoid re-executing them for every row.

```sql
CREATE OR REPLACE FUNCTION check_membership(org_id uuid)
RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM memberships
    WHERE organization_id = org_id AND user_id = (select auth.uid())
  );
$$ LANGUAGE sql STABLE;

CREATE POLICY member_access ON documents
FOR SELECT USING (check_membership(organization_id));
```

Without the `STABLE` marker, Postgres may re-execute the subquery for each row in the table.

## Avoid Cross-Schema Subqueries

Keep RLS logic within the same schema to minimize planning overhead. Cross-schema joins in RLS policies add query planner complexity and may prevent optimizations.

## Benchmarking with EXPLAIN

Always test RLS policies with real data volumes:

```sql
-- Run with EXPLAIN to check execution plan
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM my_table;
```

What to look for:

| Plan Type       | Status | Action                            |
| --------------- | ------ | --------------------------------- |
| Index Scan      | Good   | RLS policy is using indexes       |
| Sequential Scan | Bad    | Missing index on RLS column       |
| Nested Loop     | Check  | May indicate inefficient subquery |

## Separate Policies per Operation

Supabase recommends creating separate policies for SELECT, INSERT, UPDATE, and DELETE instead of using `FOR ALL`. An UPDATE requires a matching SELECT policy to function correctly.

```sql
-- Enable RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- Separate SELECT policy (team-based access)
CREATE POLICY team_select ON sensitive_data
FOR SELECT
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members WHERE user_id = (select auth.uid())
  )
);

-- Separate INSERT policy
CREATE POLICY team_insert ON sensitive_data
FOR INSERT
TO authenticated
WITH CHECK (
  team_id IN (
    SELECT team_id FROM team_members WHERE user_id = (select auth.uid())
  )
);
```

## Add Explicit Filters in Application Code

RLS policies act as implicit WHERE clauses, but always add explicit filters in application queries too. This helps Postgres build a better query plan.

```sql
-- Even though RLS filters by user_id, add it explicitly
SELECT * FROM documents WHERE user_id = (select auth.uid());
```

## Performance Checklist

- [ ] All columns in RLS `USING` clauses are indexed
- [ ] `auth.uid()` and `auth.jwt()` wrapped in `(select ...)` subselects
- [ ] Complex subqueries are wrapped in `STABLE` functions
- [ ] Separate policies per operation (SELECT, INSERT, UPDATE, DELETE)
- [ ] RLS logic stays within the same schema
- [ ] `EXPLAIN ANALYZE` shows Index Scan (not Sequential Scan)
- [ ] Application queries include explicit filters matching RLS conditions
- [ ] Tested with production-scale data volumes
- [ ] `service_role` key is never used client-side
