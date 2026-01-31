---
title: Data Layer Threat Modeling
description: STRIDE applied to database access patterns, trust boundary analysis for data layers, RLS bypass threat identification, and mitigation planning
tags: [stride, threat-modeling, data-layer, rls-bypass, trust-boundaries]
---

# Data Layer Threat Modeling

Apply STRIDE specifically at data layer trust boundaries to identify database-level threats. For general application-level STRIDE coverage, see the `security` skill.

## STRIDE at the Data Layer

### S - Spoofing (Identity at DB Level)

- **Threat**: Attacker forges or reuses JWT to impersonate another user at the database level
- **Data layer examples**: Stolen JWT used with Supabase client, service_role key leaked to client
- **Mitigations**: Short JWT expiry, asymmetric signing (RS256/EdDSA), audience validation, never expose service_role to clients

### T - Tampering (Data Integrity)

- **Threat**: Attacker modifies data through RLS bypass or unprotected mutation
- **Data layer examples**: Missing WITH CHECK on INSERT/UPDATE policies, Convex mutation without ownership check
- **Mitigations**: RLS WITH CHECK on all write operations, ownership validation in Convex handlers, database constraints

### R - Repudiation (Audit Gaps)

- **Threat**: Data modifications occur without attribution
- **Data layer examples**: Direct SQL access without audit triggers, missing actor_id in audit logs
- **Mitigations**: Database-level audit triggers, PGAudit extension, immutable audit schema

### I - Information Disclosure (Data Leakage)

- **Threat**: Unauthorized data access through policy gaps
- **Data layer examples**: Missing RLS on new tables, anon role with SELECT on sensitive tables, verbose Postgres error messages
- **Mitigations**: RLS on every public table, restrict anon access, generic error responses

### D - Denial of Service (Query Performance)

- **Threat**: Malicious queries exploit unoptimized RLS policies
- **Data layer examples**: Sequential scans from missing indexes on RLS columns, complex cross-schema subqueries in policies
- **Mitigations**: Index all RLS columns, wrap auth functions in subselects, EXPLAIN ANALYZE testing

### E - Elevation of Privilege (Permission Escalation)

- **Threat**: User gains access to data outside their authorization scope
- **Data layer examples**: Standing admin privileges, permissive RLS policies combined with OR, Convex function missing role check
- **Mitigations**: JIT access grants, restrictive policies, granular Convex functions with role validation

## Data Layer Trust Boundaries

| Boundary                  | Threats                                | Key Controls                           |
| ------------------------- | -------------------------------------- | -------------------------------------- |
| Client <-> Supabase API   | JWT forgery, service_role exposure     | RLS, auth.uid() validation             |
| Client <-> Convex         | Missing auth guards, IDOR              | getUserIdentity checks, ownership      |
| App server <-> Database   | SQL injection, privilege escalation    | Parameterized queries, least privilege |
| Admin <-> Database        | Standing privileges, unaudited changes | JIT access, audit logging              |
| Public schema <-> Private | Data leakage across schema boundaries  | Schema segmentation, GRANT/REVOKE      |

## RLS Bypass Threat Identification

Common paths attackers use to bypass RLS:

| Bypass Vector               | Detection Method                               |
| --------------------------- | ---------------------------------------------- |
| service_role key in client  | Search client code for service_role references |
| Table without RLS enabled   | Query pg_tables for relrowsecurity = false     |
| Permissive FOR ALL policies | Review policies for overly broad access        |
| Views bypassing RLS         | Check view security_invoker setting            |
| Security definer functions  | Audit functions in exposed schemas             |

```sql
-- Find tables in public schema without RLS enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = false;

-- List all RLS policies and their expressions
SELECT schemaname, tablename, policyname, permissive, cmd, qual
FROM pg_policies
WHERE schemaname = 'public';
```

## Risk Assessment for Data Layer

| Risk                                 | Likelihood | Impact   | Priority      |
| ------------------------------------ | ---------- | -------- | ------------- |
| Missing RLS on public table          | High       | Critical | Immediate     |
| service_role key in client code      | Medium     | Critical | Immediate     |
| Missing indexes on RLS columns       | High       | High     | Before launch |
| No audit logging on sensitive tables | Medium     | High     | Before launch |
| Standing admin privileges            | Medium     | Medium   | Post-launch   |
| Missing WITH CHECK on write policies | Medium     | High     | Before launch |
