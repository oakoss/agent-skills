---
title: Monitoring and Alerting
description: APM tools comparison, custom response time and query monitoring middleware, performance dashboards, and alerting thresholds
tags:
  [monitoring, alerting, apm, sentry, datadog, new-relic, dashboards, metrics]
---

# Monitoring and Alerting

## APM Tools

| Tool             | Strength                     |
| ---------------- | ---------------------------- |
| Sentry           | Error tracking + performance |
| New Relic        | Full-stack APM               |
| Datadog          | Infrastructure + APM         |
| Vercel Analytics | Next.js optimized            |

## Custom Monitoring

```typescript
// Track response times
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;

    // Log to monitoring service
    metrics.recordResponseTime(req.path, duration);

    // Alert on slow requests
    if (duration > 1000) {
      logger.warn(`Slow request: ${req.path} took ${duration}ms`);
    }
  });

  next();
});

// Track database query times
db.on('query', (query, duration) => {
  if (duration > 100) {
    logger.warn(`Slow query: ${query} took ${duration}ms`);
  }
});
```

## Performance Dashboards

```yaml
Key Metrics to Track:
  - Response time (P50, P95, P99)
  - Throughput (requests/second)
  - Error rate (%)
  - Database query times
  - Cache hit ratio
  - Memory usage
  - CPU usage

Alerting Thresholds:
  - P95 response time > 1s
  - Error rate > 1%
  - Cache hit ratio < 80%
  - Memory usage > 80%
```
