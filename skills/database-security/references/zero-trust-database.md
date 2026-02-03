---
title: Zero-Trust Database
description: Micro-segmentation at the data layer, identity propagation, connection security, and Just-in-Time access controls
tags: [zero-trust, micro-segmentation, identity-propagation, jit-access, tls]
---

# Zero-Trust Database Architecture

## Core Principles

1. **Never Trust, Always Verify**: Even if a request comes from your internal web server, verify the end-user's identity at the DB level
2. **Least Privilege**: Grant only the permissions needed for the specific operation
3. **Assume Breach**: Design your DB assuming an attacker already has a valid JWT

## Micro-Segmentation

Divide your database into logical segments with different access controls:

| Schema  | Purpose                       | App User Access                |
| ------- | ----------------------------- | ------------------------------ |
| Public  | Data reachable via API        | Read/write via RLS             |
| Private | Internal data (logs, secrets) | No direct access               |
| Audit   | Tamper-proof logs             | Insert only (no UPDATE/DELETE) |

```sql
-- Create separate schemas
CREATE SCHEMA private;
CREATE SCHEMA audit;

-- Restrict app user access to audit schema
GRANT INSERT ON audit.audit_log TO app_user;
REVOKE UPDATE, DELETE ON audit.audit_log FROM app_user;
```

## Identity Propagation

Pass the full end-user context (ID, role, organization) down to the database level:

### Supabase/Postgres

```sql
-- Access user identity in RLS policies
SELECT auth.uid();                        -- Current user ID (from JWT sub claim)
SELECT auth.jwt();                        -- Full JWT claims as JSON
SELECT auth.jwt() ->> 'role';             -- Extract role from JWT claims
SELECT auth.jwt() -> 'app_metadata';      -- Access app metadata from JWT
```

### Convex

```ts
// Access user identity in function handlers
const identity = await ctx.auth.getUserIdentity();
if (!identity) throw new Error('Unauthenticated');
const userId = identity.subject;
```

## Connection Security

| Control            | Implementation                                   |
| ------------------ | ------------------------------------------------ |
| TLS version        | Force TLS 1.3 for all connections                |
| JWT signing        | Asymmetric signing (RS256/EdDSA), not HS256      |
| Key rotation       | Rotate signing keys on a regular schedule        |
| IP allowlisting    | Restrict administrative connections by IP        |
| Connection pooling | Use connection poolers with per-user credentials |

## Just-in-Time (JIT) Access

Avoid standing privileges for administrative tasks. Implement time-bound access grants:

```sql
-- Grant temporary admin access (expires after task)
CREATE OR REPLACE FUNCTION grant_temp_admin(
  target_user_id uuid,
  duration_minutes integer DEFAULT 60
)
RETURNS void AS $$
BEGIN
  INSERT INTO temp_admin_grants (user_id, expires_at)
  VALUES (target_user_id, now() + (duration_minutes || ' minutes')::interval);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS policy checks temp grants
CREATE POLICY admin_access ON admin_data
FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM temp_admin_grants
    WHERE user_id = auth.uid()
    AND expires_at > now()
  )
);
```

Key rules:

- No standing admin privileges
- All elevated access is time-bound
- Grants are logged in the audit trail
- Expired grants are cleaned up automatically

## Implementation Checklist

- [ ] Schemas segmented (public, private, audit)
- [ ] Identity propagated to database level
- [ ] TLS 1.3 enforced on all connections
- [ ] Asymmetric JWT signing configured
- [ ] IP allowlisting for admin connections
- [ ] JIT access implemented for admin tasks
- [ ] All access patterns audited
