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

## Audit Logging with Trigger-Based History

PostgreSQL does not have native SQL:2011 system versioning (SYSTEM_TIME periods). Use trigger-based audit logging to maintain a complete history of all changes:

```sql
CREATE TABLE sensitive_data_history (
  history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  changed_by TEXT NOT NULL DEFAULT current_user,
  row_data JSONB NOT NULL
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO sensitive_data_history (operation, row_data)
    VALUES (TG_OP, to_jsonb(OLD));
    RETURN OLD;
  ELSE
    INSERT INTO sensitive_data_history (operation, row_data)
    VALUES (TG_OP, to_jsonb(NEW));
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sensitive_data_audit
AFTER INSERT OR UPDATE OR DELETE ON sensitive_data
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

For Supabase projects, the `database-security` skill covers PGAudit configuration and advanced audit trail patterns in more detail.
