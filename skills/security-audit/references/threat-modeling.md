---
title: Threat Modeling
description: STRIDE framework for threat identification, threat modeling process, risk assessment matrix, and mitigation planning
tags: [stride, threat-modeling, risk-assessment, mitigation, trust-boundaries]
---

# Threat Modeling (STRIDE)

## STRIDE Framework

Apply STRIDE at every trust boundary to identify threats systematically.

### S - Spoofing (Authentication)

- **Threat**: Attacker impersonates a user or system
- **Examples**: Stolen credentials, session hijacking, weak authentication
- **Mitigations**: MFA, strong password policies, JWT with short expiration, secure session management

### T - Tampering (Integrity)

- **Threat**: Attacker modifies data or code
- **Examples**: SQL injection, man-in-the-middle attacks, parameter manipulation
- **Mitigations**: Input validation, HTTPS/TLS everywhere, signed tokens, integrity checks (hashing)

### R - Repudiation (Accountability)

- **Threat**: User denies performing an action
- **Examples**: No audit logs, unsigned transactions, anonymous actions
- **Mitigations**: Comprehensive audit logging, digital signatures, immutable log storage

### I - Information Disclosure (Confidentiality)

- **Threat**: Sensitive data exposed to unauthorized parties
- **Examples**: Exposed API keys, database dumps, verbose error messages
- **Mitigations**: Encryption at rest and in transit, least privilege, secure secret management, RBAC

### D - Denial of Service (Availability)

- **Threat**: System becomes unavailable to legitimate users
- **Examples**: DDoS attacks, resource exhaustion, unhandled exceptions
- **Mitigations**: Rate limiting, input validation (reject massive payloads), auto-scaling, CDN/DDoS protection

### E - Elevation of Privilege (Authorization)

- **Threat**: User gains unauthorized access to higher privileges
- **Examples**: Broken access control, IDOR, missing authorization checks
- **Mitigations**: Authorization on every request, least privilege, ABAC, regular permission audits

## Threat Modeling Process

### Step 1: Identify Assets

- User data (PII, passwords, financial info)
- Business data (IP, customer lists, transactions)
- System credentials (API keys, certificates)
- Infrastructure (servers, databases, APIs)

### Step 2: Identify Trust Boundaries

| Boundary                     | Data Crossing                    |
| ---------------------------- | -------------------------------- |
| User <-> Web App             | User input, session tokens       |
| Web App <-> API              | API requests, auth tokens        |
| API <-> Database             | Queries, credentials             |
| Internal <-> External APIs   | API keys, user data              |
| Admin <-> Production systems | Admin credentials, configuration |

### Step 3: Apply STRIDE to Each Boundary

For each boundary, ask:

- **S**: Can an attacker spoof identity?
- **T**: Can data be tampered with?
- **R**: Can actions be repudiated?
- **I**: Can information be disclosed?
- **D**: Can service be denied?
- **E**: Can privileges be elevated?

### Step 4: Assess Risk

```text
Risk = Likelihood x Impact

Likelihood: High (likely), Medium (may occur), Low (unlikely)

Impact:
  Critical - Data breach, financial loss, legal liability
  High     - Significant damage, downtime
  Medium   - Limited damage, temporary disruption
  Low      - Minimal impact

Risk Level:
  Critical - Immediate action required
  High     - Address before launch
  Medium   - Address post-launch
  Low      - Monitor, may accept risk
```

### Step 5: Define Mitigations

For each threat, document:

- Mitigation strategy
- Implementation effort (low, medium, high)
- Residual risk after mitigation
- Owner and timeline
