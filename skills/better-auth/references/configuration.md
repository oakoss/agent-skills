---
title: Configuration
description: User and account config, email verification flows, rate limiting with custom rules, database hooks, endpoint hooks, and security options
tags: [configuration, email, rate-limiting, hooks, security, user-config]
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

## Email Flows

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendResetPassword: async ({ user, url }) => {
      /* send email */
    },
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url }) => {
      /* send email */
    },
    sendOnSignUp: true,
    autoSignInAfterVerification: true,
    expiresIn: 3600,
  },
});
```

## Rate Limiting

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

Available hooks: `create`, `update` for `user`, `session`, `account`, `verification` tables.

## Endpoint Hooks

```ts
hooks: {
  before: [{ matcher: (ctx) => ctx.path === '/sign-in/email', handler: createAuthMiddleware(async (ctx) => { /* ... */ }) }],
  after: [{ matcher: (ctx) => true, handler: createAuthMiddleware(async (ctx) => { /* access ctx.context.returned */ }) }],
}
```

Hook context (`ctx.context`): `session`, `secret`, `authCookies`, `password.hash()`/`verify()`, `adapter`, `internalAdapter`, `generateId()`, `tables`, `baseURL`.

## Security Options

| Option                                   | Notes                            |
| ---------------------------------------- | -------------------------------- |
| `advanced.useSecureCookies`              | Force HTTPS cookies              |
| `advanced.disableCSRFCheck`              | Security risk                    |
| `advanced.crossSubDomainCookies.enabled` | Share cookies across subdomains  |
| `advanced.ipAddress.ipAddressHeaders`    | Custom IP headers for proxies    |
| `advanced.database.generateId`           | Custom ID generation or `"uuid"` |
