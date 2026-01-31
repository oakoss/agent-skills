---
title: Platform Selection
description: Decision framework for choosing deployment platforms based on app type, database needs, geography, and cost
tags:
  [platform, vercel, railway, cloudflare, aws, gcp, render, fly, cost, database]
---

# Platform Selection

## Decision Framework

### By Application Type

| App Type        | Recommended Platforms                     |
| --------------- | ----------------------------------------- |
| Static site     | Vercel, Netlify, Cloudflare Pages         |
| React/Vue SPA   | Vercel, Netlify, Cloudflare Pages         |
| Node.js API     | Railway, Render, Fly.io, AWS Amplify      |
| Python API      | Railway, Render, Fly.io, Cloud Run        |
| Go/Rust API     | Fly.io, Railway, Cloud Run                |
| Full-stack + DB | Railway, Render, AWS Amplify              |
| Microservices   | Fly.io, Cloud Run, AWS ECS                |
| Edge-first      | Cloudflare Workers, Vercel Edge Functions |

### By Scale

| Scale              | Platforms                                   | Reasoning                                   |
| ------------------ | ------------------------------------------- | ------------------------------------------- |
| MVP (< 1K users)   | Vercel, Netlify, Railway, Cloudflare Pages  | Free tiers, minimal config, fast iteration  |
| Growth (1K-100K)   | AWS Amplify, Cloud Run, Fly.io, Render      | More control, better pricing at scale       |
| Enterprise (100K+) | AWS ECS/EKS, GKE, DigitalOcean App Platform | Full control, compliance, custom networking |

### By Database Needs

| Need               | Options                                           |
| ------------------ | ------------------------------------------------- |
| None               | Vercel, Netlify, Cloudflare Pages                 |
| PostgreSQL/MySQL   | Railway, Render, AWS RDS, Supabase, Neon          |
| Redis/caching      | Railway, Render, AWS ElastiCache, Upstash         |
| MongoDB            | MongoDB Atlas, Railway, AWS DocumentDB            |
| Serverless SQL     | Neon, PlanetScale, Supabase                       |
| Global distributed | CockroachDB, Turso (libSQL), Neon (read replicas) |

### By Geographic Distribution

**Single region**: Any platform works. Choose the region closest to the majority of users.

**Multi-region**: Fly.io (built-in multi-region), Cloudflare Workers (global edge by default), Vercel Edge Functions, AWS multi-region with Route 53.

**Global low latency**: Cloudflare Workers for compute at the edge, combined with a globally distributed database (Turso, Neon read replicas, or CockroachDB).

### By Special Requirements

| Requirement                     | Platforms                                       |
| ------------------------------- | ----------------------------------------------- |
| Compliance (HIPAA, SOC 2, GDPR) | AWS, GCP, Azure                                 |
| Long-running jobs (> 15 min)    | Railway, Render Background Workers, AWS ECS     |
| WebSockets/real-time            | Railway, Render, Fly.io, AWS ECS                |
| High compute (video, ML)        | AWS ECS/EKS, Cloud Run, dedicated GPU instances |
| Air-gapped/on-premises          | Self-hosted Kubernetes, Docker Compose          |

## Cost Optimization

### Free Tier Strategy ($0-5/month for MVP)

| Platform         | Free Tier Highlights                                      |
| ---------------- | --------------------------------------------------------- |
| Vercel           | Free for personal projects, serverless functions included |
| Cloudflare Pages | Unlimited bandwidth, 500 builds/month                     |
| Supabase         | 500 MB database, 50K API requests/day                     |
| Railway          | $5 credit/month                                           |
| Neon             | 0.5 GB storage, autoscaling to zero                       |
| Render           | Free static sites, 750 hours/month for services           |

### Production Cost Optimization

**Caching**: Use Redis or CDN caching aggressively to reduce compute and database load. Cloudflare offers unlimited bandwidth on free tier for cached assets.

**Image optimization**: Use framework-level image optimization (Next.js Image, Nuxt Image) or services like Cloudinary to reduce bandwidth costs.

**Database connection pooling**: Use PgBouncer or built-in pooling (Supabase, Neon) to reduce connection overhead and enable serverless-friendly database access.

**Right-sizing**: Monitor actual resource usage and scale down over-provisioned instances. Most managed platforms provide usage dashboards.

**Spot/preemptible instances**: Use for non-critical workloads (CI runners, batch processing, staging environments) at 60-90% discount.

**Reserved capacity**: For predictable production workloads, reserved instances (AWS) or committed use contracts (GCP) offer significant savings.

## Platform Comparison Notes

### Vercel

Primary strength is frontend deployment with integrated serverless functions. Native support for Next.js, Nuxt, SvelteKit, and other frameworks. Edge Functions run on Cloudflare's network. Generous free tier for personal projects. Costs can increase quickly at scale with serverless function invocations.

### Cloudflare Workers/Pages

Edge-first compute with global distribution by default. V8 isolate model provides fast cold starts (sub-millisecond). Pages for static sites and Workers for compute. D1 (SQLite at the edge) and KV for key-value storage. Strong free tier with unlimited bandwidth.

### Railway

Developer-friendly platform with one-click deploys, built-in databases (PostgreSQL, MySQL, Redis, MongoDB), and simple pricing. Good for full-stack applications. Supports Docker containers. Pricing is usage-based with a $5/month credit on the free tier.

### Fly.io

Built for multi-region deployment. Runs Docker containers on Firecracker microVMs. Good for applications requiring low latency globally. Built-in support for persistent volumes. Pricing based on VM size and region count.

### Render

Similar to Railway with managed databases and automatic deploys from Git. Free static site hosting. Background workers for long-running jobs. Straightforward pricing with clear tiers. Good documentation and onboarding experience.

### AWS/GCP/Azure

Full control over infrastructure. Required for compliance-heavy workloads (HIPAA, SOC 2, FedRAMP). Higher operational complexity. Best suited for teams with dedicated DevOps/platform engineering. Cost optimization requires active management.
