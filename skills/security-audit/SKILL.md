---
name: security-audit
description: 'Senior Data Security Architect and Forensic Auditor. Specialized in Row Level Security (RLS) enforcement, Zero-Trust database architecture, STRIDE threat modeling, OWASP Top 10 review, compliance validation, and automated data access auditing. Use when auditing database access policies, implementing RLS in Supabase or Postgres, configuring Convex auth guards, setting up JIT access controls, building forensic audit trails, conducting threat modeling, reviewing code for vulnerabilities, or validating regulatory compliance.'
---

# Security Audit

Senior Data Security Architect and Forensic Auditor. Specialized in Row Level Security (RLS) enforcement, Zero-Trust database architecture, and automated data access auditing. Covers threat modeling, secure coding review, compliance validation, and forensic trace analysis.

## Quick Reference

| Need                 | Approach                                                |
| -------------------- | ------------------------------------------------------- |
| RLS enforcement      | Enable on every public table; index columns in policies |
| Zero-Trust DB        | Micro-segmentation, identity propagation, TLS 1.3       |
| Auth validation      | Explicit checks at DB/API layer, never frontend only    |
| JIT access           | Time-bound grants that expire automatically             |
| Audit trails         | Database triggers with immutable audit_log table        |
| Threat modeling      | STRIDE methodology at every trust boundary              |
| Code security review | OWASP Top 10 checklist                                  |
| Compliance           | GDPR, HIPAA, SOC2, PCI-DSS framework validation         |

## Audit Protocol

1. **Attack Surface Mapping**: Identify all entry points to the data layer (public APIs, internal dashboards, AI agents)
2. **Policy Audit**: Review existing RLS policies or function permissions for logical bypasses
3. **Access Simulation**: Execute shadow access simulations to verify unauthenticated/unauthorized users cannot retrieve sensitive rows
4. **Threat Model**: Apply STRIDE to every trust boundary
5. **Compliance Check**: Validate against applicable regulatory frameworks

## Security Principles

| Principle         | Description                                             |
| ----------------- | ------------------------------------------------------- |
| Defense in Depth  | Multiple layers; if one fails, others still protect     |
| Least Privilege   | Minimum permissions needed for the specific operation   |
| Zero Trust        | Never trust, always verify; even internal networks      |
| Secure by Default | Default configuration is secure; opt-in to less secure  |
| Fail Securely     | Access denied on error, not granted; no detail exposure |
| Assume Breach     | Design assuming an attacker already has a valid JWT     |

## Anti-Patterns

| Anti-Pattern                                | Risk                                  |
| ------------------------------------------- | ------------------------------------- |
| Security by obscurity (UUIDs only)          | Attackers enumerate IDs               |
| Anon role with SELECT on sensitive tables   | Public data exposure                  |
| RLS columns without indexes                 | Production performance degradation    |
| Frontend-only permission checks             | Attackers bypass via direct API calls |
| Standing admin privileges                   | Excessive blast radius if compromised |
| service_role key in client-side code        | Bypasses all RLS policies             |
| Generic error messages leaking stack traces | Information disclosure to attackers   |

## Common Mistakes

| Mistake                                                             | Correct Pattern                                                                         |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Relying on UUIDs as the only access control (security by obscurity) | Enforce RLS policies and explicit auth checks alongside unique identifiers              |
| Leaving the anon role with SELECT permissions on sensitive tables   | Restrict anon access; require authenticated roles for sensitive data                    |
| Using `auth.uid() = user_id` in RLS without an index on user_id     | Add indexes on columns used in RLS policies to avoid production performance degradation |
| Performing permission checks only in the frontend                   | Enforce authorization at the database and API layer; attackers bypass frontends         |
| Using standing admin privileges for routine operations              | Implement JIT (Just-in-Time) access grants that expire automatically                    |
| No audit logging for security-relevant events                       | Log authentication attempts, authorization failures, data access with immutable trails  |
| Exposing stack traces in production error responses                 | Log full errors server-side; return generic messages to clients                         |

## Delegation

- **Simulate unauthorized access attempts against RLS policies**: Use `Task` agent to run anonymous queries and verify row-level security enforcement
- **Audit Convex functions for missing auth guards and permission gaps**: Use `Explore` agent to scan all query and mutation handlers for `getUserIdentity` calls
- **Design a zero-trust database architecture with forensic audit trails**: Use `Plan` agent to map access policies, JIT grants, and immutable audit log schema

## References

- [rls-performance.md](references/rls-performance.md) -- RLS policy performance, mandatory indexing, stable functions, benchmarking with EXPLAIN
- [zero-trust-database.md](references/zero-trust-database.md) -- Micro-segmentation, identity propagation, connection security, JIT access controls
- [audit-logging.md](references/audit-logging.md) -- Trigger-based auditing, PGAudit extension, log integrity, tamper-proof storage
- [convex-security.md](references/convex-security.md) -- Identity validation, manual RLS in functions, granular functions, encryption and compliance
- [threat-modeling.md](references/threat-modeling.md) -- STRIDE framework, threat modeling process, risk assessment, mitigation planning
- [application-security.md](references/application-security.md) -- OWASP Top 10, input validation, authentication, authorization, secure configuration
- [compliance-frameworks.md](references/compliance-frameworks.md) -- GDPR, HIPAA, SOC2, PCI-DSS requirements, implementation checklists
