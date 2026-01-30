---
name: ci-cd
description: CI/CD pipelines, deployment strategy, and infrastructure. Use when setting up GitHub Actions workflows, choosing deployment platforms, configuring production environments, securing pipelines with OIDC, or optimizing build performance.
version: 1.0.0
---

# CI/CD & Deployment

Choose deployment strategy, build hardened pipelines, and ship to production safely.

**Core Principle**: Start simple, scale when needed. Don't over-engineer infrastructure for traffic that hasn't arrived.

## Quick Reference

| Need                      | Solution                                    |
| ------------------------- | ------------------------------------------- |
| MVP deploy (< 1K users)   | Vercel, Netlify, Railway, Cloudflare Pages  |
| Growing product (1K-100K) | AWS Amplify, Cloud Run, Fly.io, Render      |
| Enterprise (100K+)        | AWS ECS/EKS, GKE, DigitalOcean App Platform |
| Static site               | Vercel, Netlify, Cloudflare Pages           |
| Full-stack + DB           | Railway, Render, AWS Amplify                |
| Global low latency        | Cloudflare Workers, Vercel Edge, Fly.io     |
| Compliance (HIPAA, SOC 2) | AWS, GCP, Azure                             |
| Cloud auth from CI        | OIDC roles (never long-lived keys)          |
| Action pinning            | Pin to commit SHA, not tag                  |
| Bun CI caching            | `~/.bun/install/cache` keyed on `bun.lockb` |

## Core Patterns

### GitHub Actions: Hardened Workflow

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Cache Bun Dependencies
        uses: actions/cache@v4
        with:
          path: ~/.bun/install/cache
          key: ${{ runner.os }}-bun-${{ hashFiles('**/bun.lockb') }}
          restore-keys: |
            ${{ runner.os }}-bun-

      - name: Install dependencies
        run: bun install --frozen-lockfile

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::1234567890:role/github-actions-deploy
          aws-region: us-east-1

      - name: Build & Deploy
        run: bun run build && bun run deploy
```

### Zero-Trust OIDC Integration

Long-lived AWS/Azure/GCP keys are banned in production pipelines.

- Use `id-token: write` permission and configure cloud providers with OIDC roles.
- Configure `aws-actions/configure-aws-credentials` (or equivalent) using roles, not secrets.
- Set up trust relationships in your cloud provider's IAM to accept GitHub's OIDC tokens.

### Strict Permission Scoping

- Explicitly define `permissions` at the job level, never rely on defaults.
- Default to `contents: read` and only add `write` where strictly necessary.

### Bun-First CI Optimization

- **Caching**: `actions/cache` v4+ targeting `~/.bun/install/cache`.
- **Lockfile**: Use `bun.lockb` binary format for faster resolution.
- **Testing**: `bun test` for sub-second unit and integration test execution.

### Hardened Runners and Security

- **Ephemeral runners**: For self-hosted, use JIT runners destroyed after one job.
- **Egress control**: Restrict runner network egress to known safe domains (StepSecurity).
- **Action pinning**: Always pin third-party actions to a commit SHA, not a tag or branch.

### Matrix Build with Environment Protection

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20, 22, 24]
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: bun test
```

### Multi-Stage GitHub Actions Pipeline

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun test
      - run: bun run lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: bun run deploy
```

### Enterprise Pipeline Stages

```text
Build -> Test -> Security Scan -> Stage Deploy -> Integration Tests -> Prod Deploy
```

Features at scale: multi-environment (dev/staging/prod), blue-green deployments, canary releases, automated rollbacks, SAST/DAST scanning.

Tools: GitHub Actions, GitLab CI, CircleCI, ArgoCD (GitOps for K8s), Terraform (IaC).

## Deployment Patterns

### Jamstack (Static + API)

```text
Frontend (Vercel) -> API (Railway) -> Database (Supabase)
```

Fast, cheap, scales easily. Not ideal for real-time or server-heavy apps.

### Serverless

```text
Frontend (Vercel) -> Edge Functions (Vercel) -> Serverless DB
```

Zero server management, pay per use. Watch for cold starts and vendor lock-in.

### Traditional Full-Stack

```text
Railway: Node.js API + PostgreSQL + Redis
```

Simple, everything in one place. Single point of failure risk.

### Microservices

```text
Frontend (Vercel) -> Service 1 (Cloud Run) -> Database
                  -> Service 2 (Cloud Run) -> Queue
```

Independent scaling, fault isolation. Higher complexity and cost.

## Decision Framework

**What are you deploying?**

| App Type        | Platforms                            |
| --------------- | ------------------------------------ |
| Static site     | Vercel, Netlify, Cloudflare Pages    |
| React/Vue SPA   | Vercel, Netlify, Cloudflare Pages    |
| Node.js API     | Railway, Render, Fly.io, AWS Amplify |
| Python API      | Railway, Render, Fly.io, Cloud Run   |
| Go/Rust API     | Fly.io, Railway, Cloud Run           |
| Full-stack + DB | Railway, Render, AWS Amplify         |
| Microservices   | Fly.io, Cloud Run, AWS ECS           |

**Database needs?**

| Need             | Options                                   |
| ---------------- | ----------------------------------------- |
| None             | Vercel, Netlify, Cloudflare Pages         |
| PostgreSQL/MySQL | Railway, Render, AWS RDS, Supabase        |
| Redis/caching    | Railway, Render, AWS ElastiCache, Upstash |
| MongoDB          | MongoDB Atlas, Railway, AWS DocumentDB    |

**Geographic distribution?**

- Single region: any platform.
- Global low latency: Cloudflare Workers, Vercel Edge, Fly.io multi-region.

**Special requirements?**

- Compliance (HIPAA, SOC 2, GDPR): AWS, GCP, Azure.
- Long-running jobs (>15 min): Railway, Render Background Workers, AWS ECS.
- WebSockets/real-time: Railway, Render, Fly.io, AWS ECS.
- High compute (video, ML): AWS ECS/EKS, Cloud Run, dedicated GPUs.

## Cost Optimization

**Free tier strategy** ($0-5/month for MVP):

- Vercel free for personal projects
- Supabase 500MB DB, 50K API requests/day
- Railway $5 credit/month
- Cloudflare unlimited bandwidth free

**Production optimization**:

- Cache aggressively (Redis, CDN)
- Optimize images (Next.js Image, Cloudinary)
- Database connection pooling (PgBouncer)
- Monitor and right-size resources
- Spot instances for non-critical workloads

## Security Best Practices

**Must-haves**:

- HTTPS only (automatic on most platforms)
- Environment variables for secrets (never commit)
- Database encryption at rest
- Regular dependency updates
- Rate limiting on APIs

**Recommended**:

- Security headers (helmet.js for Node)
- DDoS protection (Cloudflare)
- Automated vulnerability scanning
- Audit logs for sensitive operations
- Backup and disaster recovery plan

## Monitoring and Observability

| Tier       | Tools                                                 | Cost          |
| ---------- | ----------------------------------------------------- | ------------- |
| Basic      | Platform dashboards, Sentry, UptimeRobot              | $0-26/mo      |
| Enhanced   | New Relic/Datadog APM, LogTail, custom alerts         | $15-100/mo    |
| Enterprise | Full-stack Datadog, OpenTelemetry, Grafana, PagerDuty | $300-1000+/mo |

## Anti-Patterns

1. **DO NOT** use `secrets.AWS_ACCESS_KEY_ID` in workflows. Use OIDC roles.
2. **DO NOT** use outdated action versions (`actions/checkout@v1`). Always use v4+.
3. **DO NOT** leave `permissions` as default (broad). Scope explicitly per job.
4. **DO NOT** run expensive CI on every branch. Use `on.pull_request` filters.
5. **DO NOT** ignore cache keys. Stale caches cause "works in CI but not locally" bugs.
6. **DO NOT** over-engineer infrastructure for traffic that hasn't arrived yet.
7. **DO NOT** skip preview deployments. Every PR should get a preview URL for testing.
8. **DO NOT** commit secrets or environment variables. Use platform secret management.

## Common Mistakes

| Mistake                                                   | Correct Pattern                                                                   |
| --------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Storing long-lived AWS/GCP/Azure keys as GitHub secrets   | Use OIDC roles with `id-token: write` permission for zero-trust cloud auth        |
| Pinning GitHub Actions to tags instead of commit SHAs     | Pin third-party actions to full commit SHA to prevent supply chain attacks        |
| Leaving `permissions` as default (broad) on workflows     | Explicitly scope permissions at the job level; default to `contents: read`        |
| Running full CI on every branch push                      | Use `on.pull_request` filters and path-based triggers to avoid wasted compute     |
| Over-engineering infrastructure before product-market fit | Start with managed platforms (Vercel, Railway); scale to AWS/GKE only when needed |

## Delegation

- **Audit existing CI workflow security and permissions**: Use `Explore` agent to scan workflow YAML files for broad permissions, unpinned actions, and exposed secrets
- **Set up multi-environment deployment pipelines**: Use `Task` agent to create dev/staging/prod workflows with environment protection rules
- **Plan migration from managed platform to containerized infrastructure**: Use `Plan` agent to evaluate current deployment, define migration steps, and select target architecture

## Troubleshooting

**Workflow YAML errors**: Use `act` or dry-run commits to verify syntax and job dependencies before merging.

**OIDC failures**: Verify trust relationship configuration in your cloud provider's IAM. Confirm `id-token: write` permission is set at the job level.

**Cache misses in CI**: Check that cache keys include the correct lockfile hash (`bun.lockb`). Verify cache path matches the package manager's install directory.

**Slow pipelines**: Cache dependencies, use Bun for faster installs and test execution, parallelize independent jobs with matrix builds.

**Deploy rollback**: Have a rollback plan before every production deploy. Use blue-green or canary strategies at scale to reduce blast radius.

## Deployment Checklist

**Pre-launch**: Environment variables configured, database migrations tested, SSL/HTTPS enabled, custom domain connected, error monitoring set up, backup strategy defined.

**Launch day**: Deploy to production, verify all pages load, test critical user flows, check error monitoring dashboard, monitor performance, have rollback plan ready.

**Post-launch**: Monitor logs for errors, check response times, verify analytics tracking, review cost/usage, document issues, plan scaling strategy.
