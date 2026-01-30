---
title: Threat Modeling
description: STRIDE methodology with detailed threat categories, risk assessment process, trust boundary identification, and mitigation planning
tags:
  [stride, threat-modeling, risk-assessment, trust-boundaries, security-design]
---

# Threat Modeling

Apply STRIDE at each trust boundary (User-App, App-API, API-DB, Internal-External).

## STRIDE Categories

**S - Spoofing (Authentication)**

- Threat: Attacker impersonates a user or system
- Mitigations: MFA, strong password policies, JWT with short expiration, secure session management

**T - Tampering (Integrity)**

- Threat: Attacker modifies data or code
- Mitigations: Input validation, HTTPS/TLS everywhere, signed tokens, integrity checks (hashing)

**R - Repudiation (Accountability)**

- Threat: User denies performing an action
- Mitigations: Comprehensive audit logging, digital signatures, immutable log storage

**I - Information Disclosure (Confidentiality)**

- Threat: Sensitive data exposed to unauthorized parties
- Mitigations: Encryption at rest and in transit, least privilege, secret management (Vault, AWS Secrets Manager), RBAC

**D - Denial of Service (Availability)**

- Threat: System becomes unavailable
- Mitigations: Rate limiting, input validation (reject massive payloads), auto-scaling, CDN/DDoS protection

**E - Elevation of Privilege (Authorization)**

- Threat: User gains unauthorized higher privileges
- Mitigations: Authorization checks on every request, least privilege, ABAC, regular permission audits

## Threat Modeling Process

1. **Identify Assets** — User data, business data, credentials, infrastructure
2. **Identify Trust Boundaries** — User-App, App-API, API-DB, Internal-External, Admin-Production
3. **Apply STRIDE** at each boundary
4. **Assess Risk** — Likelihood (High/Medium/Low) x Impact (Critical/High/Medium/Low)
5. **Define Mitigations** — Strategy, effort, residual risk, owner, timeline
