---
title: Monitoring and Compliance
description: Audit logging, error handling patterns, GDPR data subject rights implementation, HIPAA/SOC2/PCI-DSS requirements, security tools, and troubleshooting
tags:
  [
    monitoring,
    audit-logging,
    gdpr,
    hipaa,
    soc2,
    pci-dss,
    compliance,
    troubleshooting,
  ]
---

# Monitoring and Compliance

## Audit Logging

```ts
async function auditLog(event: {
  userId?: string;
  action: string;
  resource: string;
  ip: string;
  userAgent: string;
  success: boolean;
  metadata?: Record<string, unknown>;
}) {
  await db.auditLog.create({ data: { ...event, timestamp: new Date() } });
}
```

## Error Handling

```ts
// BAD: exposes stack trace
res.status(500).json({ error: err.stack });

// GOOD: generic message, log full error server-side
logger.error(err);
res
  .status(500)
  .json({ error: 'Internal server error', requestId: generateRequestId() });
```

## Tools

- **Sentry** — Error tracking, security alerts
- **OWASP ZAP** — Automated web vulnerability scanner
- **Snyk / npm audit** — Dependency vulnerability scanning
- **Datadog / CloudWatch** — APM, anomaly detection

## GDPR (EU Data Subjects)

```ts
// Right to Access (DSAR)
app.get('/api/user/data-export', authMiddleware, async (req, res) => {
  const userId = req.user.id;
  const userData = {
    profile: await db.users.findById(userId),
    projects: await db.projects.findByUser(userId),
    activity: await db.activityLog.findByUser(userId),
  };
  res.setHeader('Content-Disposition', 'attachment; filename=my-data.json');
  res.json(userData);
});

// Right to Erasure
app.delete('/api/user/account', authMiddleware, async (req, res) => {
  const userId = req.user.id;
  await db.users.update(userId, {
    email: `deleted-${userId}@example.com`,
    name: 'Deleted User',
    deleted_at: new Date(),
  });
  await db.sessions.deleteByUser(userId);
  res.json({ message: 'Account deleted successfully' });
});
```

## Troubleshooting

### JWT Token Issues

- **"Token expired"** — Access token TTL too short or clock skew. Use 15min access + 7d refresh. Allow 30s clock skew.
- **"Invalid signature"** — Secret mismatch between services. Ensure all services share the same secret/key pair.
- **"Algorithm mismatch"** — Mixing HS256/RS256. Standardize on RS256 for production.

### CORS Errors

- **"No Access-Control-Allow-Origin"** — Origin not in allowed list. Check exact match including protocol and port.
- **Preflight fails** — Ensure OPTIONS requests are handled and return correct headers.
- **Credentials not sent** — Set `credentials: true` in CORS config and `credentials: 'include'` in fetch.

### Rate Limiting False Positives

- Users behind shared IP (corporate NAT) hit limits. Use user ID + IP for keying when authenticated.
- Load balancer forwarding — ensure `X-Forwarded-For` is trusted and parsed correctly.

### CSP Violations

- **Inline scripts blocked** — Use nonces (`'nonce-xxx'`) instead of `'unsafe-inline'` in production.
- **Third-party scripts blocked** — Add specific domains to `script-src` directive.
- Start with `Content-Security-Policy-Report-Only` to test before enforcing.

### Password Hashing Performance

- bcrypt with 12 rounds takes ~250ms. Intentional for security but can bottleneck high-traffic login endpoints.
- Use async `bcrypt.hash()` to avoid blocking the event loop.
- Consider argon2id for better resistance to GPU attacks.

### Encryption Key Rotation

- Implement envelope encryption: encrypt data with DEK, encrypt DEK with KEK.
- Store key version alongside encrypted data to support decryption during rotation.
- AWS KMS and Google Cloud KMS handle rotation automatically.

### Security Testing

Manual tests before deployment:

1. SQL injection: `' OR '1'='1`
2. XSS: `<script>alert('XSS')</script>`
3. CSRF: Submit form from different origin
4. Path traversal: `../../etc/passwd`
5. Auth bypass: Access protected routes without token
6. IDOR: Change resource IDs in URLs to access other users' data
