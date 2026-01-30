---
title: Secure Configuration
description: Security headers (CSP, HSTS, X-Frame-Options), CORS configuration, Express hardening with Helmet, and rate limiting patterns
tags: [security-headers, cors, helmet, rate-limiting, csp, hsts]
---

# Secure Configuration

## Security Headers

```ts
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
