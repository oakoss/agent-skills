---
title: Summarization Patterns
description: Executive summaries, PR descriptions, code change summaries, meeting notes, release notes, technical briefs, and progressive disclosure
tags:
  [
    executive-summary,
    pr-description,
    code-review,
    meeting-notes,
    release-notes,
    technical-brief,
    progressive-disclosure,
    inverted-pyramid,
  ]
---

# Summarization Patterns

## Executive Summary (Inverted Pyramid)

Lead with the conclusion. Supporting evidence follows. Details come last. The reader should be able to stop reading at any point and still have the most important information.

### Structure

1. **Recommendation / conclusion** (1-2 sentences)
2. **Key supporting evidence** (3-5 bullet points)
3. **Context and details** (1-2 paragraphs, optional)

### Template

```markdown
## Executive Summary

**Recommendation:** Migrate from REST to GraphQL for the mobile API to reduce
payload sizes by 60% and eliminate the over-fetching that causes slow load times
on 3G connections.

**Key findings:**

- Mobile API responses average 45KB; GraphQL queries reduce this to 18KB
- 73% of REST endpoints return fields the mobile app never uses
- Competitor apps using GraphQL report 40% faster perceived load times
- Migration can be incremental: GraphQL gateway wraps existing REST services

**Timeline:** 6 weeks for core endpoints, 12 weeks for full migration.
See the [technical brief](#) for architecture details.
```

### When to Use

- Presenting decisions to leadership
- Summarizing research or investigation results
- Opening a long document that needs a quick takeaway

## PR Description

Reviewers decide whether to deep-dive based on the PR description. A good description reduces review cycles and catches design issues early.

### Template

```markdown
## What changed

One-paragraph summary of the change and its purpose. Lead with WHY,
not WHAT.

## Why

- Link to issue or context: closes #123
- Business or technical motivation

## Changes

- `src/auth/`: Added rate limiting to login endpoint (max 5 attempts/min)
- `src/middleware/`: New `rateLimiter` middleware using sliding window
- `tests/auth/`: Added rate limit integration tests

## How to test

1. Start the dev server: `pnpm dev`
2. Attempt 6 rapid login requests
3. Verify the 6th request returns 429

## Screenshots

(If UI changes — before/after screenshots or screen recordings)

## Notes for reviewers

- The sliding window algorithm is in `src/middleware/rate-limiter.ts`
- I considered token bucket but sliding window better fits our use case
```

### Key Principles

- **Title under 70 characters** — scanned in PR lists
- **First paragraph answers "why"** — not "what files I touched"
- **Changed files with context** — a file list without explanation is noise
- **Test instructions** — concrete steps, not "run tests"

## Code Change Summary

Summarize a set of code changes for review, handoff, or status updates.

### Template

```markdown
## Summary

Added request rate limiting to protect the login endpoint from brute force
attacks. This addresses the security audit finding SA-042.

## Files changed (5)

| File                             | Change                               |
| -------------------------------- | ------------------------------------ |
| `src/middleware/rate-limiter.ts` | New sliding window rate limiter      |
| `src/auth/login.ts`              | Applied rate limiter middleware      |
| `src/config/security.ts`         | Added rate limit configuration       |
| `tests/auth/login.test.ts`       | Rate limit integration tests         |
| `docs/api/auth.md`               | Documented rate limit error response |

## Key decisions

- Sliding window over token bucket: smoother rate distribution, simpler state
- Per-IP limiting with user override: authenticated users get higher limits
- Redis-backed counters: consistent across multiple server instances

## Impact areas

- **Login endpoint**: Now returns 429 after threshold
- **Monitoring**: New `auth.rate_limited` metric emitted
- **Docs**: API error reference updated
```

### Focus Areas

- **Intent over implementation** — explain decisions, not line numbers
- **Impact over changes** — what does this mean for users, tests, monitoring
- **Table format for files** — scannable at a glance

## Meeting Notes

Meeting notes capture outcomes, not discussions. If the note does not contain decisions or action items, the meeting may not have needed to happen.

### Template

```markdown
## Auth System Design Review — 2025-03-15

**Attendees:** Alice, Bob, Carol

## Decisions

1. Use JWT with short-lived access tokens (15 min) and refresh tokens (7 days)
2. Store refresh tokens in Redis, not the database
3. Implement token rotation: each refresh generates a new refresh token

## Action Items

| Action                              | Owner | Due        |
| ----------------------------------- | ----- | ---------- |
| Draft JWT middleware implementation | Alice | 2025-03-20 |
| Set up Redis cluster for tokens     | Bob   | 2025-03-18 |
| Write token rotation security tests | Carol | 2025-03-22 |

## Open Questions

- Should we support device-bound tokens for mobile? (Alice to research)
- What is the maximum concurrent session count per user? (Product to decide)
```

### Key Principles

- **Decisions are numbered** — easy to reference later
- **Action items have owners and dates** — no owner means no accountability
- **Open questions tracked explicitly** — prevents them from being forgotten
- **No transcript** — summarize, do not transcribe

## Release Notes

Release notes are for users. They answer: "What can I do differently after this update?"

### Template

```markdown
## v2.1.0

### Highlights

- **Batch processing**: Process up to 1,000 items in a single API call
  with `client.batchProcess()`, reducing round trips by 10x.

### New Features

- Added `client.batchProcess()` for bulk operations
- Added `retries` option to client configuration (default: 3)

### Improvements

- Default timeout increased from 10s to 30s for large payloads
- Error messages now include the request ID for easier debugging

### Bug Fixes

- Fixed connection timeout not respecting configured `timeout` value
- Fixed retry logic not backing off on 503 responses

### Deprecations

- `client.process()` is deprecated; use `client.batchProcess()` with a
  single-item array instead. Will be removed in v3.0.

---

## v2.0.0

### Breaking Changes

- **`createInstance` renamed to `createClient`** — update all import sites.
  Codemod available: `npx package-name-codemod v2`
- **Minimum Node.js version is now 20** — upgrade before updating
- **CommonJS support dropped** — set `"type": "module"` in `package.json`

### Migration

See the [v1 to v2 migration guide](./docs/migration-v2.md) for step-by-step
instructions.
```

### Key Principles

- **Highlights first** — the one or two things most users care about
- **User language** — "process 1,000 items" not "refactored batch handler"
- **Breaking changes separated** — with migration instructions or links
- **Version and date** — clear version number, release date optional but helpful

## Technical Brief

A technical brief presents a recommendation with enough context to make a decision. One page maximum.

### Template

```markdown
## Technical Brief: API Rate Limiting Strategy

### Problem

The login endpoint has no rate limiting. Security audit SA-042 flagged this
as high severity. Brute force attacks can attempt unlimited passwords.

### Proposed Solution

Implement sliding window rate limiting at the middleware level:

- 5 requests per minute per IP for unauthenticated endpoints
- 60 requests per minute per user for authenticated endpoints
- Redis-backed counters for consistency across server instances

### Alternatives Considered

| Approach       | Pros                    | Cons                           |
| -------------- | ----------------------- | ------------------------------ |
| Token bucket   | Handles bursts well     | More complex state management  |
| Fixed window   | Simple to implement     | Allows burst at window edges   |
| Sliding window | Smooth rate enforcement | Slightly more Redis operations |

### Recommendation

Sliding window. The additional Redis cost is negligible, and it avoids the
burst vulnerability of fixed windows.

### Next Steps

- [ ] Approve this approach (Alice)
- [ ] Implement middleware (Bob, 3 days)
- [ ] Load test at 10x expected traffic (Carol, 1 day)
```

## Progressive Disclosure

Structure content so readers get value at every depth level.

### The Four Levels

| Level    | Length      | Audience            | Content                         |
| -------- | ----------- | ------------------- | ------------------------------- |
| Headline | 1 line      | Everyone            | What happened / what to do      |
| Summary  | 1 paragraph | Most stakeholders   | Key details and impact          |
| Details  | 1 page      | Implementers        | Technical specifics, trade-offs |
| Appendix | Unlimited   | Deep-dive reference | Raw data, full analysis, code   |

### Example: Incident Report

```markdown
<!-- Headline -->

## Database outage resolved — 23 minutes of degraded API responses

<!-- Summary -->

A connection pool exhaustion caused API timeouts from 14:02 to 14:25 UTC.
Root cause was a missing index on the `orders.user_id` column introduced in
yesterday's migration. 0.3% of requests failed. No data loss occurred.

<!-- Details -->

### Timeline

- 14:02 — Alerts fire: API p99 latency > 10s
- 14:05 — On-call identifies connection pool at 100%
- 14:10 — Long-running queries killed; partial recovery
- 14:18 — Missing index identified via `pg_stat_activity`
- 14:22 — Index created: `CREATE INDEX CONCURRENTLY ...`
- 14:25 — All metrics return to normal

### Root Cause

PR #456 added a query filtering orders by `user_id` without an index.
Under load, this caused full table scans holding connections for 30+ seconds.

### Prevention

- Added CI check requiring `EXPLAIN ANALYZE` for new queries on large tables
- Set `statement_timeout = 30s` as database default

<!-- Appendix (linked, not inline) -->

See [full incident report](./incidents/2025-03-15-db-outage.md) for
query plans, Grafana snapshots, and detailed timeline.
```

## Length Guidelines

| Context               | Target Length     | Format                              |
| --------------------- | ----------------- | ----------------------------------- |
| Commit message        | 1 line (50 chars) | Imperative mood                     |
| PR title              | 1 line (70 chars) | What changed                        |
| PR description        | 10-30 lines       | Template above                      |
| Slack status update   | 2-3 sentences     | What, blockers, next                |
| Executive summary     | 5-10 lines        | Conclusion + bullets                |
| Meeting notes         | 0.5-1 page        | Decisions + actions + open items    |
| Technical brief       | 1 page            | Problem + solution + recommendation |
| Release notes (minor) | 10-20 lines       | Features + fixes                    |
| Release notes (major) | 30-50 lines       | Breaking changes + migration link   |
| Incident summary      | 1 paragraph       | Impact + cause + resolution         |
| Incident full report  | 1-3 pages         | Progressive disclosure structure    |
