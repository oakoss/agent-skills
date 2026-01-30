---
title: Compliance Frameworks
description: GDPR, HIPAA, SOC2, and PCI-DSS regulatory requirements, implementation checklists, and data protection patterns
tags: [compliance, gdpr, hipaa, soc2, pci-dss, data-protection, privacy]
---

# Compliance Frameworks

## GDPR (General Data Protection Regulation)

**Scope**: EU data subjects

### Key Requirements

- Lawful basis for processing (consent, contract, legitimate interest)
- Data subject rights (access, rectification, erasure, portability)
- Privacy by design and default
- Data breach notification (72 hours)
- Data Protection Impact Assessment (DPIA) for high-risk processing

### Implementation Checklist

- [ ] Consent mechanism for data collection
- [ ] Data subject access request (DSAR) process
- [ ] Right to erasure ("right to be forgotten") implementation
- [ ] Data portability export (JSON/CSV)
- [ ] Privacy policy and cookie banner
- [ ] Data Processing Agreement (DPA) with vendors
- [ ] Breach notification process (72-hour window)
- [ ] Data retention policy with automated cleanup

### Technical Implementation

```ts
// Data export endpoint (right to portability)
async function exportUserData(userId: string) {
  const userData = await db.user.findUnique({
    where: { id: userId },
    include: { posts: true, comments: true, settings: true },
  });
  return JSON.stringify(userData, null, 2);
}

// Data deletion endpoint (right to erasure)
async function deleteUserData(userId: string) {
  await db.$transaction([
    db.comment.deleteMany({ where: { authorId: userId } }),
    db.post.deleteMany({ where: { authorId: userId } }),
    db.session.deleteMany({ where: { userId } }),
    db.user.delete({ where: { id: userId } }),
  ]);
  await auditLog({ action: 'USER_DELETION', userId });
}
```

## HIPAA (Health Insurance Portability and Accountability Act)

**Scope**: Healthcare data in the US

### Key Requirements

- Protected Health Information (PHI) must be encrypted at rest and in transit
- Access controls with minimum necessary standard
- Audit logging of all PHI access
- Business Associate Agreements (BAA) with vendors
- Incident response plan for breaches

### Implementation Checklist

- [ ] PHI encrypted at rest (AES-256)
- [ ] PHI encrypted in transit (TLS 1.3)
- [ ] Role-based access controls for PHI
- [ ] Audit logging for all PHI access
- [ ] BAA signed with all vendors handling PHI
- [ ] Employee security training documented
- [ ] Incident response plan tested
- [ ] Regular risk assessments conducted

## SOC2 (Service Organization Control 2)

**Scope**: Service providers storing customer data

### Trust Service Criteria

| Criterion       | Focus                                  |
| --------------- | -------------------------------------- |
| Security        | Protection against unauthorized access |
| Availability    | System availability commitments        |
| Processing      | Complete and accurate data processing  |
| Confidentiality | Protection of confidential information |
| Privacy         | Personal information management        |

### Implementation Checklist

- [ ] Access controls and authentication (MFA)
- [ ] Encryption at rest and in transit
- [ ] Vulnerability management (regular scans)
- [ ] Change management process documented
- [ ] Incident response plan
- [ ] Vendor management program
- [ ] Security awareness training
- [ ] Continuous monitoring and alerting

## PCI-DSS (Payment Card Industry Data Security Standard)

**Scope**: Organizations handling payment card data

### Key Requirements

| Requirement | Description                                     |
| ----------- | ----------------------------------------------- |
| 1-2         | Secure network (firewall, no default passwords) |
| 3-4         | Protect cardholder data (encryption)            |
| 5-6         | Vulnerability management (updates, secure code) |
| 7-9         | Access control (need-to-know, unique IDs)       |
| 10-11       | Monitoring and testing (logging, scans)         |
| 12          | Security policy documentation                   |

### Implementation Checklist

- [ ] Never store CVV, PIN, or magnetic stripe data
- [ ] Encrypt stored card numbers (PAN)
- [ ] Use payment tokenization (Stripe, Braintree)
- [ ] Restrict access to cardholder data
- [ ] Log all access to cardholder data
- [ ] Regular vulnerability scans
- [ ] Annual penetration testing

### Best Practice: Use Payment Processors

Minimize PCI scope by using third-party payment processors:

| Approach         | PCI Scope | Recommendation         |
| ---------------- | --------- | ---------------------- |
| Stripe Elements  | Minimal   | Preferred for web apps |
| Stripe Checkout  | Minimal   | Hosted payment page    |
| Custom card form | Full      | Avoid unless required  |

## Cross-Framework Controls

Controls that satisfy multiple compliance frameworks:

| Control                 | GDPR | HIPAA | SOC2 | PCI-DSS |
| ----------------------- | ---- | ----- | ---- | ------- |
| Encryption at rest      | Yes  | Yes   | Yes  | Yes     |
| Encryption in transit   | Yes  | Yes   | Yes  | Yes     |
| Access controls         | Yes  | Yes   | Yes  | Yes     |
| Audit logging           | Yes  | Yes   | Yes  | Yes     |
| Incident response       | Yes  | Yes   | Yes  | Yes     |
| Vendor management       | Yes  | Yes   | Yes  | Yes     |
| Data retention policies | Yes  | Yes   | Yes  | Yes     |
| Employee training       | Yes  | Yes   | Yes  | Yes     |
