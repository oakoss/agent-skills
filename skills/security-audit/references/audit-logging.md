---
title: Audit Logging
description: Trigger-based auditing in Postgres, PGAudit extension, log integrity, tamper-proof storage, and compliance-ready audit trails
tags: [audit-log, triggers, pgaudit, tamper-proof, compliance, forensics]
---

# Audit Log Implementation

Application-level logs can be bypassed. Database-level auditing (triggers or extensions) captures every change regardless of how it was initiated.

## Trigger-Based Auditing (Postgres)

Create a generic trigger that captures INSERT, UPDATE, and DELETE operations:

```sql
-- Audit log table
CREATE TABLE audit_log (
  id bigserial PRIMARY KEY,
  table_name text NOT NULL,
  action text NOT NULL,
  old_data jsonb,
  new_data jsonb,
  actor_id uuid,
  changed_at timestamptz DEFAULT now()
);

-- Generic trigger function
CREATE OR REPLACE FUNCTION process_audit() RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    INSERT INTO audit_log(table_name, action, old_data, actor_id)
    VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD), auth.uid());
  ELSIF (TG_OP = 'UPDATE') THEN
    INSERT INTO audit_log(table_name, action, old_data, new_data, actor_id)
    VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), auth.uid());
  ELSIF (TG_OP = 'INSERT') THEN
    INSERT INTO audit_log(table_name, action, new_data, actor_id)
    VALUES (TG_TABLE_NAME, 'INSERT', to_jsonb(NEW), auth.uid());
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to sensitive tables
CREATE TRIGGER audit_sensitive_data
AFTER INSERT OR UPDATE OR DELETE ON sensitive_data
FOR EACH ROW EXECUTE FUNCTION process_audit();
```

## PGAudit Extension

For high-compliance environments (HIPAA, SOC2), use the `pgaudit` extension:

- Logs full SQL statements and their parameters
- Supports session-level and object-level auditing
- Can be scoped per database, per role, or globally

```sql
-- Enable pgaudit (requires shared_preload_libraries = 'pgaudit' in postgresql.conf)
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Configure audit logging
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
ALTER SYSTEM SET pgaudit.log_statement_once = on;
ALTER SYSTEM SET pgaudit.log_level = 'log';
```

### PGAudit Log Classes

| Class    | Logged Operations                                |
| -------- | ------------------------------------------------ |
| read     | SELECT and COPY when source is a relation        |
| write    | INSERT, UPDATE, DELETE, TRUNCATE, COPY when dest |
| function | Function calls and DO blocks                     |
| role     | GRANT, REVOKE, CREATE/ALTER/DROP ROLE            |
| ddl      | All DDL not in the role class                    |
| misc     | Miscellaneous (DISCARD, FETCH, CHECKPOINT)       |
| misc_set | Miscellaneous SET commands (e.g., SET role)      |
| all      | All of the above                                 |

### Per-Database or Per-Role Scoping

```sql
-- Audit all writes on a specific database
ALTER DATABASE finance SET pgaudit.log = 'read, write';

-- Audit everything for a specific role
ALTER ROLE auditor SET pgaudit.log = 'all';
```

## Log Integrity

Prevent attackers from deleting audit logs:

| Strategy                | Implementation                                          |
| ----------------------- | ------------------------------------------------------- |
| Separate database       | Store audit logs in a read-only (for app user) database |
| Forward-only logging    | Use append-only service that cannot be modified         |
| No UPDATE/DELETE grants | App user can only INSERT into audit tables              |
| Cryptographic chaining  | Hash each log entry with the previous entry's hash      |

```sql
-- Restrict app user to INSERT only
GRANT INSERT ON audit_log TO app_user;
REVOKE UPDATE, DELETE ON audit_log FROM app_user;

-- Separate schema for audit isolation
CREATE SCHEMA audit;
ALTER TABLE audit_log SET SCHEMA audit;
```

## Application-Level Audit Logging

For events not captured by database triggers:

```ts
interface AuditEvent {
  userId: string;
  action: string;
  resource: string;
  ip: string;
  userAgent: string;
  success: boolean;
  metadata?: Record<string, unknown>;
}

async function auditLog(event: AuditEvent) {
  await db.auditLog.create({
    data: {
      ...event,
      timestamp: new Date(),
    },
  });
}

// Log security-relevant events
await auditLog({
  userId: user.id,
  action: 'LOGIN',
  resource: 'auth',
  ip: req.ip,
  userAgent: req.headers['user-agent'] ?? '',
  success: true,
});
```

## What to Audit

| Event Category         | Examples                                             |
| ---------------------- | ---------------------------------------------------- |
| Authentication         | Login, logout, failed login, password change         |
| Authorization          | Permission denied, role change, privilege escalation |
| Data access            | Sensitive data read, bulk export, API key usage      |
| Data modification      | Create, update, delete on sensitive tables           |
| Configuration changes  | RLS policy change, role assignment, schema change    |
| Administrative actions | User creation, JIT grant, service key usage          |
