---
title: Database Compliance
description: Database-specific compliance requirements for GDPR, HIPAA, SOC2, and PCI-DSS including data retention, encryption, audit logging, and access controls
tags: [compliance, gdpr, hipaa, soc2, pci-dss, data-retention, database-audit]
---

# Database Compliance

Database-specific compliance requirements and implementation patterns. For general compliance framework overviews and application-level controls, see the `application-security` skill.

## GDPR: Database Requirements

### Right to Erasure Implementation

```sql
-- Cascade delete with audit trail
CREATE OR REPLACE FUNCTION delete_user_data(target_user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Log the deletion request before executing
  INSERT INTO audit.deletion_log (user_id, requested_at)
  VALUES (target_user_id, now());

  -- Delete in dependency order
  DELETE FROM comments WHERE author_id = target_user_id;
  DELETE FROM posts WHERE author_id = target_user_id;
  DELETE FROM sessions WHERE user_id = target_user_id;
  DELETE FROM users WHERE id = target_user_id;
END;
$$;
```

### Data Retention Automation

```sql
-- Automated cleanup of expired data
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Remove sessions older than retention period
  DELETE FROM sessions WHERE expires_at < now();

  -- Anonymize inactive user data past retention period
  UPDATE users
  SET email = 'anonymized-' || id || '@deleted.local',
      name = 'Deleted User',
      anonymized_at = now()
  WHERE last_active_at < now() - interval '3 years'
    AND anonymized_at IS NULL;
END;
$$;
```

### Right to Portability

```sql
-- Export all user data as JSON
CREATE OR REPLACE FUNCTION export_user_data(target_user_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result jsonb;
BEGIN
  SELECT jsonb_build_object(
    'profile', (SELECT to_jsonb(u) FROM users u WHERE id = target_user_id),
    'posts', (SELECT jsonb_agg(to_jsonb(p)) FROM posts p WHERE author_id = target_user_id),
    'comments', (SELECT jsonb_agg(to_jsonb(c)) FROM comments c WHERE author_id = target_user_id)
  ) INTO result;

  INSERT INTO audit.data_exports (user_id, exported_at)
  VALUES (target_user_id, now());

  RETURN result;
END;
$$;
```

## HIPAA: Database Requirements

### PHI Access Controls

```sql
-- Separate schema for PHI
CREATE SCHEMA phi;

-- Strict role-based access
CREATE ROLE phi_reader;
CREATE ROLE phi_writer;

GRANT USAGE ON SCHEMA phi TO phi_reader, phi_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA phi TO phi_reader;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA phi TO phi_writer;

-- RLS on PHI tables
ALTER TABLE phi.patient_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY provider_access ON phi.patient_records
FOR SELECT TO phi_reader
USING (
  provider_id = (select auth.uid())
  OR EXISTS (
    SELECT 1 FROM phi.care_team
    WHERE patient_id = phi.patient_records.patient_id
    AND provider_id = (select auth.uid())
  )
);
```

### PHI Audit Requirements

HIPAA requires logging all access to Protected Health Information:

```sql
-- PHI-specific audit trigger
CREATE OR REPLACE FUNCTION phi.audit_phi_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit.phi_access_log (
    table_name, record_id, action, actor_id, actor_role, accessed_at
  ) VALUES (
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    TG_OP,
    (select auth.uid()),
    current_setting('request.jwt.claims', true)::jsonb ->> 'role',
    now()
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_patient_records
AFTER SELECT OR INSERT OR UPDATE OR DELETE ON phi.patient_records
FOR EACH ROW EXECUTE FUNCTION phi.audit_phi_access();
```

## SOC2: Database Controls

### Trust Service Criteria for Databases

| Criterion       | Database Control                                 |
| --------------- | ------------------------------------------------ |
| Security        | RLS enabled, least privilege roles, TLS enforced |
| Availability    | Automated backups, point-in-time recovery        |
| Processing      | Constraints, triggers for data integrity         |
| Confidentiality | Column encryption, schema segmentation           |
| Privacy         | Data retention automation, access logging        |

### Change Management Evidence

```sql
-- Track schema changes with PGAudit
ALTER SYSTEM SET pgaudit.log = 'ddl';

-- Version database migrations (use a migration tool)
-- Every schema change is a tracked migration with a timestamp
```

## PCI-DSS: Database Requirements

### Cardholder Data Protection

Never store raw cardholder data. Use tokenization via payment processors:

| Data Element     | Storage Allowed | Recommended Approach |
| ---------------- | --------------- | -------------------- |
| Full card number | Encrypted only  | Store Stripe token   |
| CVV/CVC          | Never           | Never store          |
| PIN              | Never           | Never store          |
| Cardholder name  | Yes             | Encrypt at rest      |
| Last 4 digits    | Yes             | Store for display    |

```sql
-- Store only tokenized payment references
CREATE TABLE payment_methods (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id),
  stripe_payment_method_id text NOT NULL,
  last_four text NOT NULL,
  card_brand text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS and audit logging
ALTER TABLE payment_methods ENABLE ROW LEVEL SECURITY;

CREATE POLICY owner_only ON payment_methods
FOR ALL TO authenticated
USING ((select auth.uid()) = user_id);
```

## Cross-Framework Database Checklist

| Control                  | GDPR | HIPAA | SOC2 | PCI-DSS |
| ------------------------ | ---- | ----- | ---- | ------- |
| RLS on all user tables   | Yes  | Yes   | Yes  | Yes     |
| Audit logging (triggers) | Yes  | Yes   | Yes  | Yes     |
| Encryption at rest       | Yes  | Yes   | Yes  | Yes     |
| TLS for connections      | Yes  | Yes   | Yes  | Yes     |
| Data retention policy    | Yes  | Yes   | Yes  | Yes     |
| Backup and recovery      | Yes  | Yes   | Yes  | Yes     |
| Access review process    | Yes  | Yes   | Yes  | Yes     |
| Schema segmentation      | Rec  | Yes   | Rec  | Yes     |
