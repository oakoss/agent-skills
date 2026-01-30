---
name: performance-optimizer
description: Optimize application performance and scalability. Use when investigating slow applications, scaling bottlenecks, or improving response times. Covers profiling, caching, database optimization, and frontend performance.
version: 1.0.0
---

# Performance Optimizer

Make applications fast, scalable, and cost-efficient. **Measure first, optimize second.**

## Performance Budgets

| Metric                         | Target  | Category       |
| ------------------------------ | ------- | -------------- |
| Largest Contentful Paint (LCP) | < 2.5s  | Core Web Vital |
| First Input Delay (FID)        | < 100ms | Core Web Vital |
| Cumulative Layout Shift (CLS)  | < 0.1   | Core Web Vital |
| First Contentful Paint (FCP)   | < 1.8s  | Frontend       |
| Time to Interactive (TTI)      | < 3.8s  | Frontend       |
| Total Blocking Time (TBT)      | < 200ms | Frontend       |
| API Response Time (P95)        | < 500ms | Backend        |
| Database Query Time (P95)      | < 100ms | Database       |
| Server Response Time (TTFB)    | < 600ms | Backend        |

## Optimization Phases

| Phase         | Focus                         | Key Action                                       |
| ------------- | ----------------------------- | ------------------------------------------------ |
| 1. Profiling  | Identify real bottlenecks     | Chrome DevTools, React Profiler, EXPLAIN ANALYZE |
| 2. Database   | Eliminate slow queries        | Strategic indexes, fix N+1, connection pooling   |
| 3. Caching    | Reduce redundant work         | Redis, HTTP headers, CDN for static assets       |
| 4. Frontend   | Reduce bundle and render time | Code splitting, lazy loading, image optimization |
| 5. Backend    | Speed up API responses        | Background queues, compression, pagination       |
| 6. Monitoring | Sustain performance           | APM tools, alerting thresholds, dashboards       |

## Caching Layers

| Layer         | Scope                  | Duration                                          |
| ------------- | ---------------------- | ------------------------------------------------- |
| Browser Cache | HTTP headers           | Static assets: 1 year (immutable); HTML: no-cache |
| CDN           | Cloudflare, CloudFront | Same as browser, purge on deploy                  |
| Application   | Redis, Memcached       | Varies (e.g., 1 hour for user data)               |
| Database      | Query cache            | Automatic                                         |

## Common Anti-Patterns

| Anti-Pattern                   | Fix                                            |
| ------------------------------ | ---------------------------------------------- |
| SELECT \* on large tables      | Select only needed columns                     |
| N+1 queries                    | Eager loading or DataLoader batching           |
| Functions in WHERE clause      | Store normalized values, use generated columns |
| Loading everything upfront     | Code splitting + lazy loading                  |
| Synchronous heavy operations   | Background job queues (Bull, BullMQ)           |
| No cache invalidation strategy | Invalidate on write, use TTL                   |
| `import _ from 'lodash'`       | `import debounce from 'lodash/debounce'`       |

## Optimization Checklists

| Area           | Key Checks                                                                                         |
| -------------- | -------------------------------------------------------------------------------------------------- |
| Frontend       | Lighthouse >90, bundle <200KB initial, images WebP + lazy, code splitting, critical CSS inlined    |
| Backend        | P95 <500ms, queries indexed, N+1 eliminated, pooling enabled, async background jobs, rate limiting |
| Database       | Slow query log on, all queries <100ms P95, indexes on FKs and WHERE/ORDER BY, EXPLAIN reviewed     |
| Caching        | Redis configured, CDN for static, HTTP cache headers, hit ratio >80%, invalidation strategy        |
| Infrastructure | Auto-scaling, load balancer healthy, monitoring active, centralized logs                           |

## Common Mistakes

| Mistake                                                      | Correct Pattern                                                                                    |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Optimizing before profiling                                  | Measure first with Chrome DevTools, EXPLAIN ANALYZE, or APM tools to find real bottlenecks         |
| Adding indexes on every column                               | Use strategic indexes on columns in WHERE, ORDER BY, and JOIN clauses; monitor with slow query log |
| Caching without an invalidation strategy                     | Define TTL and invalidate-on-write policies; stale cache is worse than no cache                    |
| Loading entire libraries for a single utility                | Use direct imports (e.g., `import debounce from 'lodash/debounce'`) and tree-shake                 |
| Running heavy computations synchronously in request handlers | Offload to background job queues (Bull, BullMQ) and return immediately                             |

## Delegation

When working on performance optimization, delegate to:

- `frontend-builder` — React-specific performance patterns
- `security` — Rate limiting and DDoS protection
- `ci-cd` — Build pipeline optimization

## References

- [Profiling and Measurement](references/profiling.md) — Chrome DevTools, React Profiler, Node.js/Python profiling, database EXPLAIN
- [Database Optimization](references/database.md) — Strategic indexes, N+1 fixes, query optimization, connection pooling
- [Caching Strategies](references/caching.md) — Redis patterns, HTTP cache headers, CDN configuration
- [Frontend Performance](references/frontend.md) — Code splitting, image optimization, bundle size, React performance
- [Backend Performance](references/backend.md) — Background queues, API response optimization, rate limiting
- [Monitoring and Alerting](references/monitoring.md) — APM tools, custom monitoring, dashboards, alert thresholds
