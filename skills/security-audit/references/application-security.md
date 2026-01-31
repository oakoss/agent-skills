---
title: Database Access Security
description: Securing database access patterns, API-to-database authorization, service role management, schema exposure controls, and security definer functions
tags:
  [
    database-access,
    api-security,
    service-role,
    schema-exposure,
    security-definer,
  ]
---

# Database Access Security

Patterns for securing database access from applications. For general OWASP Top 10 coverage and application-level security (XSS, CSRF, headers), see the `security` skill.

## Supabase API Security

### Service Role Key Management

The `service_role` key bypasses all RLS policies. It must never appear in client-side code.

```ts
// BAD: service_role key in browser-accessible code
const supabase = createClient(
  url,
  process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!,
);

// GOOD: anon key for client-side, service_role only in server-side code
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);

// GOOD: service_role only in server functions (API routes, server actions)
const adminClient = createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!);
```

### Anon Role Restrictions

The `anon` role should have minimal permissions. Never grant SELECT on sensitive tables to anon.

```sql
-- Restrict anon access to sensitive tables
REVOKE ALL ON sensitive_data FROM anon;

-- Allow anon read access only to public content
GRANT SELECT ON public_content TO anon;
```

### Schema Exposure Controls

Only schemas listed in Supabase API settings are exposed via PostgREST. Security definer functions in exposed schemas can bypass RLS.

```sql
-- Create utility functions in a non-exposed schema
CREATE SCHEMA private;

CREATE OR REPLACE FUNCTION private.has_role(required_role text)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = (select auth.uid()) AND role = required_role
  );
$$;

-- Use in RLS policy (function bypasses RLS on user_roles table)
CREATE POLICY admin_access ON admin_data
FOR SELECT TO authenticated
USING (private.has_role('admin'));
```

Security definer functions should:

- Live in a non-exposed schema (not `public`)
- Set `search_path = ''` to prevent schema hijacking
- Be marked `STABLE` or `IMMUTABLE` when possible

## Views and RLS

Views bypass RLS by default because they run as the view creator (typically `postgres` with bypass RLS).

```sql
-- BAD: View bypasses RLS (default behavior)
CREATE VIEW user_documents AS
SELECT * FROM documents;

-- GOOD: Postgres 15+ security_invoker forces RLS evaluation
CREATE VIEW user_documents
WITH (security_invoker = true) AS
SELECT * FROM documents;
```

## Convex API Security

### Public Function Exposure

All Convex functions are callable from the internet. Internal functions provide server-to-server isolation.

```ts
import { internalQuery, internalMutation } from './_generated/server';

// Internal function: only callable from other Convex functions
export const getUser = internalQuery({
  args: { userId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query('users')
      .withIndex('by_external_id', (q) => q.eq('externalId', args.userId))
      .unique();
  },
});
```

### External Service Authentication

For external services calling Convex (webhooks, cron jobs), verify a shared secret from environment variables.

```ts
import { httpAction } from './_generated/server';

export const webhook = httpAction(async (ctx, request) => {
  const secret = request.headers.get('x-webhook-secret');
  if (secret !== process.env.WEBHOOK_SECRET) {
    return new Response('Unauthorized', { status: 401 });
  }
  // Process webhook
});
```

## Database Connection Security

| Control            | Implementation                                         |
| ------------------ | ------------------------------------------------------ |
| TLS enforcement    | Require TLS 1.2+ for all database connections          |
| Connection pooling | Use connection poolers (PgBouncer) with per-user creds |
| IP allowlisting    | Restrict direct database access by IP                  |
| Password rotation  | Rotate database credentials on a regular schedule      |
| Read replicas      | Route read-only queries to replicas where possible     |

## Authorization Pattern: Row Ownership

The most common database access pattern is row ownership, where users can only access rows they own.

```sql
-- Standard ownership pattern
CREATE POLICY owner_select ON documents
FOR SELECT TO authenticated
USING ((select auth.uid()) = owner_id);

CREATE POLICY owner_insert ON documents
FOR INSERT TO authenticated
WITH CHECK ((select auth.uid()) = owner_id);

CREATE POLICY owner_update ON documents
FOR UPDATE TO authenticated
USING ((select auth.uid()) = owner_id)
WITH CHECK ((select auth.uid()) = owner_id);

CREATE POLICY owner_delete ON documents
FOR DELETE TO authenticated
USING ((select auth.uid()) = owner_id);
```

## Security Audit Queries

```sql
-- Find functions in exposed schemas that are security definer
SELECT n.nspname, p.proname, p.prosecdef
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public' AND p.prosecdef = true;

-- Check for tables granting access to anon
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'anon' AND table_schema = 'public';
```
