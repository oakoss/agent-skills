---
title: API Security
description: OWASP API Security Top 10 (2023), API authentication patterns, request validation, rate limiting strategies, and API-specific attack prevention
tags:
  [api-security, owasp-api, authentication, rate-limiting, authorization, ssrf]
---

# API Security

## OWASP API Security Top 10 (2023)

Separate from the general OWASP Top 10, this list targets API-specific vulnerabilities.

| #     | Risk                                            | Prevention                                                      |
| ----- | ----------------------------------------------- | --------------------------------------------------------------- |
| API1  | Broken Object Level Authorization               | Verify user owns the resource on every request                  |
| API2  | Broken Authentication                           | Strong auth, token rotation, MFA, brute-force protection        |
| API3  | Broken Object Property Level Authorization      | Allowlist response fields, validate writable properties         |
| API4  | Unrestricted Resource Consumption               | Rate limiting, pagination limits, payload size caps             |
| API5  | Broken Function Level Authorization             | Verify role/permissions for each endpoint, not just auth        |
| API6  | Unrestricted Access to Sensitive Business Flows | Protect critical workflows (checkout, transfer) with CAPTCHA    |
| API7  | Server Side Request Forgery (SSRF)              | Validate and allowlist outbound URLs, block internal networks   |
| API8  | Security Misconfiguration                       | Secure defaults, disable debug, restrict CORS, security headers |
| API9  | Improper Inventory Management                   | Document all endpoints, deprecate old versions, audit exposure  |
| API10 | Unsafe Consumption of APIs                      | Validate data from third-party APIs, enforce timeouts           |

## Object Level Authorization (API1)

The most common API vulnerability. Always verify the requesting user owns or has access to the specific resource.

```ts
app.get('/api/documents/:id', auth, async (req, res) => {
  const doc = await db.document.findFirst({
    where: {
      id: req.params.id,
      userId: req.user.id,
    },
  });

  if (!doc) return res.status(404).json({ error: 'Not found' });
  res.json(doc);
});
```

Never rely on obscure IDs (UUIDs) as access control. Always enforce ownership checks server-side.

## Object Property Level Authorization (API3)

Control which properties users can read and write. Prevent mass assignment and excessive data exposure.

```ts
const UpdateProfileSchema = z.object({
  name: z.string().min(1).max(100),
  bio: z.string().max(500).optional(),
});

app.patch('/api/profile', auth, async (req, res) => {
  const validated = UpdateProfileSchema.parse(req.body);
  await db.user.update({
    where: { id: req.user.id },
    data: validated,
  });
  res.json({ success: true });
});
```

Allowlist fields on both input (writable) and output (readable). Never spread raw request bodies into database operations.

## Rate Limiting Strategies

### Per-User Tiered Limits

```ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

const apiLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:api:' }),
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.id || req.ip,
});

const authLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:auth:' }),
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});

app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
```

### Rate Limit Headers

Always return standard rate limit headers so clients can self-throttle:

```text
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1700000000
Retry-After: 30
```

## SSRF Prevention (API7)

```ts
import { URL } from 'url';
import ipaddr from 'ipaddr.js';

const ALLOWED_PROTOCOLS = ['https:'];
const BLOCKED_RANGES = ['private', 'loopback', 'linkLocal'];

function validateExternalUrl(input: string): URL {
  const url = new URL(input);

  if (!ALLOWED_PROTOCOLS.includes(url.protocol)) {
    throw new Error('Only HTTPS URLs allowed');
  }

  const addr = ipaddr.parse(url.hostname);
  if (BLOCKED_RANGES.some((range) => addr.range() === range)) {
    throw new Error('Internal network access denied');
  }

  return url;
}
```

Never allow user-supplied URLs to reach internal services, metadata endpoints (169.254.169.254), or localhost.

## API Versioning Security

- Deprecate old API versions with sunset headers
- Monitor traffic to deprecated versions for exploitation attempts
- Never leave undocumented endpoints exposed
- Use `API-Version` or URL path versioning consistently

## Security Headers for APIs

```ts
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Frame-Options', 'DENY');
  res.removeHeader('X-Powered-By');
  next();
});
```

APIs should set `Cache-Control: no-store` on sensitive responses to prevent caching of authentication tokens or user data.

## Security Testing Patterns

```ts
describe('API Security', () => {
  test('requires authentication', async () => {
    const res = await fetch('/api/protected');
    expect(res.status).toBe(401);
  });

  test('prevents IDOR', async () => {
    const res = await fetch(`/api/documents/${otherUserDocId}`, {
      headers: { Authorization: `Bearer ${userToken}` },
    });
    expect(res.status).toBe(404);
  });

  test('enforces rate limits', async () => {
    const requests = Array.from({ length: 6 }, () =>
      fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@test.com', password: 'wrong' }),
      }),
    );
    const responses = await Promise.all(requests);
    expect(responses.some((r) => r.status === 429)).toBe(true);
  });

  test('rejects invalid input', async () => {
    const res = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify({ email: 'not-an-email' }),
    });
    expect(res.status).toBe(400);
  });
});
```
