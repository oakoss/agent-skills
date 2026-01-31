---
title: Secure Configuration
description: Security headers (CSP with nonces, HSTS, Permissions-Policy), CORS configuration, Express hardening with Helmet, and rate limiting patterns
tags:
  [security-headers, cors, helmet, rate-limiting, csp, hsts, permissions-policy]
---

# Secure Configuration

## Security Headers

```ts
import crypto from 'crypto';

const nonce = crypto.randomBytes(16).toString('base64');

response.headers.set('X-Content-Type-Options', 'nosniff');
response.headers.set(
  'Content-Security-Policy',
  `default-src 'self'; script-src 'self' 'nonce-${nonce}'; style-src 'self' 'nonce-${nonce}'; frame-ancestors 'none'`,
);
response.headers.set(
  'Strict-Transport-Security',
  'max-age=63072000; includeSubDomains; preload',
);
response.headers.set(
  'Permissions-Policy',
  'camera=(), microphone=(), geolocation=(), payment=()',
);
```

**Header notes:**

- **X-XSS-Protection** — Deprecated. Remove or set to `0`. Use CSP instead.
- **X-Frame-Options** — Legacy. Use CSP `frame-ancestors 'none'` instead (more granular control).
- **CSP nonces** — Preferred over `'unsafe-inline'` for script/style sources. Generate a unique nonce per response.
- **Permissions-Policy** — Restricts browser features (camera, microphone, geolocation). Replaces the deprecated Feature-Policy header.
- **HSTS preload** — Add `preload` directive and submit to the HSTS preload list for maximum protection.

## CORS Configuration

```ts
app.use(
  cors({
    origin:
      process.env.NODE_ENV === 'production'
        ? 'https://yourdomain.com'
        : 'http://localhost:3000',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  }),
);
```

## Express Hardening

```ts
import helmet from 'helmet';

app.use(helmet());
app.use(express.json({ limit: '10mb' }));
```

## Rate Limiting

```ts
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP',
});
app.use(limiter);

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});
app.post('/api/auth/login', authLimiter, loginHandler);
```
