---
title: Session Management
description: Session storage priority, cookie cache strategies (compact, JWT, JWE), stateless sessions, freshAge constraints, and session configuration
tags: [sessions, cookies, jwt, jwe, stateless, freshAge, cookie-cache]
---

# Session Management

## Storage Priority

1. If `secondaryStorage` defined -> sessions go there (not DB)
2. Set `session.storeSessionInDatabase: true` to also persist to DB
3. No database + `cookieCache` -> fully stateless mode

## Session Configuration

```ts
export const auth = betterAuth({
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Refresh every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 300, // 5 minutes
      encoding: 'compact', // or "jwt" or "jwe"
    },
    freshAge: 60 * 60 * 24, // 1 day - for sensitive operations
  },
});
```

**Key constraint:** `updateAge` must be <= `freshAge`, otherwise active sessions become "not fresh" before `updatedAt` is bumped.

## Stateless Sessions (v1.4.0+)

```ts
export const auth = betterAuth({
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7,
      encoding: 'jwt',
    },
  },
});
```

Limitations:

- Cannot revoke sessions (user must wait for expiry)
- Cookie size limit ~4KB
- Server must have consistent `BETTER_AUTH_SECRET` across all instances
