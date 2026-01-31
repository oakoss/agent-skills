---
title: Deployment Patterns
description: Jamstack, serverless, traditional full-stack, and microservices deployment architectures with tradeoffs
tags:
  [
    jamstack,
    serverless,
    microservices,
    full-stack,
    deployment,
    architecture,
    blue-green,
    canary,
  ]
---

# Deployment Patterns

## Jamstack (Static + API)

```text
Frontend (Vercel/Netlify) -> API (Railway/Render) -> Database (Supabase/Neon)
```

**Characteristics**: Static frontend served from CDN, API calls to separate backend, database hosted independently.

**Strengths**: Fast global delivery, cheap at low scale, scales frontend independently, strong caching story.

**Weaknesses**: Not ideal for real-time or server-heavy apps, API latency from separate services, more moving parts than monolith.

**Best for**: Marketing sites, blogs, documentation, e-commerce storefronts, dashboards with moderate data requirements.

## Serverless

```text
Frontend (Vercel/Cloudflare Pages) -> Edge Functions -> Serverless DB (Neon/PlanetScale)
```

**Characteristics**: Zero server management, functions execute on demand, pay-per-invocation pricing.

**Strengths**: Zero idle cost, automatic scaling, no infrastructure management, global edge execution.

**Weaknesses**: Cold start latency (mitigated by edge runtimes), vendor lock-in risk, limited execution time, debugging complexity.

**Best for**: APIs with variable traffic, webhook handlers, scheduled jobs, applications with unpredictable load patterns.

## Traditional Full-Stack

```text
Railway/Render: Node.js API + PostgreSQL + Redis
```

**Characteristics**: Application server, database, and cache co-located on a single platform. Persistent processes.

**Strengths**: Simple mental model, everything in one place, persistent connections (WebSockets, long-polling), predictable pricing.

**Weaknesses**: Single point of failure, vertical scaling limits, platform coupling.

**Best for**: MVPs, internal tools, applications requiring WebSockets, projects where simplicity outweighs scale requirements.

## Microservices

```text
Frontend (Vercel) -> Service 1 (Cloud Run) -> Database
                  -> Service 2 (Cloud Run) -> Queue
                  -> Service 3 (Cloud Run) -> Cache
```

**Characteristics**: Independent services with separate deployments, scaling, and data stores. Service-to-service communication via HTTP/gRPC or message queues.

**Strengths**: Independent scaling, fault isolation, technology flexibility per service, team autonomy.

**Weaknesses**: Higher complexity, distributed system challenges (consistency, latency, debugging), operational overhead.

**Best for**: Large teams, high-scale applications, systems requiring independent scaling per component, organizations with strong DevOps practices.

## Release Strategies

### Rolling Deploy

Gradually replaces old instances with new ones. Zero downtime but no instant rollback. Suitable for most applications.

### Blue-Green Deployment

Maintains two identical environments. Traffic switches from blue (current) to green (new) atomically. Instant rollback by switching back. Requires double infrastructure during deployment.

```text
Load Balancer
  ├── Blue (current, serving traffic)
  └── Green (new, idle until switch)
```

### Canary Release

Routes a small percentage of traffic to the new version. Monitors error rates and performance. Gradually increases traffic if metrics are healthy. Rolls back immediately if problems detected.

```text
Load Balancer
  ├── 95% -> Stable version
  └── 5%  -> Canary version (monitored)
```

### Feature Flags

Decouples deployment from release. Code ships to production but features activate based on flag configuration. Enables gradual rollout, A/B testing, and instant kill switches.

## Environment Strategy

### Three-Environment Model

| Environment | Purpose                              | Deploy Trigger                    |
| ----------- | ------------------------------------ | --------------------------------- |
| Development | Integration testing, feature preview | Push to feature branch            |
| Staging     | Pre-production validation, QA        | Merge to staging branch or manual |
| Production  | Live users                           | Merge to main with approval       |

### Environment Protection Rules

Configure environment protection in the deployment platform or CI system:

- Required reviewers for production deploys
- Wait timers between staging and production
- Branch restrictions (only main can deploy to production)
- Deployment concurrency limits to prevent overlapping deploys

## Rollback Strategy

Every production deployment must have a rollback plan defined before deploy.

**Managed platforms** (Vercel, Netlify, Railway): Use built-in instant rollback to previous deployment.

**Container-based** (ECS, Cloud Run, Kubernetes): Redeploy previous container image tag.

**Database migrations**: Write forward-compatible migrations that work with both old and new application versions. Avoid destructive migrations (dropping columns) until the old version is fully decommissioned.

## Security in Deployments

**Must-haves**:

- HTTPS everywhere (automatic on most managed platforms)
- Environment variables for secrets (never commit to repository)
- Database encryption at rest
- Regular dependency updates (automated with Dependabot or Renovate)
- Rate limiting on public APIs

**Recommended**:

- Security headers (CSP, HSTS, X-Frame-Options)
- DDoS protection (Cloudflare, AWS Shield)
- Automated vulnerability scanning in CI pipeline
- Audit logs for sensitive operations
- Backup and disaster recovery plan with tested restore procedures
