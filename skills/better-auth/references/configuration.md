---
title: Configuration
description: User and account config, rate limiting with custom rules, database hooks, endpoint hooks, CSRF protection, trusted origins, cookie security, OAuth security, IP tracking, and production security checklist
tags:
  [
    configuration,
    rate-limiting,
    hooks,
    security,
    csrf,
    cookies,
    oauth,
    trusted-origins,
  ]
---

# Configuration

## User and Account Config

```ts
export const auth = betterAuth({
  user: {
    modelName: 'user',
    additionalFields: {
      /* custom fields */
    },
    changeEmail: { enabled: true },
    deleteUser: { enabled: true },
  },
  account: {
    accountLinking: { enabled: true },
  },
});
```

Required for registration: `email` and `name` fields.

## Rate Limiting

Enabled by default in production, disabled in development. Per-endpoint stricter defaults on `/sign-in`, `/sign-up`, `/change-password`, `/change-email`: 3 req/10s.

Storage options: `"memory"` | `"database"` | `"secondary-storage"`. Avoid memory on serverless — use secondary-storage.

```ts
export const auth = betterAuth({
  rateLimit: {
    window: 60,
    max: 100,
    customRules: {
      '/sign-in/email': { window: 10, max: 3 },
      '/two-factor/*': { window: 10, max: 3 },
      '/forget-password': { window: 60, max: 5 },
    },
    storage: 'secondary-storage',
  },
  secondaryStorage: {
    get: async (key) => env.KV.get(key),
    set: async (key, value, ttl) =>
      env.KV.put(key, value, { expirationTtl: ttl }),
    delete: async (key) => env.KV.delete(key),
  },
});
```

Server-side calls via `auth.api.*` bypass rate limiting.

## Database Hooks

```ts
export const auth = betterAuth({
  databaseHooks: {
    user: {
      create: {
        before: async (user, ctx) => {
          if (user.email?.endsWith('@blocked.com')) {
            throw new APIError('BAD_REQUEST', {
              message: 'Email domain not allowed',
            });
          }
          return { data: { ...user, role: 'member' } };
        },
        after: async (user, ctx) => {
          await sendWelcomeEmail(user.email);
        },
      },
    },
  },
});
```

Available hooks: `create`, `update` for `user`, `session`, `account`, `verification` tables. Return `false` from a `before` hook to prevent the operation.

### Security Auditing via Database Hooks

```ts
databaseHooks: {
  session: {
    create: {
      after: async ({ data, ctx }) => {
        /* log new session with IP, user agent */
      },
    },
    delete: {
      before: async ({ data }) => {
        /* log session revocation */
      },
    },
  },
  user: {
    update: {
      after: async ({ data, oldData }) => {
        /* log email/role changes */
      },
    },
    delete: {
      before: async ({ data }) => {
        /* block protected users: return false */
      },
    },
  },
}
```

## Endpoint Hooks

```ts
hooks: {
  before: [{ matcher: (ctx) => ctx.path === '/sign-in/email', handler: createAuthMiddleware(async (ctx) => { /* ... */ }) }],
  after: [{ matcher: (ctx) => true, handler: createAuthMiddleware(async (ctx) => { /* access ctx.context.returned */ }) }],
}
```

Hook context (`ctx.context`): `session`, `secret`, `authCookies`, `password.hash()`/`verify()`, `adapter`, `internalAdapter`, `generateId()`, `tables`, `baseURL`.

## Security Options

### CSRF Protection

Three layers enabled by default — do not disable:

1. Origin/Referer header validation against trusted origins (when cookies present)
2. Fetch Metadata headers (`Sec-Fetch-Site`, `Sec-Fetch-Mode`, `Sec-Fetch-Dest`)
3. First-login protection via Fetch Metadata even without cookies

### Trusted Origins

```ts
export const auth = betterAuth({
  trustedOrigins: ['https://app.example.com', 'https://admin.example.com'],
});
```

Via env: `BETTER_AUTH_TRUSTED_ORIGINS=https://app.example.com,https://admin.example.com`

Wildcard patterns: `"*.example.com"`, `"https://*.example.com"`, `"exp://192.168.*.*:*/*"`

Dynamic:

```ts
trustedOrigins: async (request) => {
  const tenant = getTenantFromRequest(request);
  return [`https://${tenant}.myapp.com`];
};
```

Validated parameters: `callbackURL`, `redirectTo`, `errorCallbackURL`, `newUserCallbackURL`, `origin`.

### Cookie Security

Defaults: `secure: true` on HTTPS/production, `sameSite: "lax"`, `httpOnly: true`, `path: "/"`, `__Secure-` prefix.

```ts
advanced: {
  useSecureCookies: true,
  cookiePrefix: 'myapp',
  defaultCookieAttributes: { sameSite: 'strict', path: '/auth' },
  cookies: {
    session_token: {
      name: 'auth-session',
      attributes: { sameSite: 'strict' },
    },
  },
  crossSubDomainCookies: {
    enabled: true,
    domain: '.example.com',
    additionalCookies: ['session_token', 'session_data'],
  },
}
```

### OAuth Security

- **PKCE**: Automatic, uses 128-char random `code_verifier` with S256 challenge
- **State parameter**: 32-char random, expires after 10 minutes, contains callback URLs and PKCE verifier (encrypted). Strategy: `"cookie"` (default) | `"database"`
- **Encrypt tokens**: `account: { encryptOAuthTokens: true }` (AES-256-GCM) — recommended if storing tokens for API access
- **Skip state cookie**: `account: { skipStateCookieCheck: true }` — only for mobile apps that cannot maintain cookies

### IP-Based Security

```ts
advanced: {
  ipAddress: {
    ipAddressHeaders: ['x-forwarded-for', 'x-real-ip'],
    disableIpTracking: false,
  },
}
```

### Account Enumeration Prevention

Built-in on password reset:

1. Consistent response regardless of whether email exists
2. Dummy token generation + DB lookup when user not found
3. Background email sending (no response timing leak)

Return generic errors like "Invalid credentials" rather than "User not found" / "Incorrect password".

### Secret Management

Better Auth looks for secrets in order: `options.secret` > `BETTER_AUTH_SECRET` env > `AUTH_SECRET` env. Rejects placeholder secrets in production. Warns if < 32 chars or entropy < 120 bits.

### Production Security Checklist

- Strong unique secret (32+ chars, high entropy)
- `baseURL` uses HTTPS
- All valid origins in `trustedOrigins` (frontend, mobile)
- Rate limiting enabled with appropriate limits
- CSRF protection NOT disabled
- Secure cookies (automatic with HTTPS)
- `encryptOAuthTokens: true` if storing OAuth tokens
- Background tasks configured for serverless
- Audit logging via `databaseHooks` or `hooks`
- IP tracking headers configured if behind a proxy
