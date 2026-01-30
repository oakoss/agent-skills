---
title: Caching Strategies
description: Multi-layer caching architecture, Redis caching patterns with invalidation, HTTP cache headers, and CDN configuration
tags:
  [caching, redis, http-cache, cdn, cache-invalidation, cloudflare, cloudfront]
---

# Caching Strategies

## Multi-Layer Caching

```text
Browser Cache (HTTP headers)
  ↓
CDN Cache (Cloudflare, CloudFront)
  ↓
Application Cache (Redis, Memcached)
  ↓
Database Query Cache
  ↓
Database
```

## Redis Caching

```typescript
import Redis from 'ioredis';

const redis = new Redis({
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
});

async function getUser(id: string): Promise<User> {
  const cacheKey = `user:${id}`;

  // 1. Check cache
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // 2. Cache miss - fetch from database
  const user = await db.users.findById(id);

  // 3. Store in cache (expire in 1 hour)
  await redis.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}

// Cache invalidation
async function updateUser(id: string, data: Partial<User>) {
  await db.users.update(id, data);
  await redis.del(`user:${id}`); // Invalidate cache
}
```

## HTTP Cache Headers

```typescript
// Express middleware
app.use((req, res, next) => {
  // Static assets: cache for 1 year
  if (req.url.match(/\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$/)) {
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
  }

  // HTML: no cache (always revalidate)
  if (req.url.endsWith('.html') || req.url === '/') {
    res.setHeader('Cache-Control', 'no-cache, must-revalidate');
  }

  // API responses: cache for 5 minutes
  if (req.url.startsWith('/api/')) {
    res.setHeader('Cache-Control', 'public, max-age=300');
    res.setHeader('ETag', generateETag(req.url));
  }

  next();
});
```

## CDN Configuration

```yaml
Static Assets to CDN:
  - Images: /images/**
  - JavaScript: /js/**
  - CSS: /css/**
  - Fonts: /fonts/**

CDN Settings:
  - Cache duration: 1 year (with versioned URLs)
  - Gzip/Brotli compression: enabled
  - Image optimization: WebP conversion
  - Purge on deploy: yes (via API)

Recommended CDNs:
  - Cloudflare (free tier excellent)
  - CloudFront (AWS integration)
  - Fastly (enterprise, very fast)
```
