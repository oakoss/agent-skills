---
title: RLS and Security
description: Row-Level Security policies, column-level security via views, security definer vs invoker, and temporal audit logging
tags:
  [
    rls,
    row-level-security,
    column-level-security,
    audit-logging,
    postgresql-views,
  ]
---

# RLS and Security

## Enabling RLS

Every table in a Supabase or Neon project MUST have RLS enabled:

```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
```

## Standard Policy Patterns

### Own-Data Access

The default policy for personal data:

```sql
CREATE POLICY "Users can manage their own projects"
ON projects
FOR ALL
USING (auth.uid() = user_id);
```

### Team-Based Access

Use EXISTS subqueries for permission checks via join tables:

```sql
CREATE POLICY "Team members can view shared data"
ON team_data
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM team_members
    WHERE team_members.team_id = team_data.team_id
    AND team_members.user_id = auth.uid()
  )
);
```

## Security Definers vs Security Invokers

- **Definer**: Function runs with the owner's privileges. Use sparingly and only for trusted administrative operations.
- **Invoker**: Function runs with the caller's privileges. Recommended for API integration where RLS should still apply.

## Column-Level Security (CLS)

Use PostgreSQL Views to hide sensitive columns from public APIs:

```sql
CREATE VIEW public_user_profiles AS
SELECT id, name, avatar_url
FROM users
WHERE is_public = true;
```

This prevents exposure of password hashes, internal IDs, or other sensitive fields through the public-facing API layer.

## Audit Logging with Temporal History

Use the native PostgreSQL system versioning pattern to maintain a complete history of all changes:

```sql
ALTER TABLE sensitive_data
  ADD COLUMN valid_from TIMESTAMPTZ GENERATED ALWAYS AS ROW START;
ALTER TABLE sensitive_data
  ADD COLUMN valid_to TIMESTAMPTZ GENERATED ALWAYS AS ROW END;
ALTER TABLE sensitive_data
  ADD PERIOD FOR SYSTEM_TIME (valid_from, valid_to);
ALTER TABLE sensitive_data
  SET (system_versioning = ON);
```
