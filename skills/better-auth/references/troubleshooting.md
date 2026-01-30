---
title: Troubleshooting
description: D1 eventual consistency, CORS errors, OAuth redirect mismatch, admin 403, nanostore refresh, additionalFields bugs, Expo crash, and known issues
tags: [troubleshooting, d1, cors, oauth, admin, expo, known-issues]
---

# Troubleshooting

## D1 Eventual Consistency (Session reads return null)

Session reads immediately after write return stale data. Use Cloudflare KV for session storage:

```ts
session: {
  storage: {
    get: async (sid) => { const s = await env.SESSIONS_KV.get(sid); return s ? JSON.parse(s) : null; },
    set: async (sid, session, ttl) => { await env.SESSIONS_KV.put(sid, JSON.stringify(session), { expirationTtl: ttl }); },
    delete: async (sid) => { await env.SESSIONS_KV.delete(sid); },
  },
}
```

## CORS Errors for SPA Applications

Both CORS config and `trustedOrigins` must match frontend origin exactly (no trailing slash):

```ts
app.use(
  '/api/auth/*',
  cors({
    origin: 'http://localhost:5173',
    credentials: true,
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  }),
);

export const auth = betterAuth({
  trustedOrigins: ['http://localhost:5173'],
});
```

CORS middleware must be registered BEFORE auth routes.

## OAuth Redirect URI Mismatch

Callback URL must be exact character-for-character match: `{baseURL}/api/auth/callback/{provider}`.

## Admin Plugin 403 Despite Custom Middleware

Admin plugin has dual authorization: your middleware AND `user.role === 'admin'` in database. Both must pass.

```sql
UPDATE user SET role = 'admin' WHERE email = 'admin@example.com';
```

## Organization `updated_at` Must Be Nullable

better-auth inserts `null` for `updated_at` on creation. Remove `NOT NULL` constraint:

```ts
updatedAt: integer('updated_at', { mode: 'timestamp' }), // No .notNull()
```

## User Data Updates Not Reflecting in UI (TanStack Query)

better-auth uses nanostores, not TanStack Query. After updating user data:

```ts
authClient.$store.notify('$sessionSignal');
// Or use refetch:
const { data: session, refetch } = authClient.useSession();
await refetch();
```

## `additionalFields` string[] Returns Stringified JSON

When querying via Drizzle directly, `string[]` fields return `'["a","b"]'` (string) instead of arrays. Use `auth.api` (has transformer) or manually parse.

## Expo `fromJSONSchema` Crash (v1.4.16)

Importing `expoClient` crashes with `TypeError: Cannot read property 'fromJSONSchema' of undefined`. Tracked in [issue #7491](https://github.com/better-auth/better-auth/issues/7491).

## `freshAge` Based on Creation Time, Not Activity

`freshAge` checks time-since-creation, NOT recent activity. Set `updateAge <= freshAge` to avoid active sessions being rejected.

## OAuth Token Endpoints Return Wrapped JSON

OAuth 2.1/OIDC token endpoints return `{ response: { ...tokens } }` instead of spec-compliant top-level JSON. Tracked in [issue #7355](https://github.com/better-auth/better-auth/issues/7355).

## Schema Generation Fails for D1

Use Drizzle Kit instead of better-auth CLI for D1:

```bash
npx drizzle-kit generate
wrangler d1 migrations apply my-app-db --remote
```
