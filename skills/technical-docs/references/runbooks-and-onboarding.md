---
title: Runbooks and Onboarding
description: Incident runbook templates with symptoms, diagnosis, resolution, and escalation paths, plus developer onboarding guide patterns
tags:
  [
    runbook,
    onboarding,
    incident-response,
    escalation,
    setup,
    first-contribution,
  ]
---

## Runbooks

Runbooks are for 3 AM incidents. They must be unambiguous, step-by-step, and assume the reader is stressed and unfamiliar with the system.

### Runbook Template

```markdown
# Runbook: Database Connection Pool Exhaustion

## Symptoms

- API responses timing out (>30s)
- Error logs: `PrismaClientKnowledgeBaseError: Timed out waiting for connection`
- Monitoring: Connection pool utilization > 95%

## Severity

High — user-facing degradation

## Diagnosis

1. Check connection pool metrics in Grafana: `Dashboard > DB > Pool`
2. Identify top queries by duration:

` ` `bash
psql -c "SELECT pid, now() - query_start AS duration, query
         FROM pg_stat_activity
         WHERE state = 'active'
         ORDER BY duration DESC
         LIMIT 10;"
` ` `

3. Check for long-running transactions:

` ` `bash
psql -c "SELECT pid, now() - xact_start AS duration
         FROM pg_stat_activity
         WHERE xact_start IS NOT NULL
         ORDER BY duration DESC
         LIMIT 5;"
` ` `

## Resolution

### Step 1: Kill long-running queries (immediate relief)

` ` `bash
psql -c "SELECT pg_terminate_backend(pid)
         FROM pg_stat_activity
         WHERE duration > interval '5 minutes'
         AND state = 'active';"
` ` `

### Step 2: Increase pool size (temporary)

Update the `DATABASE_POOL_SIZE` env var and restart the service:

` ` `bash
kubectl set env deployment/api DATABASE_POOL_SIZE=20
kubectl rollout restart deployment/api
` ` `

### Step 3: Identify root cause

Review recent deployments for new queries or missing indexes.

## Escalation

- **L1**: On-call engineer (this runbook)
- **L2**: Database team (#db-team in Slack)
- **L3**: Infrastructure lead (page via PagerDuty)

## Prevention

- Set connection pool alerts at 80% utilization
- Require `EXPLAIN ANALYZE` for new queries touching large tables
- Add query timeout: `statement_timeout = '30s'`
```

### Key Principles

- **Symptoms first** — start with what the reader is seeing
- **Copy-paste commands** — no pseudocode, no "run the appropriate command"
- **Escalation paths** — who to contact when the runbook does not resolve the issue
- **Prevention section** — turn incidents into improvements

## Onboarding Guide

An onboarding guide reduces the time from "git clone" to "first meaningful contribution."

### Template

```markdown
# Developer Onboarding

## Prerequisites

- Node.js >= 20 (use `nvm install` with the project's `.nvmrc`)
- pnpm >= 9
- Docker (for local database)

## First-Time Setup

` ` `bash
git clone https://github.com/org/repo.git
cd repo
pnpm install
cp .env.example .env.local    # Edit with your local values
pnpm db:setup                 # Start database and run migrations
pnpm dev                      # Start dev server at localhost:3000
` ` `

## Project Structure

` ` `sh
src/
  app/          # Next.js app router pages
  components/   # Shared UI components
  lib/          # Business logic and utilities
  server/       # API routes and server-side code
` ` `

## Key Concepts

- **Feature flags**: Managed via LaunchDarkly. See `src/lib/flags.ts`.
- **Database**: PostgreSQL via Prisma. Schema at `prisma/schema.prisma`.
- **Auth**: NextAuth.js with OAuth providers. Config at `src/lib/auth.ts`.

## Common Tasks

| Task             | Command               |
| ---------------- | --------------------- |
| Run dev server   | `pnpm dev`            |
| Run tests        | `pnpm test`           |
| Run linter       | `pnpm lint`           |
| Generate types   | `pnpm codegen`        |
| Create migration | `pnpm db:migrate:dev` |
| Reset database   | `pnpm db:reset`       |

## Your First Contribution

1. Pick an issue labeled `good-first-issue`
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes and add tests
4. Run `pnpm test && pnpm lint` before committing
5. Open a PR against `main`
```

### Key Principles

- **Test the guide** — have a new team member follow it; fix every stumbling block
- **Keep it current** — outdated setup instructions are worse than none
- **Link, don't duplicate** — reference existing docs rather than copying content
- **Include common tasks** — the commands developers run daily
