---
title: API and Code Documentation
description: API endpoint references, JSDoc/TSDoc patterns, code documentation philosophy, runbooks, and documentation testing
tags:
  [
    api-docs,
    jsdoc,
    tsdoc,
    runbook,
    endpoint-reference,
    doc-testing,
    link-checking,
    self-documenting,
  ]
---

# API and Code Documentation

## API Endpoint Reference

Every public API endpoint needs a consistent reference entry. Consumers should be able to integrate without reading source code.

### Endpoint Documentation Template

```markdown
### Create User

Creates a new user account and sends a verification email.

**Endpoint:** `POST /api/v1/users`

**Authentication:** Bearer token (admin role required)

**Request Headers:**

| Header          | Value              | Required |
| --------------- | ------------------ | -------- |
| `Authorization` | `Bearer <token>`   | Yes      |
| `Content-Type`  | `application/json` | Yes      |

**Request Body:**

| Field   | Type     | Required | Description                |
| ------- | -------- | -------- | -------------------------- |
| `email` | `string` | Yes      | Valid email address        |
| `name`  | `string` | Yes      | Display name (2-100 chars) |
| `role`  | `string` | No       | Default: `"member"`        |

**Request Example:**

` ` `bash
curl -X POST https://api.example.com/api/v1/users \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "name": "Jane Smith"}'
` ` `

**Response (201 Created):**

` ` `json
{
  "id": "usr_abc123",
  "email": "jane@example.com",
  "name": "Jane Smith",
  "role": "member",
  "createdAt": "2025-03-15T10:30:00Z"
}
` ` `

**Error Responses:**

| Status | Code               | Description                |
| ------ | ------------------ | -------------------------- |
| 400    | `validation_error` | Invalid or missing fields  |
| 401    | `unauthorized`     | Missing or invalid token   |
| 403    | `forbidden`        | Insufficient permissions   |
| 409    | `conflict`         | Email already registered   |
| 429    | `rate_limited`     | Too many requests (60/min) |
```

### Key Principles

- **Real examples** — use realistic data, not `foo`/`bar`
- **Every error code** — document all possible error responses with causes
- **Copy-paste ready** — curl examples should work with minimal edits
- **Versioned paths** — include the API version in the path
- **Rate limits** — document limits alongside the endpoints they apply to

## TypeDoc / JSDoc Patterns

### When to Document

| Document                         | Skip                                        |
| -------------------------------- | ------------------------------------------- |
| Public API functions             | Private/internal helpers                    |
| Non-obvious return values        | Functions where types tell the full story   |
| Side effects not in the type     | Obvious getters and setters                 |
| Complex parameters with defaults | Single-parameter functions with clear names |
| Thrown errors                    | Re-exported types from dependencies         |

### Good JSDoc Examples

```ts
/**
 * @returns Amount in cents, not dollars
 */
export function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

/**
 * Deletes the user and all associated data (posts, comments, sessions).
 * Triggers a `user.deleted` webhook after successful deletion.
 *
 * @throws {NotFoundError} If user does not exist
 * @throws {ForbiddenError} If caller lacks admin role
 */
export async function deleteUser(id: string): Promise<void> {
  // ...
}

/**
 * @param ttl - Cache duration in seconds
 * @default ttl 3600
 */
export function setCacheControl(ttl?: number): void {
  // ...
}
```

### JSDoc to Skip

```ts
// Types already communicate everything here
export function getUserById(id: string): Promise<User | null> {
  return db.user.findUnique({ where: { id } });
}

// Obvious getter
export function getFullName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}
```

### Component Prop Documentation

Document on the type, not the component function:

```tsx
type AlertProps = {
  /** @default "info" */
  variant?: 'info' | 'warning' | 'error' | 'success';
  /** Dismissible alerts show a close button */
  dismissible?: boolean;
  /** Called when the alert is dismissed; required if `dismissible` is true */
  onDismiss?: () => void;
  children: React.ReactNode;
};

function Alert({
  variant = 'info',
  dismissible,
  onDismiss,
  children,
}: AlertProps) {
  // ...
}
```

## Code Documentation Philosophy

### The Hierarchy

1. **Self-documenting code first** — rename variables, extract functions, simplify logic
2. **Types second** — let TypeScript signatures communicate contracts
3. **Tests third** — tests document behavior and edge cases
4. **Comments last** — only when the code genuinely cannot explain itself

### Comments That Earn Their Place

```ts
// Stripe's webhook retry window is 72 hours with exponential backoff
const WEBHOOK_RETENTION_HOURS = 80;

// Auth middleware must run before rate limiter reads the user tier
app.use(authMiddleware);
app.use(rateLimiter);

// Workaround for https://github.com/prisma/prisma/issues/12345
const result = await prisma.$queryRaw`...`;
```

### Comments to Remove

```ts
// Initialize the counter (the code already says this)
let counter = 0;

// Get user from database (the function name says this)
const user = await getUserById(id);

// Loop through items (every developer knows what for-of does)
for (const item of items) {
  /* ... */
}
```

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

## Documentation Testing

Untested docs rot. Automate freshness checks where possible.

### Link Checking

Validate internal and external links on every CI run:

```bash
# Using markdown-link-check
npx markdown-link-check docs/**/*.md --config .markdown-link-check.json
```

### Example Code Testing

Extract code examples from markdown and run them as tests:

```ts
// docs.test.ts — verify README quick start example compiles
import { createClient } from '../src';

test('quick start example works', () => {
  const client = createClient({ apiKey: 'test-key' });
  expect(client).toBeDefined();
});
```

### Freshness Tracking

| Strategy              | How                                                 |
| --------------------- | --------------------------------------------------- |
| Last-updated dates    | Frontmatter `updated:` field, checked in CI         |
| Doc ownership         | CODEOWNERS file maps doc paths to responsible teams |
| PR reminders          | Bot comments on PRs that change code but not docs   |
| Quarterly review      | Calendar reminder to audit docs for staleness       |
| Broken example alerts | CI runs extracted code examples against current API |
