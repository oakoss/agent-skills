---
title: RLS Performance
description: Row Level Security policy performance optimization, mandatory indexing, stable functions, cross-schema considerations, and benchmarking with EXPLAIN
tags: [rls, performance, indexing, postgres, supabase, stable-functions]
---

# RLS Performance Optimization

Each RLS policy is essentially a hidden `WHERE` clause added to every query. If not optimized, it can turn an O(1) lookup into an O(N) scan.

## Mandatory Indexing

Any column used in a `USING` or `WITH CHECK` clause MUST be indexed.

```sql
-- If policy is auth.uid() = user_id, then user_id needs a B-Tree index
CREATE INDEX idx_sensitive_data_user_id ON sensitive_data(user_id);

-- For team-based access
CREATE INDEX idx_sensitive_data_team_id ON sensitive_data(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
```

## Wrapping in Stable Functions

Postgres can cache the results of `STABLE` functions. Wrap complex subqueries in a function to avoid re-executing them for every row.

```sql
CREATE OR REPLACE FUNCTION check_membership(org_id uuid)
RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM memberships
    WHERE organization_id = org_id AND user_id = auth.uid()
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

## Hardened RLS Policy Example

```sql
-- Enable RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- Team-based access policy
CREATE POLICY user_team_access ON sensitive_data
FOR SELECT
TO authenticated
USING (
  team_id IN (
    SELECT team_id FROM team_members WHERE user_id = auth.uid()
  )
);

-- Never use service_role key for client-side operations
-- It bypasses all RLS policies
```

## Performance Checklist

- [ ] All columns in RLS `USING` clauses are indexed
- [ ] Complex subqueries are wrapped in `STABLE` functions
- [ ] RLS logic stays within the same schema
- [ ] `EXPLAIN ANALYZE` shows Index Scan (not Sequential Scan)
- [ ] Tested with production-scale data volumes
- [ ] `service_role` key is never used client-side
