---
title: Application Security
description: OWASP Top 10 review, input validation, SQL injection and XSS prevention, authentication patterns, secure configuration, and security headers
tags:
  [
    owasp,
    xss,
    sql-injection,
    authentication,
    authorization,
    security-headers,
    rate-limiting,
  ]
---

# Application Security

## OWASP Top 10

### A01: Broken Access Control

Users access data or functions they should not.

```ts
// BAD: No authorization check
app.get('/api/users/:id', (req, res) => {
  const user = db.users.findById(req.params.id);
  res.json(user); // Anyone can see any user!
});

// GOOD: Check ownership
app.get('/api/users/:id', authMiddleware, (req, res) => {
  if (req.params.id !== req.user.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const user = db.users.findById(req.params.id);
  res.json(user);
});
```

### A02: Cryptographic Failures

```ts
// BAD: Plaintext password
const user = { email, password: req.body.password };

// GOOD: Hash with bcrypt
import bcrypt from 'bcrypt';
const hashedPassword = await bcrypt.hash(req.body.password, 12);
const user = { email, password: hashedPassword };
```

### A03: Injection (SQL, XSS, Command)

```ts
// BAD: SQL injection
const query = `SELECT * FROM users WHERE email = '${userInput}'`;

// GOOD: Parameterized query
const query = 'SELECT * FROM users WHERE email = ?';
db.query(query, [userInput]);

// GOOD: ORM handles it
const user = await prisma.user.findUnique({
  where: { email: userInput },
});
```

```tsx
// BAD: XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// GOOD: React auto-escapes
<div>{userInput}</div>

// GOOD: Sanitize if HTML is needed
import DOMPurify from 'isomorphic-dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

### A04-A10: Other Critical Issues

| Category                       | Risk                              | Prevention                       |
| ------------------------------ | --------------------------------- | -------------------------------- |
| A04: Insecure Design           | No rate limiting, no threat model | Threat modeling, rate limiting   |
| A05: Security Misconfiguration | Default passwords, stack traces   | Hardened configs, generic errors |
| A06: Vulnerable Components     | Outdated dependencies             | `npm audit`, Dependabot          |
| A07: Auth Failures             | Weak passwords, no MFA            | Strong policies, MFA             |
| A08: Integrity Failures        | Supply chain attacks              | Verify packages, lock files      |
| A09: Logging Failures          | No audit logs                     | Comprehensive logging            |
| A10: SSRF                      | Unvalidated URLs                  | URL allowlisting                 |

## Input Validation with Zod

```ts
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(100),
  age: z.number().int().min(13).max(120),
  website: z.string().url().optional(),
});

const result = UserSchema.safeParse(req.body);
if (!result.success) {
  return res.status(400).json({ errors: result.error.issues });
}
const validData = result.data;
```

## Security Headers

```ts
// Essential security headers
response.headers.set('X-Frame-Options', 'DENY');
response.headers.set('X-Content-Type-Options', 'nosniff');
response.headers.set('X-XSS-Protection', '1; mode=block');
response.headers.set(
  'Content-Security-Policy',
  "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
);
response.headers.set(
  'Strict-Transport-Security',
  'max-age=31536000; includeSubDomains',
);
```

## Rate Limiting

```ts
import rateLimit from 'express-rate-limit';

// Global rate limit
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP',
});
app.use(limiter);

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});
app.post('/api/auth/login', authLimiter, loginHandler);
```

## Secure Error Handling

```ts
// BAD: Exposes internals
catch (error) {
  res.status(500).json({ error: error.message })
}

// GOOD: Generic message with tracking ID
catch (error) {
  console.error('Error:', error)
  res.status(500).json({
    error: 'Internal server error',
    requestId: generateRequestId()
  })
}
```
